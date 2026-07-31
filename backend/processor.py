import os
import json
from openai import OpenAI

def process_file(file_bytes: bytes) -> list[dict]:
    content = file_bytes.decode('utf-8')

    prompt = (
        "You are an inventory risk analyst. Given the following inventory data (CSV or text), "
        "extract each product’s risk status. Return a JSON array of objects with keys:\n"
        '  "title": the product name or SKU (the primary entity tracked by the retailer)\n'
        '  "status": one of "dead:critical", "slow_moving:warning", "healthy:good"\n'
        '  "details": a dict holding relevant metrics (e.g., capital_value, sales_velocity, days_supply)\n'
        '  "due_date": ISO date string if a review is due, otherwise null\n\n'
        "Classification rules:\n"
        "- dead:critical → no sales in last 90 days AND high capital tied up (>$10,000).\n"
        "- slow_moving:warning → low sales velocity (<10 units in 90 days) but some capital at risk.\n"
        "- healthy:good → good sales velocity and low capital risk.\n\n"
        "Data:\n"
        + content
    )

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a precise JSON extractor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )

    result_text = response.choices[0].message.content.strip()
    # Remove markdown code fences if present
    if result_text.startswith("```"):
        lines = result_text.splitlines()
        result_text = "\n".join(lines[1:-1])

    items = json.loads(result_text)
    if isinstance(items, dict):
        items = [items]

    allowed_statuses = {"dead:critical", "slow_moving:warning", "healthy:good"}
    for item in items:
        item.setdefault("title", "Unknown")
        item.setdefault("details", {})
        item.setdefault("due_date", None)
        if item.get("status") not in allowed_statuses:
            item["status"] = "healthy:good"

    return items
