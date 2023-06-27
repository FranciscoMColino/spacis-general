import asyncio
import enum
import json

import data_recording
import spacis_utils
import websockets


# Using enum class create enumerations
class ServerStatus(enum.Enum):
    INIT = 0
    WAITING_FOR_CLIENT = 'Waiting for client...'
    CONNECTED = 'Connected'
    DISCONNECTED = 'Disconnected'

class GCSServer:
    def __init__(self, data_recorder):
        self.client_websocket = None
        #self.state = ServerState.WAITING_FOR_CLIENT
        self.port = 8080
        self.server = None
        self.data_recorder = data_recorder

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
        async for message in websocket:

            # confirm connection to client and save the websocket
            if message == "client-connect":
                self.app.update_server_status(ServerStatus.CONNECTED)
                self.client_websocket = websocket
                # update app server state to connected and timestamp
                continue

            # Handle messages accordingly
            self.received_message_handler(message)

        # client disconnected
        self.client_websocket = None
        self.app.update_server_status(ServerStatus.DISCONNECTED)