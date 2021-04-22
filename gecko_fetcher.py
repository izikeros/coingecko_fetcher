#!/usr/bin/env python3
import json
import time

import requests

# location where the data will be saved
DATA_FILE = "/home/safjan/data/coingecko_data.json"

BASE_URL = "https://api.coingecko.com/api/v3"
ENDPOINT = "/coins/markets"
CURRENCY = "usd"
ORDER = "market_cap_desc"

# How often make serie of request to refresh local data
UPDATE_FREQUENCY_MINUTES = 5


def get_coingecko_front_page(
    n=200,
    p_max=6,
    spark="true",
    change="1h,7d,14d,30d",  # "1h,24h,7d,14d,30d,200d,1y" # NOTE: 24h is by default
):

    all_responses = []
    for p in range(1, p_max + 1):
        url = (
            f"{BASE_URL}{ENDPOINT}"
            f"?vs_currency={CURRENCY}"
            f"&order={ORDER}"
            f"&per_page={n}"
            f"&page={p}"
            f"&sparkline={spark}"
            f"&price_change_percentage={change}"
        )
        raw_response = requests.get(url)
        response = json.loads(raw_response.content.decode("utf-8"))
        p += 1
        all_responses.extend(response)
        # TODO: KS: 2021-04-22: create data dir if not exists
        # TODO: KS: 2021-04-22: solve need for providing username
        # TODO: KS: 2021-04-22: try/except if data dir exists
        # TODO: KS: 2021-04-22: consider adding sidecar file with information on last update time
    with open(DATA_FILE, "wt") as file_out:
        json.dump(all_responses, file_out)


if __name__ == "__main__":
    while True:
        get_coingecko_front_page()
        time.sleep(UPDATE_FREQUENCY_MINUTES * 60)
