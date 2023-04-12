import asyncio

import websockets

client_websocket = None

# Define a coroutine that handles incoming WebSocket messages
async def websocket_handler(websocket, path):
    async for message in websocket:
        # Process the incoming message
        print(f"Received: {message}")
        await websocket.send(f"You said: {message}")
        if message == "client-connect":
            global client_websocket
            client_websocket = websocket

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