import pandas as pd
#import qai_hub as hub
import numpy as np
#import csv
#import tensorflow as tf
import torch.nn.functional
from torchvision.ops import box_convert
import json
from scipy.special import softmax
import h5py
import os

def process_h5(filename, confidence_threshold, category_mapping, file_no):
    predictions = []

    with h5py.File(filename, "r") as file:
        # Get the logits and bboxes from the h5 file
        img_count = len(file['data']['0'])
        image_id = 0 + (500 * file_no)
        for i in range(img_count):
            image_name = image_details[image_id]['Image Name']
            image_width = image_details[image_id]['Original Width']
            image_height = image_details[image_id]['Original Height']

            batch = 'batch_' + str(i)
            out = torch.tensor(np.array((file['data']['0'][batch])))
            # out_list.append(out)

            bboxes = torch.tensor(np.array((file['data']['1'][batch])))
            # bboxes.append(bbox_list)

            scores = torch.tensor(softmax(out.numpy(), -1))  # softmax
            # score_list.append(scores)

            for j in range(len(scores[0])):
                score = scores[0][j]

                if score.max() > confidence_threshold:
                    pred_class = np.argsort(score, axis=0)[-1:].item()  # Get class with highest score
                    #print("Class ", pred_class)
                    pred_score = score.max().item()  # Max confidence score
                    #print("Score ", pred_score)
                    pred_box = bboxes[0][j].tolist()  # The bounding box

                    # Convert box from [0, 1] range (normalized) to image pixel coordinates
                    pred_box = box_convert(torch.tensor(pred_box), 'cxcywh', 'xyxy').tolist()

                    # After converting to [xyxy], scale to pixel values
                    pred_box[0] = round(pred_box[0] * image_width, 2)  # x1 * image_width
                    pred_box[1] = round(pred_box[1] * image_height, 2)  # y1 * image_height
                    pred_box[2] = round(pred_box[2] * image_width, 2)  # x2 * image_width
                    pred_box[3] = round(pred_box[3] * image_height, 2)  # y2 * image_height

                    # Store the result
                    if category_mapping.get(pred_class, 0) != 0:
                        predictions.append({
                        	"image_id": image_name,
                        	"category_id": category_mapping.get(pred_class, 0),  # Default to 0 if class not found
                        	"bbox": pred_box,
                        	"score": round(pred_score, 3)
                    	})
            image_id += 1
    return predictions

confidence_threshold = 0.9
#image_details = read_image_details('image_details.csv')
df = pd.read_csv('image_details.csv')
image_details = df.to_dict(orient='index')
filename = "artifacts/dataset-dw9ve4oq7.h5"

# Read the class labels for coco
with open("coco-labels-2014_2017.txt", "r") as f:
    categories = [s.strip() for s in f.readlines()]
category_mapping = {i: i for i in range(91)}

directory_path = 'outputs'
h5_files = [f for f in os.listdir(directory_path) if f.endswith('.h5')]
h5_files.sort()

all_results = []
file_count = 0
for h5_file in h5_files:
    h5_file_path = os.path.join(directory_path, h5_file)
    try:
        # Read data from each HDF5 file using your processing function
        file_predictions = process_h5(h5_file_path, confidence_threshold, category_mapping, file_count)
        all_results.extend(file_predictions)
        file_count += 1
    except Exception as e:
        print(f"Error reading {h5_file_path}: {e}")

# Save the predictions as a JSON file

# Write results to a JSON file
with open('results.json', 'w') as f:
    json.dump(all_results, f)

print("Results saved to results.json")