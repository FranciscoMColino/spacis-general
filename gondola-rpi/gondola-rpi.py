import asyncio

import websockets

websocket = None

async def other_task():
    while True:
        print("Performing other task...")
        await asyncio.sleep(5)

async def websocket_spammer():
    while True:
        if websocket:
            print("Spamming now...")
            await websocket.send("spam")
        await asyncio.sleep(5)

# deprecated
async def websocket_client():
    #connect to the server and keep open
    global websocket
    async with websockets.connect('ws://localhost:8080') as websocket:  
        print("WebSocket client started.")
        #send a message to the server
        await websocket.send("client-connect")
        #handle messages from the server
        # Receiving messages from the server
        while True:
            try:
                message = await websocket.recv()
                print(f'Received: {message}')
                # Handle messages accordingly

            except websockets.exceptions.ConnectionClosed:
                print('WebSocket connection closed by the server')
                break

async def main():
    #start a websockets client that connects to a server

    asyncio.ensure_future(websocket_client())
    asyncio.create_task(other_task())  # Run other_task concurrently
    asyncio.create_task(websocket_spammer())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

    

        

asyncio.run(main())