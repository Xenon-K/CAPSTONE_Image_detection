import qai_hub as hub
from qai_hub_models.utils.printing import print_profile_metrics_from_job
from typing import Any
from qai_hub_models.configs.perf_yaml import bytes_to_mb
from collections import Counter
'''
model = hub.get_model("mnov4je9m")
device = hub.Device("Samsung Galaxy S24 Ultra")

# Profile the previously compiled model
profile_job = hub.submit_profile_job(
    model=model,
    device=device,
)
assert isinstance(profile_job, hub.ProfileJob)
'''
profile_job = hub.get_job('jpvq26krg')

results = profile_job.download_profile()
#profile_job.download_results('artifacts')

exec_details = results['execution_detail']
exec_summary = results['execution_summary']

profile_data: dict[str, Any] = profile_job.download_profile()  # type: ignore
print_profile_metrics_from_job(profile_job, profile_data)

for keys in exec_summary:
    print(keys, ":", exec_summary[keys])

inference_time = exec_summary["estimated_inference_time"]/1000
peak_memory_bytes = exec_summary["inference_memory_peak_range"]
mem_min = bytes_to_mb(peak_memory_bytes[0])
mem_max = bytes_to_mb(peak_memory_bytes[1])

print(mem_min)
print(mem_max)

compute_unit_counts = Counter(
        [op.get("compute_unit", "UNK") for op in profile_data["execution_detail"]]
    )
print(compute_unit_counts['NPU'])
#print(exec_details.keys())
#print(exec_details)