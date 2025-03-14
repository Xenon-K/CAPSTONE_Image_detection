import json
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
import csv

gt_file = 'results/instances_val2017.json'   # Ground truth annotations
results_file = 'results/results.json'  # Predicted results

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

# get data ready for csv
header = ['Metric', 'Value']
data = [
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
    ('AR large', round(metrics[11], 3))
]

# create results csv
csv_filename = 'results/coco_results.csv'
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data)

print(f"COCO evaluation results saved to " + csv_filename)