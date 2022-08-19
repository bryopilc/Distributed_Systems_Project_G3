#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Grupo 3 - Sistemas Distribuidos

from datetime import datetime, timezone
import sys
import requests
import time

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


if __name__ == "__main__":
    check_available("requests")
    from datetime import datetime, timezone
    while True:
        summarize_laser_egg("dd85475c-a5ef-4a15-b00f-206e408528b2") #obtiene valores del Kaiterra con el ID
        time.sleep(10)
