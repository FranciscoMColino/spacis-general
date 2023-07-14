import asyncio
import json

import websockets

HOST = "16.16.139.172"
PORT = 8765

ON_DISPATCH_INTERVAL = 1/100
NO_ACTIVITY_INTERVAL = 1

WS_CLIENT_WAIT_TIME = 5

# TODO dispatcher should maybe be a separate class?

class GCSClient:
    def __init__(self):
        self.message_buffer = []
        self.url = f"ws://{HOST}:{PORT}"
        self.ws = None

    async def periodic_dispatch(self):
        while True:
            if self.ws is not None and self.ws.open:
                if len(self.message_buffer) > 0:
                    message = {
                        "user": "ground-control-station",
                        "content": self.message_buffer.pop(0)
                    }

                    await self.ws.send(json.dumps(message))
                    await asyncio.sleep(ON_DISPATCH_INTERVAL)
                    continue
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