import os
import numpy as np
from PIL import Image
import csv
import qai_hub as hub

# Folder containing your images
folder_path = 'val2017'

# Initialize batch size and output CSV file path
batch_size = 250
csv_file_path = 'image_details.csv'
resize = 640


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

            for image_file in batch_files:
                # Open the image and get its original dimensions
                image_path = os.path.join(folder_path, image_file)
                with Image.open(image_path) as img:
                    original_width, original_height = img.size
                    image_name = os.path.splitext(image_file)[0]
                    image_name = image_name.lstrip('0')

                    # Convert image to numpy array and store it in batch
                    image_resize = img.resize((resize, resize))   # resize for model (detr 480,480; yolo 640,640)
                    if image_resize.mode != 'RGB':
                        # If the image is not RGB, convert it to RGB
                        image_resize = image_resize.convert('RGB')

                    image_array = np.array(image_resize, dtype=np.float32)
                    image_array = np.expand_dims(image_array / 255.0, axis=0)
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
            dataset_name = 'coco_' + str(batch_number) + 'of' + str(batches) + '_' + str(resize)
            print("Uploading", dataset_name)
            hub_dataset = hub.upload_dataset(data, dataset_name)

            print(f"Processed batch {batch_number} with {len(batch_files)} images.")

    print("Finished processing all batches!")


# Call the function to process images
load_images_in_batches(folder_path, batch_size)
