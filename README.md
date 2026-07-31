# Slow-Moving & Dead Inventory Capital-at-Risk Monitor

A backend service that processes multi-platform retailer inventory reports to flag
capital tied up in slow-moving and dead stock.

**Product archetype:** Capital-at-Risk Monitor. It watches uploaded inventory
reports (CSV / plain text), classifies each product as `dead:critical`,
`slow_moving:warning`, or `healthy:good`, and writes structured JSON records so
retailers can see exactly how much working capital is at risk.

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Set environment variables:
   - `DEEPSEEK_API_KEY` — key for the DeepSeek LLM used to extract risk statuses.
   - `SUPABASE_URL` — Supabase project URL.
   - `SUPABASE_SERVICE_KEY` — service-role key for the jobs/records API.
   - `PRODUCT_ID` — the product id stored on jobs to poll.

## What the poller expects as input

- A `jobs` table with `status` set to `pending` and `job_type` set to `process_upload`.
  Only jobs whose `product_id` matches `PRODUCT_ID` are picked up.
- Each job must provide at least one input file, either via a single
  `input_file_path` or a list `input_file_paths`.
- Files are downloaded from Supabase Storage under the `uploads/` bucket and may
  be CSV or plain text inventory reports (e.g. product, stock, capital_value,
  sales_90d rows).

## How it works

1. `poller.py` continuously polls for pending jobs every 30 seconds.
2. It downloads each input file, calls `process_file()` which sends the raw data
   to DeepSeek and parses the returned JSON array.
3. For every extracted product it inserts a record into the `records` table with
   the product title, risk status, details, optional due date, and source path.
4. The job is marked `completed` (or `failed` with a short summary).

## Usage

- **Continuous polling**: `python poller.py`
- **Quick demo**: `python run_demo.py` — processes a hardcoded sample report and prints JSON.
- **Tests**: `python -m unittest run_tests.py` — mocked unit tests, no API call needed.

Dashboard: https://slow-moving-dead-inventory-capital-at-ri.vokrix.co
Vercel: slow-moving-dead-inventory-capital-at-ri
Railway: 
Railway: slow-moving-dead-inventory-capital-at-ri
Cloudflare: slow-moving-dead-inventory-capital-at-ri.vokrix.co

Billing: 
Billing: price_1TzHNO2c9uGCcgMSi9B8fQiJ
