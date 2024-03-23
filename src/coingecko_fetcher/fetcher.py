#!/usr/bin/env python3
"""Fetch data from CoinGecko API and save to file.

Prerequisites:
- Python 3.6 or later
- requests library

For troubleshooting, set the environment variable LOGLEVEL to DEBUG.
$ LOGLEVEL=DEBUG ./gecko_fetcher.py

To run the fetcher periodically, use the -p flag:
$ ./gecko_fetcher.py -p

To run the fetcher once, use the -o flag:
$ ./gecko_fetcher.py -o

To run the fetcher once and save the responses to a file, use the -s flag:
$ ./gecko_fetcher.py -s

"""

import argparse
import json
import logging
import os
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

# from requests.packages.urllib3.util.retry import Retry
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)
log_level = os.environ.get("LOGLEVEL", "INFO")

level_format = "[%(levelname).1s] %(message)s"
logging.basicConfig(format=level_format, level=log_level)

UPDATE_FREQUENCY_MINUTES = 5

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

if os.path.isfile(str(config_file)):
    log.debug("Config file found. Reading...")
    with open(str(config_file)) as f:
        config = json.load(f)

    if "data_dir" in config:
        data_dir = Path(config["data_dir"])
        log.debug("data_dir: %s", data_dir)
    if "data_file_name" in config:
        data_file_name = config["data_file_name"]
        log.debug("data_file_name: %s", data_file_name)
    if "num_entries_per_page" in config:
        num_entries_per_page = int(config["num_entries_per_page"])
        log.debug("num_entries_per_page: %s", num_entries_per_page)
    if "p_max" in config:
        p_max = int(config["p_max"])
        log.debug("p_max: %s", p_max)
    if "spark" in config:
        spark = config["spark"]
        log.debug("spark: %s", spark)
    if "percentage_price_change_periods" in config:
        percentage_price_change_periods = config["percentage_price_change_periods"]
        log.debug(
            "percentage_price_change_periods: %s", percentage_price_change_periods
        )
else:
    log.debug("Config file not found. Using defaults and creating config file...")
    # If config file doesn't exist, create one with defaults
    config = {
        "data_dir": str(data_dir),
        "data_file_name": data_file_name,
        "num_entries_per_page": num_entries_per_page,
        "p_max": p_max,
        "spark": spark,
        "percentage_price_change_periods": percentage_price_change_periods,
    }
    with open(str(config_file), "w") as f:
        json.dump(config, f, indent=4)
    log.debug("Config file created.")


ENDPOINT = "/coins/markets"
CURRENCY = "usd"
ORDER = "market_cap_desc"
BASE_URL = "https://api.coingecko.com/api/v3"


retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


def get_coingecko_front_page(
    n=num_entries_per_page,
    p_max=p_max,
    spark=spark,
    change=percentage_price_change_periods,
    base_url=BASE_URL,
    endpoint=ENDPOINT,
    currency=CURRENCY,
    order=ORDER,
    with_retry=False,
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
            log.debug(f"Requesting page: {p}")
            raw_response = http.get(url) if with_retry else requests.get(url)
        except requests.ConnectionError as e:
            print(
                "OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n"
            )
            print(str(e))
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
        except KeyboardInterrupt:
            print("Someone closed the program")

        try:
            response = json.loads(raw_response.content.decode("utf-8"))
            log.debug("...got response")
            all_responses.extend(response)
        except json.decoder.JSONDecodeError as e:
            print("OOPS!! JSON Decode Error")
            log.error(f"Error: {e}")
        p += 1

        # TODO: KS: 2021-04-22: consider adding sidecar file with information on last update time
    return all_responses


def save_responses(responses):
    with open(data_full_file, "w") as file_out:
        json.dump(responses, file_out)
    log.info(f"Fetcher - Responses saved to: {data_full_file}, exiting")


def run_once():
    log.info("Fetcher - initiated")
    t = time.time()
    cg_responses = get_coingecko_front_page()
    elapsed_time = time.time() - t
    log.info(f"Fetcher - {len(cg_responses)} items fetched in {elapsed_time:.1f} s")
    save_responses(cg_responses)


def run_forever():
    while True:
        while True:
            run_once()
            time.sleep(UPDATE_FREQUENCY_MINUTES * 60)


# TODO: KS: 2022-04-20: use argparse to parse command line arguments and enable running periodically
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch data from CoinGecko")

    parser.add_argument(
        "-p",
        "--periodically",
        action="store_true",
        default=False,
        help="run fetching periodically",
    )
    args = parser.parse_args()

    if args.periodically:
        run_forever()
    else:
        run_once()
