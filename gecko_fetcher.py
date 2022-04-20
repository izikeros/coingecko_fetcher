#!/usr/bin/env python3
import json
import logging
import os
import time
from pathlib import Path

import requests

log = logging.getLogger(__name__)
log_level = os.environ.get("LOGLEVEL", "INFO")

level_format = "%(levelname)s:%(message)s"
logging.basicConfig(format=level_format, level=log_level)


# Try to read config file
config_dir = Path.home() / ".config" / "gecko_fetcher"
config_file = config_dir / "config.json"
os.makedirs(str(config_dir), exist_ok=True)

# Defaults
data_dir = Path.home() / "data"
data_file_name = "coingecko_data.json"
data_full_file = data_dir / data_file_name
num_entries_per_page = 200
p_max = 6
spark = "true"
# "1h,24h,7d,14d,30d,200d,1y" # NOTE: 24h is included by default,
percentage_price_change_periods = "1h,7d,14d,30d"

if os.path.isfile(str(config_dir)):
    with open(str(config_file), "r") as f:
        config = json.load(f)
    if "data_dir" in config:
        data_dir = Path(config["data_dir"])
    if "data_file_name" in config:
        data_file_name = config["data_file_name"]
    if "num_entries_per_page" in config:
        num_entries_per_page = int(config["num_entries_per_page"])
    if "p_max" in config:
        p_max = int(config["p_max"])
    if "spark" in config:
        spark = config["spark"]
    if "percentage_price_change_periods" in config:
        percentage_price_change_periods = config["percentage_price_change_periods"]
else:
    # If config file doesn't exist, create one with defaults
    config = {
        "data_dir": str(data_dir),
        "data_file": data_file_name,
        "num_entries_per_page": num_entries_per_page,
        "p_max": p_max,
        "spark": spark,
        "change": percentage_price_change_periods,
    }
    with open(str(config_file), "w") as f:
        json.dump(config, f)


ENDPOINT = "/coins/markets"
CURRENCY = "usd"
ORDER = "market_cap_desc"
BASE_URL = "https://api.coingecko.com/api/v3"


def get_coingecko_front_page(
    n=num_entries_per_page,
    p_max=p_max,
    spark=spark,
    change=percentage_price_change_periods,
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
        response = []
        try:
            raw_response = requests.get(url)
            response = json.loads(raw_response.content.decode("utf-8"))
        except Exception as e:
            pass
        p += 1
        all_responses.extend(response)
        # TODO: KS: 2021-04-22: consider adding sidecar file with information on last update time
    return all_responses


def save_responses(responses):
    # create data dir if not exists
    with open(data_full_file, "wt") as file_out:
        json.dump(responses, file_out)


if __name__ == "__main__":
    log.info("Fetcher initiated")
    while True:
        t = time.process_time()
        responses = get_coingecko_front_page()
        elapsed_time = time.process_time() - t
        log.info(f"{len(responses)} items fetched in {elapsed_time:.1f} s")
        save_responses(responses)
        log.info("Responses saved, waiting for next update")
        time.sleep(UPDATE_FREQUENCY_MINUTES * 60)
