import os
import time
import json
import requests
import sys
sys.path.insert(0, 'backend')  # so import processor works
import processor

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_KEY']
PRODUCT_ID = os.environ['PRODUCT_ID']

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

def poll_jobs():
    url = f"{SUPABASE_URL}/rest/v1/jobs"
    params = {
        "status": "eq.pending",
        "job_type": "eq.process_upload",
        "product_id": f"eq.{PRODUCT_ID}"
    }
    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

def download_file(bucket, path, dest):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(r.content)

def upload_file(bucket, path, content):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
    r = requests.put(url, data=content, headers=HEADERS)
    r.raise_for_status()

def update_job(job_id, data):
    url = f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}"
    r = requests.patch(url, json=data, headers=HEADERS)
    r.raise_for_status()

def create_record(record):
    url = f"{SUPABASE_URL}/rest/v1/records"
    r = requests.post(url, json=record, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def process_job(job):
    job_id = job['id']
    try:
        # Download input file from uploads bucket
        bucket = "uploads"
        paths = job.get('input_file_paths') or []
        if not paths and job.get('input_file_path'):
            paths = [job['input_file_path']]
        file_path = paths[0] if paths else ''
        local_file = os.path.basename(file_path)
        download_file(bucket, file_path, local_file)

        # Run processor
        with open(local_file, "rb") as f:
            result = processor.process_file(f.read())

        # Write records
        for rec in result:
            record = {
                "product_id": PRODUCT_ID,
                "customer_id": job.get('customer_id'),
                "title": rec['title'],
                "status": rec['status'],
                "details": json.dumps(rec.get('details', {})),
                "source_file_path": file_path,
                "due_date": rec.get('due_date')
            }
            create_record(record)

        # Upload result
        result_content = json.dumps(result).encode('utf-8')
        result_path = f"results/{job_id}.json"
        upload_file("results", result_path, result_content)

        # Mark completed
        update_job(job_id, {
            "status": "completed",
            "output_file_path": result_path,
            "result_summary": "Processed successfully",
            "completed_at": "now()"
        })
    except Exception as e:
        update_job(job_id, {
            "status": "failed",
            "result_summary": str(e),
            "completed_at": "now()"
        })

if __name__ == "__main__":
    while True:
        jobs = poll_jobs()
        for job in jobs:
            process_job(job)
        time.sleep(60)
