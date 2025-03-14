import pandas as pd
import qai_hub as hub
import numpy as np
import csv
import tensorflow as tf
import torch.nn.functional
from torchvision.ops import box_convert
import json
from scipy.special import softmax
import h5py
import os

confidence_threshold = 0.0


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

                    '''x_scale = image_width
                    y_scale = image_height

                    pred_box[0] = round(((pred_box[0] - (pred_box[2]/2)) * x_scale), 2)  # x1 * image_width
                    pred_box[1] = round(((pred_box[1] - (pred_box[3]/2)) * y_scale), 2)  # y1 * image_height
                    pred_box[2] = round(pred_box[2] * x_scale, 2)  # x2 * image_width
                    pred_box[3] = round(pred_box[3] * y_scale, 2)  # y2 * image_height'''

                    # Store the result in list to store in json later
                    '''predictions.append({
                    "image_id": image_name,
                    "category_id": category_mapping.get(pred_class, 0),
                    "bbox": pred_box,
                    "score": round(pred_score, 3)
                    })'''

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
        file_predictions = process_h5(h5_file_path, confidence_threshold, category_mapping, file_count)
        all_results.extend(file_predictions)
        file_count += 1
    except Exception as e:
        print(f"Error reading {h5_file_path}: {e}")

# Write results to a JSON file (will overwrite if already exists
with open('results/results.json', 'w') as f:
    json.dump(all_results, f)

print("Results saved to results.json")
