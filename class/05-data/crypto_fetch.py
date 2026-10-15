import json

with open("data/cmc_listings.json", "r") as f:
    data = json.load(f)

for coin in data["data"][:5]:
    quote = coin["quote"][0]
    print(f"{coin['name']}: ${quote['price']:.2f} ({quote['percent_change_24h']:.2f}%)")
