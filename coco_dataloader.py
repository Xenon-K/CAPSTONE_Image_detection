import os
import numpy as np
from PIL import Image
import csv
import qai_hub as hub


# Folder containing your images
folder_path = 'val2017'

# Initialize output CSV file path and model flag
csv_file_path = 'image_details.csv'
model_flag = 0   # 0 for detr, 1 for yolo
quant_flag = 0  # 0 for float 32, 1 for uint8
transpose_flag = 0 # 0 for (1,480,480,3) tflite, 1 for (1,3,480,480) onnx


# Function to load images in batches
def load_images_in_batches(folder_path, batch_size):
    # Get the list of image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]

    # Prepare CSV for storing image names and original dimensions
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Image Name', 'Original Width', 'Original Height'])

        batch_start = 0
        while batch_start < len(image_files):
            batch_end = min(batch_start + batch_size, len(image_files))
            batch_files = image_files[batch_start:batch_end]

            # Prepare numpy array to store image data for this batch
            image_data_batch = []
            datasets = []

            for image_file in batch_files:
                # Open the image and get its original dimensions
                image_path = os.path.join(folder_path, image_file)
                with Image.open(image_path).convert("RGB") as img:
                    original_width, original_height = img.size
                    image_name = os.path.splitext(image_file)[0]
                    image_name = image_name.lstrip('0')

                    # Convert image to numpy array and store it in batch
                    image_resize = img.resize((resize, resize), resample=Image.Resampling.BILINEAR)   # resize for model (detr 480,480; yolo 640,640)


                    image_array = np.array(image_resize, dtype=np.float32)
                    extra_suffix = ''

                    if model_flag == 0:
                        # normalizing for detr
                        mean = np.array([0.485, 0.456, 0.406])
                        std = np.array([0.229, 0.224, 0.225])
                        image_array = ((image_array / 255.0 - mean) / std).astype(np.float32)
                        extra_suffix += 'norm_small'
                    elif quant_flag == 0:
                        image_array = (image_array / 255.0).astype(np.float32)
                    else:
                        image_array = image_array.astype(np.uint8)
                        extra_suffix += 'quant'

                    if transpose_flag == 1:
                        image_array = np.transpose(image_array, (2,0,1))
                        extra_suffix += 'ONNX'

                    image_array = np.expand_dims(image_array, axis=0)
                    #print(image_array.dtype)
                    #print(image_array.shape)
                    image_data_batch.append(image_array)

                    # Write the image name and its original dimensions to the CSV
                    csv_writer.writerow([image_name, original_width, original_height])

            # Move to the next batch
            batch_start = batch_end

            data = dict(
                image=image_data_batch
            )
            batch_number = batch_start // batch_size
            batches = int(5000/batch_size)
            dataset_name = 'coco_' + str(batch_number) + 'of' + str(batches) + '_' + str(resize) + extra_suffix
            print("Uploading", dataset_name)
            hub_dataset = hub.upload_dataset(data, dataset_name)
            print(hub_dataset)
            print(f"Processed batch {batch_number} with {len(batch_files)} images.\n")

    print("Finished processing all batches!")

if model_flag == 0:
    batch_size = 250
    resize = 480
elif model_flag == 1:
    batch_size = 250
    resize = 640

# Call the function to process images
load_images_in_batches(folder_path, batch_size)
