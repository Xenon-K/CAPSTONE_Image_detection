import qai_hub as hub
import pandas as pd
import numpy as np
import torch.nn.functional
from pydash import to_lower
from torchvision.ops import box_convert
from torchvision.ops import nms
import json
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
import csv
import h5py
import os
import re
from typing import Any
from qai_hub_models.configs.perf_yaml import bytes_to_mb
from collections import Counter
from qai_hub_models.utils.printing import print_profile_metrics_from_job
from scipy.special import softmax

detr = ['dz7z48rr9', 'dz2r53807', 'd82nd3e07', 'do7ml3v39', 'dq9kr31o7',
        'dk7gkm162', 'd67jw4gz2', 'dn7xze8r9', 'dp70n6q09', 'dv74k3ny2']

confidence_threshold = 0.0
Device = 'D28'
Model = 'M04'
Runtime = 'tf'
model_id = "mn0lwjk3n"
device_id = "Google Pixel 5 (Family)"

model = hub.get_model(model_id)
device = hub.Device(device_id)

job_list = []

for i in detr:
    dataset = hub.get_dataset(i)
    print("Dataset information:", dataset)


    inference_job = hub.submit_inference_job(
        model=model,
        device=device,
        inputs=dataset,
    )

    job_list.append(inference_job)

# Profile the previously compiled model
profile_job = hub.submit_profile_job(
    model=model,
    device=device,
)


for jobs in job_list:
    jobs.download_results('toSort')

results = profile_job.download_profile()

folder_path = 'toSort'

files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Get the creation time for each file and sort by it
files = [(f, os.path.getctime(os.path.join(folder_path, f))) for f in files]
files.sort(key=lambda x: x[1])

for index, (file_name, _) in enumerate(files, start=1):
    file_extension = os.path.splitext(file_name)[1]  # Get the file extension
    if index < 10:
        new_name = f"{Device}-{Model}-{Runtime}-0{index}{file_extension}"
    else:
        new_name = f"{Device}-{Model}-{Runtime}-{index}{file_extension}"
    # Construct the full file path
    old_file_path = os.path.join(folder_path, file_name)
    new_file_path = os.path.join('outputs', new_name)

    # Rename the file
    os.rename(old_file_path, new_file_path)


def process_h5(filename, confidence_threshold, category_mapping, file_no):
    predictions = []

    with h5py.File(filename, "r") as file:
        # Get the logits and bboxes from the h5 file
        img_count = len(file['data']['0'])
        image_id = 0 + (500 * file_no)      # get index shift based on batch no for accessing image detail csv
        for i in range(img_count):
            # get original image id and dimensions from csv
            image_name = image_details[image_id]['Image Name']
            image_width = image_details[image_id]['Original Width']
            image_height = image_details[image_id]['Original Height']

            # extract data from h5 file
            batch = 'batch_' + str(i)
            out = torch.tensor(np.array((file['data']['0'][batch])))
            bboxes = torch.tensor(np.array((file['data']['1'][batch])))
            scores = torch.tensor(softmax(out.numpy(), -1))  # softmax the logits

            # check each prediction
            for j in range(len(scores[0])):
                score = scores[0][j]

                # if prediction meets confidence threshold get data and save to put in results json
                if score.max() > confidence_threshold:
                    pred_class = np.argsort(score, axis=0)[-1:].item()  # Get class with highest score
                    pred_score = score.max().item()
                    if category_mapping.get(pred_class, 0) == 0:
                        pred_class = np.argsort(score, axis=0)[-2].item()
                        sorted_indices = np.argsort(score, axis=0)
                        # Get the second highest index (second to last in sorted order)
                        second_pred_class = sorted_indices[-2].item()
                        # Get the second highest score
                        pred_score = score[second_pred_class].item()
                    #print("Class ", pred_class)
                      # Max confidence score
                    #print("Score ", pred_score)
                    pred_box = bboxes[0][j].tolist()  # The bounding box

                    # Convert box from cxcywh format (detr) to xywh (coco)
                    pred_box = box_convert(torch.tensor(pred_box), 'cxcywh', 'xywh').tolist()

                    # After converting to xywh, scale to original dimensions
                    pred_box[0] = round(pred_box[0] * image_width, 2)  # x1 * image_width
                    pred_box[1] = round(pred_box[1] * image_height, 2)  # y1 * image_height
                    pred_box[2] = round(pred_box[2] * image_width, 2)  # x2 * image_width
                    pred_box[3] = round(pred_box[3] * image_height, 2)  # y2 * image_height


                    # Store the result in list to store in json later
                    predictions.append({
                    "image_id": image_name,
                    "category_id": category_mapping.get(pred_class, 0),
                    "bbox": pred_box,
                    "score": round(pred_score, 3)
                    })
            image_id += 1
    return predictions


# read the image details csv to get original image id and dimensions
df = pd.read_csv('image_details.csv')
image_details = df.to_dict(orient='index')
df = pd.read_csv('old2newcoco.csv')
index_convert = df.to_dict(orient='index')
df = pd.read_csv('Device.csv')
device_list = df.to_dict(orient='index')
df = pd.read_csv('Model.csv')
model_list = df.to_dict(orient='index')

# Read the class labels for coco
with open("coco-labels-2014_2017.txt", "r") as f:
    categories = [s.strip() for s in f.readlines()]
category_mapping = {i: i for i in range(91)}

# get all h5 files in directory
directory_path = 'outputs'
h5_files = [f for f in os.listdir(directory_path) if f.endswith('.h5')]
h5_files.sort()

h5name = str(h5_files[0])
result_name = h5name[:10]

pattern = r"D(\d+)-M(\d+)-(\w+)-\d+.h5"

# Search for the pattern in the string
match = re.search(pattern, h5name)

if match:
    # Extracting the values
    d_id = int(match.group(1))  # 01 as integer
    m_id = int(match.group(2))  # 03 as integer
    r_id = match.group(3)  # 'tf' as string

    # index shift
    d_id -= 1
    m_id -= 1

    r_id = to_lower(r_id)
    if r_id == 'tf':
        r_id = 'tflite'
    elif r_id == 'on':
        r_id = 'onnx'
    elif r_id == 'qn':
        r_id = 'QNN'
    else:
        print("Invalid runtime code in input filename")
        exit(-2)
else:
    print("Output file name error.")
    exit(-1)

# read and process all h5 files
all_results = []
file_count = 0
for h5_file in h5_files:
    h5_file_path = os.path.join(directory_path, h5_file)
    try:
        # Read data from each h5 file and get results
        print("reading file: " + h5_file)
        file_predictions = process_h5(h5_file_path, confidence_threshold, category_mapping, file_count)
        all_results.extend(file_predictions)
        file_count += 1
    except Exception as e:
        print(f"Error reading {h5_file_path}: {e}")

# Write results to a JSON file (will overwrite if already exists
result_json = 'results/'+result_name+'-results.json'
with open(result_json, 'w') as f:
    json.dump(all_results, f)

print("Results saved to " + result_json)

gt_file = 'results/instances_val2017.json'   # Ground truth annotations
results_file = result_json  # Predicted results

# Load COCO ground truth data
coco_gt = COCO(gt_file)

# Load COCO results (predictions)
coco_dt = coco_gt.loadRes(results_file)

# Initialize the COCOeval object for bbox
coco_eval = COCOeval(coco_gt, coco_dt, 'bbox')

# Run the evaluation
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

# get metrics in a variable
metrics = coco_eval.stats


#profile_job.download_results('artifacts')

exec_details = results['execution_detail']
exec_summary = results['execution_summary']

profile_data: dict[str, Any] = profile_job.download_profile()  # type: ignore
print_profile_metrics_from_job(profile_job, profile_data)

inference_time = exec_summary["estimated_inference_time"]/1000
peak_memory_bytes = exec_summary["inference_memory_peak_range"]
mem_min = bytes_to_mb(peak_memory_bytes[0])
mem_max = bytes_to_mb(peak_memory_bytes[1])

compute_unit_counts = Counter(
        [op.get("compute_unit", "UNK") for op in profile_data["execution_detail"]]
    )
gpu_value = compute_unit_counts.get("GPU", 0)
cpu_value = compute_unit_counts.get("CPU", 0)
npu_value = compute_unit_counts.get("NPU", 0)

# get data ready for csv
header = ['Metric', 'Value']
data = [
    ('Device', device_list[d_id]['Name']),
    ('Chipset', device_list[d_id]['Chipset']),
    ('OS', device_list[d_id]['OS']),
    ('Model', model_list[m_id]['Name']),
    ('Runtime', r_id),
    ('AP', round(metrics[0], 3)),
    ('AP@.5', round(metrics[1], 3)),
    ('AP@.75', round(metrics[2], 3)),
    ('AP small', round(metrics[3], 3)),
    ('AP medium', round(metrics[4], 3)),
    ('AP large', round(metrics[5], 3)),
    ('AR', round(metrics[6], 3)),
    ('AR@.5', round(metrics[7], 3)),
    ('AR@.75', round(metrics[8], 3)),
    ('AR small', round(metrics[9], 3)),
    ('AR medium', round(metrics[10], 3)),
    ('AR large', round(metrics[11], 3)),
    ('Inference Time', inference_time),
    ('Min Memory', mem_min),
    ('Peak Memory', mem_max),
    ('Compute Units NPU', npu_value),
    ('Compute Units GPU', gpu_value),
    ('Compute Units CPU', cpu_value)
]

#make new directory in completed
os.makedirs(os.getcwd()+"/completed"+"/"+result_name+"/")#make output directory

# create results csv
csv_filename = os.getcwd()+"/completed"+"/"+result_name+"/"+result_name+'-coco_results.csv'
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)

    #move files into a nice new folder in completed
folder_path = 'outputs'
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
# Get the creation time for each file and sort by it
files = [(f, os.path.getctime(os.path.join(folder_path, f))) for f in files]
files.sort(key=lambda x: x[1])

for index, (file_name, _) in enumerate(files, start=1):
    file_extension = os.path.splitext(file_name)[1]  # Get the file extension
    # Construct the full file path
    old_file_path = os.path.join(folder_path, file_name)
    new_file_path = os.path.join(os.getcwd()+"/completed"+"/"+result_name+"/", file_name)

    # Rename the file
    os.rename(old_file_path, new_file_path)

os.rename(os.getcwd()+'/results/'+result_name+'-results.json', os.getcwd()+"/completed"+"/"+result_name+"/"+result_name+'-results.json')
print(f"COCO evaluation results saved to " + csv_filename)
