import asyncio
import enum
import json
import time

import websockets

import data_recording
import spacis_utils


class Client:
    def __init__(self):
        self.connected = False
        self.last_update = ""
        self.websocket = None

class GCSServer:
    def __init__(self, data_recorder, spacis_server_client):
        self.client_websocket = None
        #self.state = ServerState.WAITING_FOR_CLIENT
        self.port = 8080
        self.server = None
        self.data_recorder = data_recorder
        self.client = Client()
        self.spacis_server_client = spacis_server_client

    def setup(self, app):
        self.app = app

    async def start(self):
        self.server = await websockets.serve(self.websocket_handler, '192.168.137.1', self.port)

    def received_message_handler(self, message):
        # convert message to json
        try:
            message = json.loads(message)

            # switch case for message type
            if message["type"] == "sensor_data":
                unpacked_data = spacis_utils.unpack_sensor_data(message['data'])
                #print(f"RECEIVED: sensor data {message['data']} with {len(unpacked_data)} samples")
                self.data_recorder.record_data(unpacked_data) # TODO better saves
                self.app.update_data(unpacked_data)
                # print("RECEIVERD: unpacked data ", unpacked_data)
                self.spacis_server_client.add_message(message)
            
            elif message["type"] == "temperature_status":
                data = message['data']
                self.app.set_temperature_status(data)

            elif message["type"] == "system_control_data":
                data = message['data']
                self.app.set_system_control_data(data)

            elif message["type"] == "gps_data":
                data = message['data']
                self.app.set_gps_status(data)
                print(f"RECEIVED: gps data {data}")
                self.spacis_server_client.add_message(message)

            else:
                print("RECEIVED: invalid type, {}".format(message["type"]))
        except json.decoder.JSONDecodeError:
            print("RECEIVED: invalid message format (not JSON)")

        if self.client.connected:
            # last update time as str with date
            self.client.last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def send_message(self, message):
        if self.client.websocket:
            asyncio.create_task(self.client.websocket.send(message))

    async def websocket_handler(self, websocket):
        try:
            async for message in websocket:
                # Handle messages accordingly

                if message == "client-connect" and not self.client.connected:
                    self.client.connected = True
                    self.client.websocket = websocket
                    print("LOG: Client connected")
                    continue
                elif self.client.connected and websocket != self.client.websocket:
                    print("LOG: Client already connected")
                # update app server state to connected and timestamp
                
                # TODO if json format is correct
                self.received_message_handler(message)


        except Exception as e:
            # Handle the exception or log it as needed
            print(f"ERROR: WebSocket connection error: {e}")

        finally:
            # Client disconnected
            self.client.connected = False
            self.client.websocket = None
            print("LOG: Client disconnected")