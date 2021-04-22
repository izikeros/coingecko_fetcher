# Gecko Fetcher
Service for periodical fetching data from the [CoinGecko.com](https://www.coingecko.com/) and saving it in json file.

CoinGecko is a website and mobile app used to aggregate information regarding the performance of the majority of all cryptocurrencies available.

By default, service is making request to Coingecko api endpoint `'/coins/markets` to fetch data of the first 1200 coins/tokens and save them to file `~/data/coingecko_data.json`. It was meant to work in the background and ensure local file with up-to-date (but not real-time) coin prices for other apps.

## Requirements

Requires `python3` and `requests` library.

```sh
pip install requests
```

## Installation

### install script

Clone the repository. It is suggested to keep main script `gecko_fetcher.py` in `~/bin/`. You need to provide proper path to this script in the file that define `systemd` service (see install service section below).

### edit path in the script

Provide proper path to the file where data will be saved. You need to edit `gecko_fetcher.py` file. In my case it is:

```python
DATA_FILE = "/home/safjan/data/coingecko_data.json"
```

### install service

Edit `gecko_fether.service` and provide proper path to the script and the python executable.

Copy `gecko_fether.service` to `/etc/systemd/system/gecko_fetcher.service`

The `ExecStart` flag takes in the command that you want to run. So basically the first argument is the python path (in my case it’s python3) and the second argument is the path to the script that needs to be executed. `Restart` flag is set to always because I want to restart my service if the server gets restarted.  Now we need to reload the daemon.
```sh
sudo systemctl daemon-reload
```
Let’s enable our service so that it doesn’t get disabled if the server restarts.
```sh
sudo systemctl enable gecko_fetcher.service
```
And now let’ start our service.

```sh
sudo systemctl start gecko_fetcher.service
```
Now our service is up and running.

### control service

There are several commands you can do to start, stop, restart, and check status.
To stop the service.

```sh
sudo systemctl stop gecko_fetcher.service
```
To restart.
```sh
sudo systemctl restart ngecko_fetcher.service
```
To check status.
```sh
sudo systemctl status gecko_fetcher.service
```



## Credits

Thanks to [WasiUllah Khan](https://wasiullah-khan21.medium.com/) for the article [Setup a python script as a service through systemctl/systemd](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) which was great instruction how to create service. Parts of the article were adopted and included to this README.