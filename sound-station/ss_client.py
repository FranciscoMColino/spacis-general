import asyncio
import json

import spacis_utils
import websockets

WS_CLIENT_WAIT_TIME = 1/100
WS_CLIENT_LONG_WAIT_TIME = 1/200
RECONNECT_WAIT_TIME = 5

class SSClient:
    def __init__(self, app, data_recorder, settings, gps_module):
        self.settings = settings
        self.websocket = None
        self.app = app
        self.gps_module = gps_module
        self.data_recorder = data_recorder
        self.url = "ws://" + settings["cloud_server_ip"] + ":" + str(settings["cloud_server_port"])

    async def run(self):
        while True:
            try:
                await self.connect()
                break
            except Exception as e:
                print("LOG: Exception in client ", e)
                await asyncio.sleep(RECONNECT_WAIT_TIME)
        print("LOG: Client starting to read from server")
        await self.read_from_server()

    async def connect(self):
        while True:
            try:
                print("LOG: Trying to connect to server")
                self.ws = await websockets.connect(self.url)
                print("LOG: Client reached server")
                await self.ws.send("sound-station-connect")
                print("LOG: Client connected to server")

                # TODO better client-server handshake
                
                break
            except ConnectionRefusedError:
                #print("LOG: Connection refused")
                await asyncio.sleep(WS_CLIENT_WAIT_TIME)
            except TimeoutError:
                print("LOG: Connection timed out")
                await asyncio.sleep(WS_CLIENT_LONG_WAIT_TIME)

    def message_handler(self, message):
        
        # convert message to json
        try:
            message = json.loads(message)

            # switch case for message type
            if message["type"] == "sensor_data":
                unpacked_data = spacis_utils.unpack_sensor_data(message['data'])
                #print(f"RECEIVED: sensor data {message['data']} with {len(unpacked_data)} samples")
                # TODO record data
                self.data_recorder.record_multiple_sensor_data(unpacked_data)
                print("RECEIVERD: unpacked data ", len(unpacked_data))

            elif message["type"] == "gps_data":
                data = message['data']
                self.gps_module.update_gps_data(data)
                print(f"RECEIVED: gps data {data}")
                self.data_recorder.record_gps_data([
                    data['lat'],
                    data['lon'],
                    data['alt'],
                    data['speed'],
                    data['climb'],
                    data['track'],
                    data['time'],
                    data['error']
                ])

            else:
                print("RECEIVED: invalid type {}, ignoring message".format(message["type"]))

        except json.decoder.JSONDecodeError:
            print("RECEIVED: invalid message format (not JSON)")

    async def read_from_server(self):
            
        #handle messages from the server
        # Receiving messages from the server
        while True:
            try:
                message = await self.ws.recv()
                print(f'RECEIVED: {message[:20]}')

                # handle the message
                self.message_handler(message)

                asyncio.sleep(WS_CLIENT_WAIT_TIME)

            except websockets.exceptions.ConnectionClosedError as e:
                print("LOG: Connection closed by server ", e)

                self.ws = None

                await self.connect()

            except Exception as e:
                print("LOG: Exception while reading from server ", e)

                self.ws = None

                await asyncio.sleep(RECONNECT_WAIT_TIME)

        
