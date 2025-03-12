import numpy as np
from PIL import Image
import qai_hub as hub

# gets last 10 datasets and prints ids/summaries
#dataset = hub.get_datasets(limit=10)
#print("Dataset information:", dataset)

# detr coco dataset (1, 480,480, 3) float 32
coco = ['d67ooy5n7', 'd67jod6n9', 'd67801862', 'd693pyql7', 'dr2qzxjl2',
        'dq9koxj57','d693py1l7', 'dn7xx1v57', 'd67801op2', 'dp7lop8j7']

# yolo (1, 640, 640, 3) float 32
coco2 = ['dd9po5ww2', 'do7mox1d9', 'dw9vekn07', 'dv955ngg9', 'do7morzd9',
        'dw26y0ke9','dd9poxgw2', 'dd9poxnn2', 'dp703xql7', 'd67jo1gn9']

model = hub.get_model("mqpdrkpoq")
device = hub.Device("Samsung Galaxy S24 Ultra")

for i in coco2:
    dataset = hub.get_dataset(i)
    # print("Dataset information:", dataset)


    inference_job = hub.submit_inference_job(
        model=model,
        device=device,
        inputs=dataset,
    )