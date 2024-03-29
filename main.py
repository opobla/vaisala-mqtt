import json
import os
import time
import paho.mqtt.publish as publish
from datetime import datetime
from timeloop import Timeloop
from datetime import timedelta
from drivers import VaisalaDriver

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.



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
            "isodatetime": current_date.isoformat(),
            "datetime": str(time.time_ns() // 1000),
            "temp_c": client.get_temperature(),
            "atmpres_Pa": client.get_pressure() * 100,
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
