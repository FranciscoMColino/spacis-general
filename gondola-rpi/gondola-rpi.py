import asyncio
import json
import signal
import sys
import threading

import signal_management
import spacis_utils
import websockets

websocket = None

async def other_task():
    while True:
        print("TASK: other task...")
        await asyncio.sleep(5)

async def websocket_spammer():
    while True:
        if websocket:
            print("TASK: Spamming now...")
            await websocket.send("spam")
        await asyncio.sleep(5)

# TODO exception handling
async def periodic_data_transfer():
    while True:
        await asyncio.sleep(1/1600)
        if websocket and signal_management.lock.acquire(False) and signal_management.recorded_signals:
            # TODO replace prints with a proper logger
            print(f"SENDING: Sensor data w/ {len(signal_management.recorded_signals)} samples")
            message = {}
            message["type"] = "sensor_data"
            message["data"] = spacis_utils.pack_sequence(signal_management.recorded_signals)
            await websocket.send(json.dumps(message))
            signal_management.recorded_signals = [] # this is the 2nd cache
            signal_management.lock.release()
            await asyncio.sleep(1/10)

# deprecated
async def websocket_client():
    #connect to the server and keep open
    global websocket
    async with websockets.connect('ws://localhost:8080') as websocket:  
        print("CLIENT STARTED")
        #send a message to the server
        await websocket.send("client-connect")
        #handle messages from the server
        # Receiving messages from the server
        while True:
            try:
                message = await websocket.recv()
                print(f'RECEIVED: {message}')
                # Handle messages accordingly

            except websockets.exceptions.ConnectionClosed:
                print('WebSocket connection closed by the server')
                break

# Define a handler function for KeyboardInterrupt
def interrupt_handler(signal, frame):
    print("KeyboardInterrupt caught. Exiting gracefully...")
    signal_management.kill_signal_generator()
    signal_management_thread.join()
    sys.exit(0)

async def main():
    # Register the handler for KeyboardInterrupt
    signal.signal(signal.SIGINT, interrupt_handler)

    #start thread running signal generator
    signal_management.serial_reading = True
    global signal_management_thread
    signal_management_thread = threading.Thread(target=signal_management.signal_generator)
    signal_management_thread.start()

    asyncio.ensure_future(websocket_client())
    test = asyncio.create_task(other_task())  # Run other_task concurrently
    asyncio.create_task(websocket_spammer())
    asyncio.create_task(periodic_data_transfer())

    while True:
        await asyncio.sleep(1)
        

asyncio.run(main())