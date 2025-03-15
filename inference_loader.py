import numpy as np
from PIL import Image
import qai_hub as hub

# gets last 10 datasets and prints ids/summaries
#dataset = hub.get_datasets(limit=30)
#print("Dataset information:", dataset)

# detr coco dataset (1, 480,480, 3) float 32
coco = ['dp7035le7', 'd67oog6q7', 'dk7g4en07', 'dv91dn189', 'dv955r3m9',
        'dp7lomyw7','dq9ko0w57', 'dj7dmlk87', 'd693pkwl7', 'dr2qzo362']

# yolo (1, 640, 640, 3) float 32
coco2 = ['dz2roj5g2', 'dn7xxkw67', 'd693pkq07', 'dq9ko0pd7', 'dj7dmljq7',
        'dk7g4eje7','dn7xxkve7', 'dv91dn4n9', 'dw26yljz9', 'dj7dmlxk7',
         'd6780vxl2','dp7lomm47', 'dn7xxkke7', 'd6780vvl2', 'dp7ld1142',
         'dz7zzoo57','d09ywyy17', 'dv91ojjn2', 'd67oqkz69', 'dn7x4y5e2']

model = hub.get_model("mq8z0xxvq")
device = hub.Device("Samsung Galaxy S24 Ultra")

for i in coco2:
    dataset = hub.get_dataset(i)
    #print("Dataset information:", dataset)


    inference_job = hub.submit_inference_job(
        model=model,
        device=device,
        inputs=dataset,
    )
