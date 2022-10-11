import re
from datetime import datetime, timedelta
import telnetlib

class VaisalaDriver:
    """The vaisala driver
    """

    SEND_CMD_OUTPUT_FORMAT='6.6 "P=" P " " U6 3.2 "T=" T " " U3 3.1 "RH=" RH " " U4 \r \n'

    def __init__(self, ip, port=23, time_to_live_s=40):
        self.temperature_in_celsius = None
        self.pressure_in_hPa = None
        self.relative_humidity = None
        self.last_update = None
        self.vaisala_ip = ip
        self.vaisala_port = port
        self.time_to_live_s = time_to_live_s
        self._telnet_client = None

    @property
    def telnet_client(self):
        if not self._telnet_client:
            self._telnet_client = telnetlib.Telnet(self.vaisala_ip, self.vaisala_port)
            self.telnet_client.read_until(">".encode("ascii"))
            self.telnet_client.write(self.SEND_CMD_OUTPUT_FORMAT.encode('ASCII'))
            self.telnet_client.read_until(">".encode("ascii"))
        return self._telnet_client 
            
    def update_info(self):
        self.telnet_client.write("SEND".encode("ascii") + b"\r")
        self.telnet_client.read_until(b"\n")
        response = self.telnet_client.read_until(b"\n")
        self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity = self.parse_response(response)
        self.last_update = datetime.now()
        return self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity

    def get_pressure(self):
        if self.is_info_expired(): self.update_info()
        return self.pressure_in_hPa

    def get_temperature(self):
        if self.is_info_expired(): self.update_info()
        return self.temperature_in_celsius

    def get_relative_humidity(self):
        if self.is_info_expired(): self.update_info()
        return self.relative_humidity

    def parse_response(self, response):
        self.pressure_in_hPa = self._extract_measurement("P", response)
        self.temperature_in_celsius = self._extract_measurement("T", response)
        self.relative_humidity = self._extract_measurement("RH", response)
        return self.pressure_in_hPa, self.temperature_in_celsius, self.relative_humidity

    @staticmethod
    def _extract_measurement(unit, text):
        try:
            regex = '[ \t]*{}=[ \t]*(-?[0-9.]+)(e-?[0-9]+)?'.format(unit)
            token = re.search(regex.encode('ASCII'), text)
            result = token.group(1) + token.group(2) if token.group(2) else token.group(1)
            return float(result)
        except AttributeError:
            return None

    def is_info_expired(self):
        return self.last_update is None or \
            datetime.now() - self.last_update > timedelta(seconds=self.time_to_live_s)


if __name__ == '__main__':
    client = VaisalaDriver('192.168.0.103')
    print(f'{"Temperature:":<20}{client.get_temperature():>8.2f} ºC')
    print(f'{"Pressure:":<20}{client.get_pressure():>8.2f} hPas')
    print(f'{"Relative humidity:":<20}{client.get_relative_humidity():>8.2f} %')
    print("Fin del loop")
