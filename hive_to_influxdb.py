#!/usr/bin/env python

import settings as settings
import requests
import json
import time
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

# InfluxDB
client = InfluxDBClient(host=settings.influx_hostname, port=settings.influx_port)
client.switch_database(settings.influx_db_name)

# Logon to Hive
payload = {'username':settings.british_gas_username, 'password':settings.british_gas_password, 'devices':True, 'products':True}
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
url = 'https://beekeeper.hivehome.com:443/1.0/cognito/login'

while True:
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    print('Starting request @ ' + current_time)

    r = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)

    #print(json.dumps(r.json(), indent=2))

    sessionId = r.json()["token"]
    data = r.json()["products"]
    len_ = len(data)


    # Pull information for products
    for i in range(len_):
        product_name = data[i]["state"]["name"]
        product_type = data[i]["type"]

        # Add data to influx database
        if product_type == 'heating':
            temp = float(data[i]["props"]["temperature"])
            target_temp = float(data[i]["state"]["target"])
            status = data[i]["props"]["working"]
            
            if status is False:
                status_boolean = 0
            else:
                status_boolean = 1

            # Convert results into JSON ready for InfluxDB
            json_body = [
                {
                    "measurement": product_type,
                    "tags": {
                        "product_name": product_name,
                    },
                    "time": current_time,
                    "fields": {
                        "temp": temp,
                        "target_temp": target_temp,
                        "status": status,
                        "status_boolean": status_boolean
                    }
                }
            ]

        elif product_type == 'hotwater' or  product_type == 'activeplug':
            status = data[i]["state"]["status"]

            if status == "OFF":
                status_boolean = 0
            else:
                status_boolean = 1

            # Convert results into JSON ready for InfluxDB
            json_body = [
                {
                    "measurement": product_type,
                    "tags": {
                        "product_name": product_name,
                    },
                    "time": current_time,
                    "fields": {
                        "status": status,
                        "status_boolean": status_boolean
                    }
                }
            ]

        print(json_body)
        client.write_points(json_body)

    print("Sleeping for 60 seconds")
    print('')
    print('')

    time.sleep(60)
