#import qai_hub as hub
import numpy as np
import csv
#import tensorflow as tf
import torch.nn.functional
from torchvision.ops import box_convert
import json
from scipy.special import softmax
import h5py

confidence_threshold = 0.5

filename = "DETR results creator/archives/dataset-dn7xnjke9.h5"

# Read the class labels for coco
with open("coco-labels-2014_2017.txt", "r") as f:
    categories = [s.strip() for s in f.readlines()]
category_mapping = {i: i for i in range(91)}

out_list = []
bbox_list = []
score_list = []
predictions = []

imageInfoList=[]
#read CSV into list
with open('image_details.csv', newline='') as cocoLabel:
    cocoReader=csv.reader(cocoLabel)
    for row in cocoReader:
       # imageInfoList.append( tuple(next(cocoReader)) )
        print(cocoReader)

with h5py.File(filename, "r") as file:
    # get the logits and bboxes from the h5 file
    img_count = len(file['data']['0'])
    image_id = 0
    for i in range(0, img_count):
        batch = 'batch_' + str(i)
        out = torch.tensor(np.array((file['data']['0'][batch])))
        #out_list.append(out)

        bboxes = torch.tensor(np.array((file['data']['1'][batch])))
        #bboxes.append(bbox_list)

        scores = torch.tensor(softmax(out.numpy(), -1)) # softmax
        #score_list.append(scores)

        for j in range(len(scores[0])):
            score = scores[0][j]

            if score.max() > confidence_threshold:
                pred_class = np.argsort(score, axis=0)[-1:].item()  # Get class with highest score
                #print("Class ", pred_class)
                pred_score = score.max().item()  # Max confidence score
                #print("Score ", pred_score)
                pred_box = bboxes[0][j].tolist()  # The bounding box

                # Convert box from [0, 1] range (normalized) to image pixel coordinates
                pred_box = box_convert(torch.tensor(pred_box), 'xywh', 'xyxy').tolist()
                # Rescale here

                # Store the result
                predictions.append({
                    "image_id": image_id,#Update
                    "category_id": category_mapping.get(pred_class, 0),  # Default to 0 if class not found
                    "bbox": pred_box,
                    "score": pred_score
                })





# Save the predictions as a JSON file
results = predictions

# Write results to a JSON file
with open('results.json', 'w') as f:
    json.dump(results, f)

print("Results saved to results.json")