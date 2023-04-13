import asyncio
import json

import spacis_utils
import websockets

client_websocket = None

# TODO reply to messages from the client
def received_message_handler(message):
    # convert message to json
    try:
        message = json.loads(message)

        # switch case for message type
        if message["type"] == "sensor_data":
            unpacked_data = spacis_utils.unpack_sensor_data(message['data'])
            print(f"RECEIVED: sensor data {message['data']} with {len(unpacked_data)} samples")
            # TODO save sensor data to a file
            # TODO update sensor data buffer for the correlation analysis
        else:
            print("RECEIVED: invalid type")
    except json.decoder.JSONDecodeError:
        print("RECEIVED: invalid message format (not JSON)")
        

# Define a coroutine that handles incoming WebSocket messages
async def websocket_handler(websocket, path):
    async for message in websocket:

        # TODO better way to handle this
        # confirm connection to client and save the websocket
        if message == "client-connect":
            global client_websocket
            client_websocket = websocket
            print("RECEIVED: {message}")
            continue
        
        # Handle messages accordingly
        received_message_handler(message)
        

# Define a coroutine that performs other tasks concurrently
async def other_task():
    while True:
        #print("Performing other task...")
        await asyncio.sleep(1)

# Start the server
async def start_server():
    server = await websockets.serve(websocket_handler, 'localhost', 8080)
    print("WebSocket server started.")
    return server

# Stop the server
async def stop_server(server):
    server.close()
    await server.wait_closed()
    print("WebSocket server stopped.")

#task that prints terminal input
# TODO this will be the command reader of the GUI
async def terminal_input():
    while True:
        user_input = await asyncio.to_thread(input, "Enter input: ")
        if client_websocket is not None:
            await client_websocket.send(user_input)
        else:
            print("No client connected.")

# Run the event loop
async def main():
    server = await start_server()
    other_task_handle = asyncio.create_task(terminal_input())  # Run other_task concurrently

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

    await stop_server(server)
    other_task_handle.cancel()

asyncio.run(main())