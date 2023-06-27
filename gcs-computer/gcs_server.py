import asyncio
import enum
import json

import data_recording
import spacis_utils
import websockets


class ClientState:
    def __init__(self):
        self.connected = False
        self.last_update = None
        self.websocket = None

class GCSServer:
    def __init__(self, data_recorder):
        self.client_websocket = None
        #self.state = ServerState.WAITING_FOR_CLIENT
        self.port = 8080
        self.server = None
        self.data_recorder = data_recorder
        self.client = ClientState()

    def setup(self, app):
        self.app = app

    async def start(self):
        self.server = await websockets.serve(self.websocket_handler, 'localhost', self.port)

    def received_message_handler(self, message):
        # convert message to json
        try:
            message = json.loads(message)

            # switch case for message type
            if message["type"] == "sensor_data":
                unpacked_data = spacis_utils.unpack_sensor_data(message['data'])
                #print(f"RECEIVED: sensor data {message['data']} with {len(unpacked_data)} samples")
                self.data_recorder.record_data(unpacked_data) # TODO better saves
                self.app.update_data(message['data'])
                # TODO update sensor data buffer for the correlation analysis
            
            elif message["type"] == "temperature_status":
                data = message['data']
                self.app.set_temperature_status(data)
                
            else:
                print("RECEIVED: invalid type")
        except json.decoder.JSONDecodeError:
            print("RECEIVED: invalid message format (not JSON)")

    def send_message(self, message):
        if self.client_websocket:
            asyncio.create_task(self.client_websocket.send(message))

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