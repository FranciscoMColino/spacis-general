import asyncio
import json
import time

import websockets

HOST = "16.16.139.172"
PORT = 8765

ON_DISPATCH_INTERVAL = 1/100
NO_ACTIVITY_INTERVAL = 1

WS_CLIENT_WAIT_TIME = 5

class GCSClient:
    def __init__(self, settings):
        self.message_buffer = []
        self.settings = settings
        self.url = f"ws://{settings.cloud_server_ip}:{settings.cloud_server_port}"
        self.ws = None
        
    async def periodic_dispatch(self):
        start = time.time()
        
        while True:
            print("PERIODIC_DISPATCH: Starting, elapsed time from last exec {}".format(time.time() - start))
            start = time.time()
            print("LOG: Periodic dispatch")
            if self.ws is not None and self.ws.open:
                print("LOG: Dispatching message")
                if len(self.message_buffer) > 0:
                    message = {
                        "user": "ground-control-station",
                        "content": self.message_buffer.pop(0)
                    }

                    await self.ws.send(json.dumps(message))
                    print("PERIODIC_DISPATCH: Finished, elapsed time {}".format(time.time() - start))
                    start = time.time()
                    await asyncio.sleep(ON_DISPATCH_INTERVAL)
                    continue
            else:
                print("LOG: No connection, {}".format(self.ws.open if self.ws is not None else "None"))
                print("LOG: Trying to connect")
                await self.connect()
            print("PERIODIC_DISPATCH: Finished, elapsed time {}".format(time.time() - start))
            start = time.time()
            await asyncio.sleep(NO_ACTIVITY_INTERVAL)
    
    def add_message(self, message):
        self.message_buffer.append(message)

    async def connect(self):
        while True:
            try:
                self.ws = await websockets.connect(self.url)
                print("LOG: Client started")
                await self.ws.send("ground-control-station-connect")
                print("LOG: Client connected to server")

                # TODO better client-server handshake

                break
            except ConnectionRefusedError:
                #print("LOG: Connection refused")
                await asyncio.sleep(WS_CLIENT_WAIT_TIME)