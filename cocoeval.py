import json
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

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
