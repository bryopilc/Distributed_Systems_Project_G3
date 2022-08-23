#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Grupo 3 - Sistemas Distribuidos
import os
from datetime import datetime, timezone
import sys
import requests
import time
import uuid
import boto3

db = boto3.client('dynamodb',
  aws_access_key_id='AKIAWCB2QHJSQDUZYIMS',
  aws_secret_access_key='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',
  region_name='us-east-1')


def lambda_handler(event, context):
    DB_HOST = os.environ["DB_HOST"]
    DB_USER = os.environ["DB_USER"]
    DB_PASS = os.environ["DB_PASS"]
    print("Connected to %s as %s" % (DB_HOST, DB_USER))
    return None

#URL base de API Kaiterra y APIKEY del sensor
API_BASE_URL = "https://api.kaiterra.com/v1/"
API_KEY = "NGZkOTRlZGUzYWE1NGEzYzk2NWYyYTY0Zjk1NjdlNmYwODhh"

# Sesión al server
session = requests.session()

#Recibir contenido de parametros ambientales mediante petición HTTP GET
def do_get(relative_url, *, params={}, headers={}):
    import json

    params['key'] = API_KEY
    url = API_BASE_URL.strip("/") + relative_url
    
    response = session.get(url, params=params, headers=headers)
    
    content_str = ''
    if len(response.content) > 0:
        content_str = response.content.decode('utf-8')
        print()

    response.raise_for_status()
        
    if len(content_str) > 0:
        return json.loads(content_str)

    return None

#path de dispositivo
def get_laser_egg(id: str):
    return do_get("/lasereggs/" + id)

#mostrar temperatura filtrada desde json recibido
def summarize_laser_egg(id: str):
    data = get_laser_egg(id)
    latest_data = data.get('info.aqi')
    
    print(latest_data)
    
    if latest_data:
        ts = parse_rfc3339_utc(latest_data['ts'])
        ts_ago = (datetime.now(timezone.utc) - ts).total_seconds()
        
        temp = latest_data['data'].get('temp')
        if temp:
            print("  TEMPERATURA LST:   {} °C".format(temp))
            return temp
        else:
            print("  TEMPERATURA LST:   no data")

    else:
        print("Kaiterra no ha cargado datos aún")

#verificar disponibilidad del dispositivo
def check_available(name):
    import importlib
    try:
        _ = importlib.import_module(name, None)
    except ImportError:
        print("Módulo perdido '{}'.  Ejecute nuevamente este código:".format(name))
        print("   pip -r requirements.txt")
        sys.exit(1)


def parse_rfc3339_utc(ts: str) -> datetime:
    '''
    Devuelve timestamp como un timezone-aware en la zona UTC respectiva.
    '''
    return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def putData(id: str):
    id_register = str(uuid.uuid4())
    data = get_laser_egg(id)
    latest_data = data.get('info.aqi')

    db.put_item(
        TableName='Kaiterra',
        Item=
        {
            'id': {
                'S': id_register
            },
            'deviceID': {
                'S': id
            },
            'humidity': {
                'N': str(latest_data['data'].get('humidity'))
            },
            'rco2': {
                'N': str(latest_data['data'].get('rco2 (ppm)'))
            },
            'temp': {
                'N': str(latest_data['data'].get('temp'))
            }
        }
    )
    print("Added item")
    return None

if __name__ == "__main__":
    check_available("requests")
    from datetime import datetime, timezone

    while True:
        summarize_laser_egg("dd85475c-a5ef-4a15-b00f-206e408528b2") #obtiene valores del Kaiterra con el ID
        putData("dd85475c-a5ef-4a15-b00f-206e408528b2")
        time.sleep(10)

