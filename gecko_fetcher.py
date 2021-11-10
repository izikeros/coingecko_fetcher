#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path

import requests

import logging

log = logging.getLogger(__name__)
log_level = os.environ.get("LOGLEVEL", "INFO")

level_format = '%(levelname)s:%(message)s'

logging.basicConfig(format=level_format, level=log_level)

# location where the data will be saved
# TODO: KS: 2021-09-15: read from the config file from user home directory
DATA_FILE = str(Path.home() / "data/coingecko_data.json")

ENDPOINT = "/coins/markets"
CURRENCY = "usd"
ORDER = "market_cap_desc"
BASE_URL = "https://api.coingecko.com/api/v3"

# How often make serie of request to refresh local data
# TODO: KS: 2021-09-15: read from the config file from user home directory
UPDATE_FREQUENCY_MINUTES = 5


def get_coingecko_front_page(
    n=200,
    p_max=6,
    spark="true",
    change="1h,7d,14d,30d",  # "1h,24h,7d,14d,30d,200d,1y" # NOTE: 24h is by default,
    base_url=BASE_URL,
    endpoint=ENDPOINT,
    currency=CURRENCY,
    order=ORDER,
):
    all_responses = []
    for p in range(1, p_max + 1):
        url = (
            f"{base_url}{endpoint}"
            f"?vs_currency={currency}"
            f"&order={order}"
            f"&per_page={n}"
            f"&page={p}"
            f"&sparkline={spark}"
            f"&price_change_percentage={change}"
        )
        try:
            raw_response = requests.get(url)
            response = json.loads(raw_response.content.decode("utf-8"))
        except:
            pass
        p += 1
        all_responses.extend(response)
        # TODO: KS: 2021-04-22: create data dir if not exists
        # TODO: KS: 2021-04-22: solve need for providing username
        # TODO: KS: 2021-04-22: try/except if data dir exists
        # TODO: KS: 2021-04-22: consider adding sidecar file with information on last update time
    return all_responses


def save_responses(responses):
    with open(DATA_FILE, "wt") as file_out:
        json.dump(responses, file_out)


if __name__ == "__main__":
    log.info("Fetcher initiated")
    while True:
        t = time.process_time()
        responses = get_coingecko_front_page()
        elapsed_time = time.process_time() - t
        log.info(f"{len(responses)} items fetched in {elapsed_time}")
        save_responses(responses)
        log.info("Responses saved, waiting for next update")
        time.sleep(UPDATE_FREQUENCY_MINUTES * 60)
