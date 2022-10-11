import json
import os
import time
import paho.mqtt.publish as publish
from datetime import datetime
from timeloop import Timeloop
from datetime import timedelta
from drivers import VaisalaDriver


mqtt_topic = os.environ["MQTT_TOPIC"]
mqtt_broker_hostname = os.environ["MQTT_BROKER_HOSTNAME"]
mqtt_broker_port = int(os.environ["MQTT_BROKER_PORT"])
vaisala_location = os.environ["VAISALA_LOCATION"]
vaisala_polling_secs = int(os.environ.get("VAISALA_POLLING_SECS", 60))


tl = Timeloop()


@tl.job(interval=timedelta(seconds=vaisala_polling_secs))
def publish_vaisala():
    client = VaisalaDriver(vaisala_location)
    current_date = datetime.now()

    payload = {
            "datetime": current_date.isoformat(),
            "temperature_C": client.get_temperature(),
            "atm_pressure_hPas": client.get_pressure(),
            "rel_humidity": client.get_relative_humidity()
    }

    publish.single(
            mqtt_topic, 
            payload=json.dumps(payload), 
            qos=0, 
            retain=False, 
            hostname=mqtt_broker_hostname, 
            port=mqtt_broker_port, 
            client_id="vaisala-mqtt", 
            keepalive=60, 
            transport="tcp"
    )

if __name__ == "__main__":
    tl.start(block=True)
