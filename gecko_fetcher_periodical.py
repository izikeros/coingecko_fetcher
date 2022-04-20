#!/usr/bin/env python3
# TODO: KS: 2021-11-14: perhaps you need to duplicate code to have standalone script
import logging
import os
import time

from gecko_fetcher import get_coingecko_front_page
from gecko_fetcher import save_responses

log = logging.getLogger(__name__)
log_level = os.environ.get("LOGLEVEL", "INFO")

level_format = "%(levelname)s:%(message)s"
logging.basicConfig(format=level_format, level=log_level)

# How often make serie of request to refresh local data
# TODO: KS: 2021-09-15: read from the config file from user home directory
UPDATE_FREQUENCY_MINUTES = 5

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
