import json
from app import price_checker

with open("tracking_data.json") as f:
    data = json.load(f)

price_checker(data)
