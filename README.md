# Install

```
poetry install
```

# Run example

```
export MQTT_TOPIC="icaro/vaisala"
export MQTT_BROKER_HOSTNAME="10.8.0.19"
export MQTT_BROKER_PORT=9000
export VAISALA_LOCATION="192.168.0.103"
poetry run python main.py
```
