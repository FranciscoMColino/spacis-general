import asyncio

import websockets


#handle messages from a websocket server as a client
async def websocket_handler(websocket, path):
    async for message in websocket:
        # Process the incoming message
        print(f"You said: {message}")



async def main():
    #etart a websockets client that connects to a server
    async with websockets.connect('ws://localhost:8080') as websocket:
        print("WebSocket client started.")
        #send a message to the server
        await websocket.send("client-connect")
        #handle messages from the server
        await websocket_handler(websocket, "")
        

asyncio.run(main())