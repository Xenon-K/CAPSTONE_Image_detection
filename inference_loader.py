import numpy as np
from PIL import Image
import qai_hub as hub

# gets last 10 datasets and prints ids/summaries
#dataset = hub.get_datasets(limit=30)
#print("Dataset information:", dataset)


# yolo (1, 640, 640, 3) float 32
yolo = ['dz2roj5g2', 'dn7xxkw67', 'd693pkq07', 'dq9ko0pd7', 'dj7dmljq7',
        'dk7g4eje7','dn7xxkve7', 'dv91dn4n9', 'dw26yljz9', 'dj7dmlxk7',
         'd6780vxl2','dp7lomm47', 'dn7xxkke7', 'd6780vvl2', 'dp7ld1142',
         'dz7zzoo57','d09ywyy17', 'dv91ojjn2', 'd67oqkz69', 'dn7x4y5e2']

detr = ['dj7d63pq9', 'dv91oekn2', 'dn7x4qre2', 'dv91oevn2', 'dj7d63vk9',
        'dz2rn66l7', 'dd9p5zzo7', 'dz2rn6vl7', 'dr2qy6my7', 'dp7ldk5r2']

model = hub.get_model("mn1ekr4rm")
device = hub.Device("Samsung Galaxy S24")

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

for jobs in job_list:
    jobs.download_results('toSort')
