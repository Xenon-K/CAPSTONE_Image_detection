import numpy as np
from PIL import Image
import qai_hub as hub
import os
import time



# yolo (1, 640, 640, 3) float 32
yolo = ['dz2roj5g2', 'dn7xxkw67', 'd693pkq07', 'dq9ko0pd7', 'dj7dmljq7',
        'dk7g4eje7','dn7xxkve7', 'dv91dn4n9', 'dw26yljz9', 'dj7dmlxk7',
         'd6780vxl2','dp7lomm47', 'dn7xxkke7', 'd6780vvl2', 'dp7ld1142',
         'dz7zzoo57','d09ywyy17', 'dv91ojjn2', 'd67oqkz69', 'dn7x4y5e2']

Device = 'D49'
Model = 'M19'
Runtime = 'tf'

model = hub.get_model("mnwgj23wq")
device = hub.Device("Samsung Galaxy S24 Ultra")

job_list = []

for i in yolo:
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
    new_file_path = os.path.join(folder_path, new_name)

    # Rename the file
    os.rename(old_file_path, new_file_path)