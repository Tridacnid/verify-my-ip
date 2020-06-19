# verify-my-ip
A small python application that will periodically check your publicly visible IP
and send an email alert if the retrieved IP address doesn't match the expected value.

Nice for monitoring a home server that is on a dynamic IP address.

### Usage
`python verify-my-ip.py <expected ipv4 address> --config <path to config.yaml file>`

### Configuration
Currently only one yaml element is needed: `webhook`

`webhook` is a Discord webhook that can be POSTed to by the script during startup and when a discrepancy is detected.
