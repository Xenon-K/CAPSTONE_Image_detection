import subprocess
import re
import csv

# Device name (customize this)
device = "QCS8550 (Proxy)"
runtime = 'tflite'
# Sanitize device name for safe file naming
safe_device_name = device.replace(" ", "_")
csv_file = f"models_{safe_device_name}_{runtime}.csv"

# Define your export commands
commands = [
    fr'python -m qai_hub_models.models.conditional_detr_resnet50.export --device "{device}" --target-runtime {runtime} --height 480 --width 480 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.detr_resnet101.export --device "{device}" --target-runtime {runtime} --height 480 --width 480 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.detr_resnet101_dc5.export --device "{device}" --target-runtime {runtime} --height 480 --width 480 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.detr_resnet50.export --device "{device}" --target-runtime {runtime} --height 480 --width 480 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.detr_resnet50_dc5.export --device "{device}" --target-runtime {runtime} --height 480 --width 480 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov3.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov5.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov6.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov7.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov8_det.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov10_det.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov11_det.export --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov7.export --quantize w8a8 --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov8_det.export --quantize w8a8 --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing',
    fr'python -m qai_hub_models.models.yolov11_det.export --quantize w8a8 --device "{device}" --target-runtime {runtime} --height 640 --width 640 --skip-profiling --skip-inferencing'
]

# Regex to extract model name and hub ID
pattern = r'python .*?\\([^\\]+)\\demo\.py.*?--hub-model-id (\S+?) --device'

# Open CSV file and write headers
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Model Name", "Hub Model ID"])

    for cmd in commands:
        print(f"\n🔧 Running command:\n{cmd}\n")

        # Run command and capture output line-by-line
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            encoding='utf-8',  # Decode as UTF-8
            errors='ignore'    # Ignore undecodable characters
        )

        all_lines = []
        for line in process.stdout:
            print(line, end="")  # Real-time print
            all_lines.append(line.strip())

        process.wait()

        # Only analyze the last 5 lines
        last_lines = all_lines[-5:]
        stdout = "\n".join(last_lines)

        # Extract relevant information
        match = re.search(pattern, stdout)
        if match:
            model_name = match.group(1)
            hub_model_id = match.group(2)
            print(f"✅ Found model: {model_name}, ID: {hub_model_id}")
            writer.writerow([model_name, hub_model_id])
        else:
            print("⚠️ No matching line found in last 5 lines.")
