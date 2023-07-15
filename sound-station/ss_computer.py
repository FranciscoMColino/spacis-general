import asyncio
import tkinter as tk

from data_recording import DataRecorder
from ss_app import SSApp
from ss_client import SSClient
from ss_serial import TransmitterSerial


# Run the event loop
async def main():

    root = tk.Tk()

    serial_com = TransmitterSerial()
    res = serial_com.connect()

    # TODO - handle serial connection failure, put in logs
    if res:
        print("Connected to INO serial")
    else:
        print("Failed to connect to INO serial")
        return 
    
    data_recorder = DataRecorder()
    app = SSApp(root, serial_com, data_recorder)
    ws_client = SSClient(app, data_recorder)

    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())
    asyncio.create_task(app.update_spectogram_task())

    asyncio.create_task(serial_com.read_messages())
    asyncio.create_task(ws_client.run())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

asyncio.run(main())        