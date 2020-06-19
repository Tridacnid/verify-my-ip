import argparse
import json
import logging
import os
import time

from requests import get, post
from yaml import load, Loader

# Constants
SLEEP_TIME_SECONDS: int = 60  # 1 minute
DEFAULT_CONFIG_FILE: str = "config.yaml"
DISCORD_API_GATEWAY_BASE_URL: str = "https://discord.com/api/v6"

# Set up logging
logging.basicConfig(format="%(levelname)s %(asctime)s: %(message)s", level=logging.INFO)

# Set up argument parser
parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="Periodically verify our expected public IP address hasn't changed.")
parser.add_argument("expected_ip_address", type=str, help="The expected IP address.")
parser.add_argument("--config", type=str, help="The path to a yaml configuration file.", default=DEFAULT_CONFIG_FILE)
args = parser.parse_args()
expected_ip_address: str = args.expected_ip_address
config_file: str = args.config

# Set up our yaml config data
with open(os.path.abspath(os.path.expanduser(config_file))) as f:
    config_str = f.read()
config = load(config_str, Loader=Loader)


class DiscordAlertException(Exception):
    pass


def send_discord_alert(message: str):
    data = {
        "content": f"{message}"
    }
    r = post(config.get("webhook"), json=data)
    logging.info(f"Hit Discord webhook. Result: {r}, text: {r.text}")
    if not r.ok:
        raise DiscordAlertException("Unable to send Discord alert")


send_discord_alert("verify-my-ip booting up")


# Main loop
def main():
    global expected_ip_address
    try:
        while True:
            try:
                r = get("https://api.ipify.org")
                ip: str = r.text
                if ip != expected_ip_address:
                    error_message: str = f"Public IP address {ip} does not match the expected value of {expected_ip_address}"
                    logging.error(error_message)
                    # Send discord message
                    send_discord_alert(message=f"WARN: {error_message}")
                    # send_discord_alert can throw an Exception, which bypasses updating our expected_ip_address
                    # without sending a message
                    logging.info(f"Updating expected IP address value to {ip}")
                    expected_ip_address = ip
                else:
                    logging.info(f"IP address verified to still be {ip}")
            except Exception as e:
                # log this as a warning
                logging.warning(f"Received exception: {e}")

            # Sleep for designated polling time
            time.sleep(SLEEP_TIME_SECONDS)

    except KeyboardInterrupt:
        logging.info("Shutting down.")


main()
send_discord_alert("verify-my-ip shutting down")