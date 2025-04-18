import qai_hub as hub
import pandas as pd
import numpy as np
import torch.nn.functional
from pydash import to_lower
from torchvision.ops import box_convert, nms
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

'''
# detr for fast models/devices
detr = ['dz7z48rr9', 'dz2r53807', 'd82nd3e07', 'do7ml3v39', 'dq9kr31o7',
        'dk7gkm162', 'd67jw4gz2', 'dn7xze8r9', 'dp70n6q09', 'dv74k3ny2']
'''
# detr for models/devices
detr = ['dx9e8x8o9','d09y1e119','dv91040n2','dw2646xz9','dz7z4eg59',
        'dp70n1wd9','dr9wmorw2','dk7gkq6y2','d67ox1n67','d67jwnxp2',
        'dn7xzvge9','d09y1el19','dp70n1dd9','do7mlm5m9','dv9104xn2',
        'dw2646rz9','dw9v83jm7','dx9e8xjo9','dn7xzvde9','dr2qqwjy2']

# yolo (1, 640, 640, 3) float 32
yolo = ['dv9516pz2', 'do7ml3g39', 'dp7lg36j2', 'd67ox3lg7', 'dn7xzeor9',
        'dr2qq30v2', 'do7ml34l9', 'dr9wm3lo2', 'dp7lg3e12', 'd67jw4mm2',
        'dj7d0neq9', 'dq9kr3md7', 'dz2r534g7', 'dw264e1g9', 'dj7d0nvq9',
        'dv95164e2', 'dq9kr3xd7', 'dw264ewg9', 'd67jw4lm2', 'dv9516je2']

# yolo (1, 640, 640, 3) uint8
yolo_q = ['dp70nxz09','d678rmgp2','do7mlrd39','dq9kr4mo7','dr9wmzem2',
          'dk7gk8z62','d67jw1dz2','dd9ppxdd9','do7mlrq39','dr9wmzgm2',
          'dz2r5qp07','dp7lgwpj2','d693m5y37','dj7d0y3p9','d82ndg6o7',
          'dv74kylz2','dz7z41jy9','dv910p3x2','dw26405g9','dx9e8nlv9']

'''-------------------------------------'''
# put your models to run in here
models = [("M01", "mmrwd45wn"),
          ("M02", "mqk1l3ewm"),
          #("M03", ""),
          ("M04", "mng43w86n"),
          #("M05", ""),
          ("M06", "mq8y6ejgm"),
          #("M07", ""),
          ("M08", "mm5z6z49m"),
          ("M09", "mn706093q"),
          ("M10", "mq2eje9lq"),
          ("M11", "mm5z6zp6m"),
          ("M12", "mq2ejer0q"),
          ("M15", "mmrwdy4xn"),
          ("M16", "mng4303rn"),
          ("M17", "mmd4d1y0m")
          ]
Device = 'D13'
Runtime = 'tf'
device_id = "QCS8550 (Proxy)"
'''-------------------------------------'''

# static variable
confidence_threshold = 0.0
iou_threshold=0.6
convert_flag = True # if output is coco 80 true, if coco 91 false

def process_yolo(filename, confidence_threshold, category_mapping, file_no, idx_convert, batch_size):
    predictions = []

    with h5py.File(filename, "r") as file:
        # Get the logits and bboxes from the h5 file
        img_count = len(file['data']['0'])
        image_id = 0 + (batch_size * file_no)  # get index shift based on batch no for accessing image detail csv
        for i in range(img_count):
            # get original image id and dimensions from csv
            image_name = image_details[image_id]['Image Name']
            image_width = image_details[image_id]['Original Width']
            image_height = image_details[image_id]['Original Height']

            # extract data from h5 file
            batch = 'batch_' + str(i)
            bboxes = torch.tensor(np.array((file['data']['0'][batch])))
            scores = torch.tensor(np.array((file['data']['1'][batch])))
            classes = torch.tensor(np.array((file['data']['2'][batch])))

            # fix shape for input into nms
            bboxes = bboxes.squeeze(0)
            scores = scores.squeeze(0)
            classes = classes.squeeze(0)

            # Apply nms
            indices = nms(bboxes, scores, iou_threshold)

            # Use the indices to extract the remaining boxes, scores, and classes, re-add batch dim
            bboxes = bboxes[indices]
            bboxes = bboxes.unsqueeze(0)
            scores = scores[indices]
            scores = scores.unsqueeze(0)
            classes = classes[indices]
            classes = classes.unsqueeze(0)

            # check each prediction
            for j in range(len(scores[0])):
                score = scores[0][j]

                # if prediction meets confidence threshold get data and save to put in results json
                if score.max() > confidence_threshold:
                    # get predicted class
                    pred_class=classes[0][j].item()
                    if convert_flag:
                        pred_class = idx_convert[pred_class]['coco_class']
                    #print("Class ", pred_class)
                    pred_score = score.item()  # Max confidence score
                    #print("Score ", pred_score)
                    pred_box = bboxes[0][j].tolist()  # The bounding box

                    # Convert box from xyxy format (yolo) to xywh (coco)
                    pred_box = box_convert(torch.tensor(pred_box), 'xyxy', 'xywh').tolist()

                    # After converting to xywh, scale to original dimensions
                    xscale=image_width/640
                    yscale=image_height/640
                    pred_box[0] = round(pred_box[0] * xscale, 2)  # xmin * xscale
                    pred_box[1] = round(pred_box[1] * yscale, 2)  # ymin * yscale
                    pred_box[2] = round(pred_box[2] * xscale, 2)  # w * xscale
                    pred_box[3] = round(pred_box[3] * yscale, 2)  # h * yscale

                    # Store the result in list to store in json later
                    if category_mapping.get(pred_class, 0) != 0:
                        predictions.append({
                            "image_id": image_name,
                            "category_id": category_mapping.get(pred_class, 0),
                            "bbox": pred_box,
                            "score": round(pred_score, 3)
                        })
            image_id += 1
    return predictions

def process_detr(filename, confidence_threshold, category_mapping, file_no, batch_size):
    predictions = []

    with h5py.File(filename, "r") as file:
        # Get the logits and bboxes from the h5 file
        img_count = len(file['data']['0'])
        image_id = 0 + (batch_size * file_no)      # get index shift based on batch no for accessing image detail csv
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

def process_detr_pp(filename, confidence_threshold, category_mapping, file_no, batch_size):
    predictions = []

    with h5py.File(filename, "r") as file:
        # Get the logits and bboxes from the h5 file
        img_count = len(file['data']['0'])
        image_id = 0 + (batch_size * file_no)      # get index shift based on batch no for accessing image detail csv
        for i in range(img_count):
            # get original image id and dimensions from csv
            image_name = image_details[image_id]['Image Name']
            image_width = image_details[image_id]['Original Width']
            image_height = image_details[image_id]['Original Height']

            # extract data from h5 file
            batch = 'batch_' + str(i)

            bboxes = torch.tensor(np.array((file['data']['0'][batch])))
            scores = torch.tensor(np.array((file['data']['1'][batch])))
            classes = torch.tensor(np.array((file['data']['2'][batch])))


            # check each prediction
            for j in range(len(scores[0])):
                score = scores[0][j]

                # if prediction meets confidence threshold get data and save to put in results json
                if score.max() > confidence_threshold:
                    pred_class=classes[0][j].item()
                    pred_score = score.item()
                    pred_box = bboxes[0][j].tolist()  # The bounding box

                    # Convert box from cxcywh format (detr) to xywh (coco)
                    pred_box = box_convert(torch.tensor(pred_box), 'xyxy', 'xywh').tolist()

                    xscale = image_width / 480
                    yscale = image_height / 480
                    # After converting to xywh, scale to original dimensions
                    pred_box[0] = round(pred_box[0] * xscale, 2)  # x1 * image_width
                    pred_box[1] = round(pred_box[1] * yscale, 2)  # y1 * image_height
                    pred_box[2] = round(pred_box[2] * xscale, 2)  # x2 * image_width
                    pred_box[3] = round(pred_box[3] * yscale, 2)  # y2 * image_height

                    # Store the result in list to store in json later
                    predictions.append({
                    "image_id": image_name,
                    "category_id": category_mapping.get(pred_class, 0),
                    "bbox": pred_box,
                    "score": round(pred_score, 3)
                    })
            image_id += 1
    return predictions

def sort_files():
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

def move_completed(data, result_name):
    # make new directory in completed
    os.makedirs(os.getcwd() + "/completed" + "/" + result_name + "/")  # make output directory

    # create results csv
    csv_filename = os.getcwd() + "/completed" + "/" + result_name + "/" + result_name + '-coco_results.csv'
    header = ['Metric', 'Value']
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

    # move files into a nice new folder in completed
    folder_path = 'outputs'
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # Get the creation time for each file and sort by it
    files = [(f, os.path.getctime(os.path.join(folder_path, f))) for f in files]
    files.sort(key=lambda x: x[1])

    for index, (file_name, _) in enumerate(files, start=1):
        file_extension = os.path.splitext(file_name)[1]  # Get the file extension
        # Construct the full file path
        old_file_path = os.path.join(folder_path, file_name)
        new_file_path = os.path.join(os.getcwd() + "/completed" + "/" + result_name + "/", file_name)

        # Rename the file
        os.rename(old_file_path, new_file_path)

    os.rename(os.getcwd() + '/results/' + result_name + '-results.json',
              os.getcwd() + "/completed" + "/" + result_name + "/" + result_name + '-results.json')
    print(f"COCO evaluation results saved to " + csv_filename)

def get_model_num(modelID):
    return int(modelID[1:])

def get_dataset(modelID):
    number = get_model_num(modelID)

    if 1 <= number <= 5:
        return detr
    elif 6 <= number <= 13:
        return yolo
    elif 14 <= number <= 17:
        return yolo_q

def get_id(h5name):
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

    return d_id, m_id, r_id

def run_benchmark(model_id, device_id):
    model = hub.get_model(model_id)
    device = hub.Device(device_id)

    job_list = []

    dataset = get_dataset(Model)

    for i in dataset:
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

    sort_files()

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

    d_id, m_id, r_id = get_id(h5name)

    # read and process all h5 files
    all_results = []
    file_count = 0
    for h5_file in h5_files:
        h5_file_path = os.path.join(directory_path, h5_file)
        try:
            # Read data from each h5 file and get results

            with h5py.File(h5_file_path, "r") as file:
                batches = len(file['data']['0'])
                #print('Batch size:', batches)
                if 'data' in file and '2' in file['data']:
                    detr_pp = True
                else:
                    detr_pp = False
            if get_model_num(Model) > 5:
                print("reading file: " + h5_file + " Yolo")
                file_predictions = process_yolo(h5_file_path, confidence_threshold, category_mapping, file_count,
                                            index_convert, batches)
            else:
                if detr_pp:
                    print("reading file: " + h5_file + " DETR_PP")
                    file_predictions = process_detr_pp(h5_file_path, confidence_threshold, category_mapping, file_count, batches)
                else:
                    print("reading file: " + h5_file + " DETR")
                    file_predictions = process_detr(h5_file_path, confidence_threshold, category_mapping, file_count, batches)
            all_results.extend(file_predictions)
            file_count += 1
        except Exception as e:
            print(f"Error reading {h5_file_path}: {e}")

    # Write results to a JSON file (will overwrite if already exists
    result_json = 'results/' + result_name + '-results.json'
    with open(result_json, 'w') as f:
        json.dump(all_results, f)

    print("Results saved to " + result_json)

    gt_file = 'results/instances_val2017.json'  # Ground truth annotations
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

    exec_details = results['execution_detail']
    exec_summary = results['execution_summary']

    profile_data: dict[str, Any] = profile_job.download_profile()  # type: ignore
    print_profile_metrics_from_job(profile_job, profile_data)

    inference_time = exec_summary["estimated_inference_time"] / 1000
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
    csv_data = [
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

    move_completed(csv_data, result_name)

# read the image details csv to get original image id and dimensions
df = pd.read_csv('image_details.csv')
image_details = df.to_dict(orient='index')
df = pd.read_csv('old2newcoco.csv')
index_convert = df.to_dict(orient='index')
df = pd.read_csv('Device.csv')
device_list = df.to_dict(orient='index')
df = pd.read_csv('Model.csv')
model_list = df.to_dict(orient='index')

for model in models:
    if model[1] != "":
        Model = model[0]
        run_benchmark(model[1], device_id)
