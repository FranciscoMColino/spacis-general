import asyncio
import json
import threading

import signal_management
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

# TODO exception handling
async def periodic_data_transfer():
    while True:
        await asyncio.sleep(1/1600)
        if websocket and signal_management.lock.acquire(False) and signal_management.recorded_signals:
            print("Sending data...")
            await websocket.send(json.dumps(signal_management.recorded_signals))
            print("Data sent: " + str(len(signal_management.recorded_signals)))
            signal_management.recorded_signals = [] # this is the 2nd cache
            signal_management.lock.release()
            await asyncio.sleep(1/10)
        

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

    #start thread running signal generator
    signal_management.serial_reading = True
    signal_management_thread = threading.Thread(target=signal_management.signal_generator)
    signal_management_thread.start()

    asyncio.ensure_future(websocket_client())
    asyncio.create_task(other_task())  # Run other_task concurrently
    asyncio.create_task(websocket_spammer())
    asyncio.create_task(periodic_data_transfer())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

    signal_management.kill_signal_generator()
    signal_management_thread.join()
        

asyncio.run(main())