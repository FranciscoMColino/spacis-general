import asyncio
import enum
import json

import data_recording
import spacis_utils
import websockets


# Using enum class create enumerations
class ServerState(enum.Enum):
    INIT = 0
    WAITING_FOR_CLIENT = 1
    CONNECTED = 2
    CONNECTION_LOST = 3

class GCSServer:
    def __init__(self, app):
        self.client_websocket = None
        #self.state = ServerState.WAITING_FOR_CLIENT
        self.app = app
        self.port = 8080
        self.server = None

    async def start(self):
        self.server = await websockets.serve(self.websocket_handler, 'localhost', self.port)

    def received_message_handler(self, message):
        # convert message to json
        try:
            message = json.loads(message)

            # switch case for message type
            if message["type"] == "sensor_data":
                unpacked_data = spacis_utils.unpack_sensor_data(message['data'])
                print(f"RECEIVED: sensor data {message['data']} with {len(unpacked_data)} samples")
                # data_recorder.record_data(unpacked_data) # TODO better saves
                
                # TODO update sensor data buffer for the correlation analysis
            else:
                print("RECEIVED: invalid type")
        except json.decoder.JSONDecodeError:
            print("RECEIVED: invalid message format (not JSON)")

    async def websocket_handler(self, websocket):
        async for message in websocket:

            # confirm connection to client and save the websocket
            if message == "client-connect":
                self.client_websocket = websocket
                # update app server state to connected and timestamp
                continue

            # Handle messages accordingly
            self.received_message_handler(message)

        print()