import qai_hub as hub

model = hub.get_model("mq8z0xxvq")
device = hub.Device("Samsung Galaxy S24 Ultra")

# Profile the previously compiled model
'''profile_job = hub.submit_profile_job(
    model=model,
    device=device,
)
assert isinstance(profile_job, hub.ProfileJob)'''

profile_job = hub.get_job('jpvq26krg')

results = profile_job.download_profile()
#profile_job.download_results('artifacts')

exec_details = results['execution_detail']
exec_summary = results['execution_summary']

for keys in exec_summary:
    print(keys, ":", exec_summary[keys])

#print(exec_summary.keys())
#print(exec_summary)
