import os
import json
from processor import process_file

if "DEEPSEEK_API_KEY" not in os.environ:
    print("DEEPSEEK_API_KEY not set. Demo skipped. Set the key to run extraction.")
    exit(0)

# Hardcoded sample inventory report (CSV)
sample_data = (
    b"product,stock,capital_value,sales_90d\n"
    b"Dead Product X,200,30000,0\n"
    b"Slow Mover Y,80,5000,3\n"
    b"Healthy Product Z,150,2000,60\n"
)

results = process_file(sample_data)
print(json.dumps(results, indent=2))
exit(0)
