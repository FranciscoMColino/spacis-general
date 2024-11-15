import asyncio
import enum
import json
import time

import data_recording
import spacis_utils
import websockets

HEART_BEAT_INTERVAL = 1

SAMPLE_FREQ_SIZE = 5
GATHER_PERIOD = 1/4


class Client:
    def __init__(self):
        self.connected = False
        self.last_update = ""
        self.websocket = None


class GCSServer:
    def __init__(self, data_recorder, spacis_server_client, settings):
        self.client_websocket = None
        self.settings = settings
        self.port = settings['gcs_server_port']
        self.server = None
        self.data_recorder = data_recorder
        self.client = Client()
        self.spacis_server_client = spacis_server_client
        self.current_batch_id = 0
        self.last_few_batch_size = []
        self.average_batch_freq = 0

    def setup(self, app):
        self.app = app

    async def start(self):
        self.server = await websockets.serve(self.websocket_handler, self.settings['gcs_server_ip'], self.port)

    def received_message_handler(self, message):
        # convert message to json
        try:
            message = json.loads(message)

            # print(f"RECEIVED: message of type {message['type']}")

            # switch case for message type
            if message["type"] == "sensor_data":
                unpacked_data = spacis_utils.unpack_sensor_data(
                    message['data']['sensor_read'])
                unpacked_elapsed = spacis_utils.unpack_elapsed_time(
                    message['data']['elapsed_time'])
                unpacked_pps_ids = spacis_utils.unpack_pps_ids(
                    message['data']['pps_id'])

                if len(self.last_few_batch_size) >= SAMPLE_FREQ_SIZE:
                    self.last_few_batch_size.pop(0)
                    self.last_few_batch_size.append(len(unpacked_data))
                else:
                    self.last_few_batch_size.append(len(unpacked_data))

                self.average_batch_freq = sum(
                    self.last_few_batch_size) / (GATHER_PERIOD*SAMPLE_FREQ_SIZE)

                self.data_recorder.record_multiple_sensor_data(
                    unpacked_data, unpacked_elapsed, unpacked_pps_ids, self.current_batch_id)

                self.data_recorder.record_batch_data(
                    self.current_batch_id, len(unpacked_data))

                self.app.update_data(unpacked_data)
                # print("RECEIVERD: unpacked data ", unpacked_data)
                if self.spacis_server_client.connected:
                    new_message = {
                        "type": "sensor_data",
                        "data": message['data']['sensor_read'],
                    }
                    self.spacis_server_client.add_message(new_message)

                self.current_batch_id += 1

            elif message["type"] == "temperature_status":
                data = message['data']
                self.app.set_temperature_status(data)
                self.data_recorder.record_temperature_data([
                    data['box_temperature'],
                    data['cpu_temperature']]
                )

            elif message["type"] == "system_control_data":
                data = message['data']
                self.app.set_system_control_data(data)

            elif message["type"] == "gps_data":
                data = message['data']
                self.app.set_gps_status(data)
                if self.spacis_server_client.connected:
                    self.spacis_server_client.add_message(message)
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

            elif message["type"] == "pps_data":
                # print("RECEIVED: pps data")

                self.data_recorder.record_pps_data(message['data'])
            else:
                print("RECEIVED: invalid type, {}".format(message["type"]))
        except json.decoder.JSONDecodeError:
            print("RECEIVED: invalid message format (not JSON)")
        except Exception as e:
            print(
                "RECEIVED: error processing message: {} on message {}".format(e, message))

        if self.client.connected:
            # last update time as str with date
            self.client.last_update = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())

    def send_message(self, message):
        if self.client.websocket:
            asyncio.create_task(self.client.websocket.send(message))

    def send_hearbeat(self):
        obj = {
            "type": "heartbeat",
            "data": {
                "last_update": self.client.last_update
            }
        }
        self.send_message(json.dumps(obj))

    async def periodic_heartbeat(self):
        while True:
            # Send heartbeat to client every 5 seconds
            await asyncio.sleep(HEART_BEAT_INTERVAL)
            try:
                if self.client:
                    self.send_hearbeat()
            except Exception as e:
                print(f"ERROR: Failed to send heartbeat: {e}")

    async def websocket_handler(self, websocket):
        try:
            async for message in websocket:
                # Handle messages accordingly

                if message == "client-connect":
                    self.client.connected = True
                    self.client.websocket = websocket
                    self.send_hearbeat()
                    print("LOG: Client connected")
                    continue
                # elif self.client.connected and websocket != self.client.websocket:
                #    print("LOG: Client already connected")
                # update app server state to connected and timestamp

                # TODO if json format is correct
                self.received_message_handler(message)

        except Exception as e:
            # Handle the exception or log it as needed
            print(f"ERROR: WebSocket connection error: {e}")
            self.client.connected = False
            self.client.websocket = None

        finally:
            # Client disconnected
            self.client.connected = False
            self.client.websocket = None
            print("LOG: Client disconnected")
