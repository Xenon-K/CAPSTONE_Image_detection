import pandas as pd
#import qai_hub as hub
import numpy as np
#import csv
#import tensorflow as tf
import torch.nn.functional
from torchvision.ops import box_convert
from torchvision.ops import nms
import json
#from scipy.special import softmax
import h5py
import os

confidence_threshold = 0.3
iou_threshold=0.45
batch_size = 250
convert_flag = True # if output is coco 80 true, if coco 91 false

def process_h5(filename, confidence_threshold, category_mapping, file_no, idx_convert):
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


# read the image details csv to get original image id and dimensions
df = pd.read_csv('image_details.csv')
image_details = df.to_dict(orient='index')
df2 = pd.read_csv('old2newcoco.csv')
index_convert = df2.to_dict(orient='index')

# Read the class labels for coco
with open("coco-labels-2014_2017.txt", "r") as f:
    categories = [s.strip() for s in f.readlines()]
category_mapping = {i: i for i in range(91)}

# get all h5 files in directory
directory_path = 'outputs'
h5_files = [f for f in os.listdir(directory_path) if f.endswith('.h5')]
h5_files.sort()

# read and process all h5 files
all_results = []
file_count = 0
for h5_file in h5_files:
    h5_file_path = os.path.join(directory_path, h5_file)
    try:
        # Read data from each h5 file and get results
        print("reading file: " + h5_file)
        file_predictions = process_h5(h5_file_path, confidence_threshold, category_mapping, file_count, index_convert)
        all_results.extend(file_predictions)
        file_count += 1
    except Exception as e:
        print(f"Error reading {h5_file_path}: {e}")

# Write results to a JSON file (will overwrite if already exists
with open('results/results.json', 'w') as f:
    json.dump(all_results, f)

print("Results saved to results.json")
