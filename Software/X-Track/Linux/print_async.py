#!/usr/bin/env python3

import aioesphomeapi
import asyncio
import socket
import json


async def main():
    loop = asyncio.get_running_loop()
    cli = aioesphomeapi.APIClient("fufoemborra.local", 6053, "")

    await cli.connect(login=True)

    list = {}

    def convert_to_serializable(obj):
            if isinstance(obj, aioesphomeapi.LightInfo):
                # Conve rtir el objeto LightInfo a un diccionario serializable
                return {
                    "type": "LightInfo",
                    "state": {
                        "object_id": obj.object_id,
                        "key": obj.key,
                        "name": obj.name,
                        "unique_id": obj.unique_id,
                        "supported_color_modes": obj.supported_color_modes,
                        "min_mireds": obj.min_mireds,
                        "effects": obj.effects,
                        "disabled_by_default": obj.disabled_by_default,
                        "icon": obj.icon,
                        "entity_category": obj.entity_category,
                        "legacy_supports_brightness": obj.legacy_supports_brightness,
                        "legacy_supports_rgb": obj.legacy_supports_brightness,
                        "legacy_supports_white_value": obj.legacy_supports_white_value,
                        "legacy_supports_color_temperature": obj.legacy_supports_color_temperature,
                    }
                }
            elif isinstance(obj, aioesphomeapi.SwitchInfo):
                return {
                    "type": "SwitchInfo",
                    "state": {
                        "object_id": obj.object_id,
                        "key": obj.key,
                        "name": obj.name,
                        "unique_id": obj.unique_id,
                        "icon": obj.icon,
                        "assumed_state": obj.assumed_state,
                        "disabled_by_default": obj.disabled_by_default,
                        "entity_category": obj.entity_category,
                        "device_class": obj.device_class,
                    }
                }
            elif isinstance(obj, aioesphomeapi.SensorInfo):
                return {
                    "type": "SensorInfo",
                    "state": {
                        "object_id": obj.key,
                        "key": obj.key,
                        "name": obj.name,
                        "unique_id": obj.unique_id,
                        "icon": obj.icon,
                        "unit_of_measurement": obj.unit_of_measurement,
                        "accuracy_decimals": obj.accuracy_decimals,
                        "force_update": obj.force_update,
                        "device_class": obj.device_class,
                        "state_class": obj.state_class,
                        "disabled_by_default": obj.disabled_by_default,
                        "entity_category": obj.entity_category,
                    }
                }
            elif isinstance(obj, aioesphomeapi.LightState):
                return {
                    "type": "LightState",
                    "key": obj.key,
                    "name": list[obj.key],
                    "state": obj.state,
                    "brightness": obj.brightness,
                    "color_mode": obj.color_mode,
                    "color_brightness": obj.color_brightness,
                    "red": obj.red,
                    "green": obj.green,
                    "blue": obj.blue,
                    "white": obj.white,
                    "color_temperature": obj.color_temperature,
                    "cold_white": obj.cold_white,
                    "warm_white": obj.warm_white,
                    "effect": obj.effect,
                }
            elif isinstance(obj, aioesphomeapi.SensorState):
                return {
                    "type": "SensorState",
                    "key": obj.key, #fixed32 key = 1;
                    "name": list[obj.key],
                    "state": obj.state, #float state = 2;
                    "missing_state": obj.missing_state, #bool missing_state = 3;
                }
            elif isinstance(obj, aioesphomeapi.SwitchState):
                return {
                    "type": "SwitchState",
                    "key": obj.key, #fixed32 key = 1;
                    "name": list[obj.key],
                    "state": obj.state #bool state = 2;
                }
            # Puedes agregar más casos según los tipos de objetos que necesites manejar
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def cb(state):
        #if type(state) == aioesphomeapi.BinarySensorState:
        try:
            print(state)
            #if isinstance(state, aioesphomeapi.LightState):
            serialized_state = convert_to_serializable(state)
            json_message = json.dumps(serialized_state)
            connection.sendall(json_message.encode('utf-8') + b'\n')
        except Exception as e:
            print(f"Error en el callback de cambio de estado: {e}")

    

    l = await cli.list_entities_services()
    for entity in l:
        for ent in entity:
            list[ent.key] = ent.name

    print (list)           


    print(f'Creando socket')

    # Crear un socket para la comunicación con el programa en C
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 12345))
    server.listen()

    # Aceptar la conexión
    connection, address = server.accept()
    print(f'Conexión establecida desde {address}')


    await cli.subscribe_states(cb)

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()
    