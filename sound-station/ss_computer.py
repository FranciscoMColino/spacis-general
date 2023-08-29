import asyncio
import tkinter as tk

from app_models import DelayControl
from data_recording import DataRecorder
from delay_module import DelayModule
from gps_module import GpsModule
from spacis_utils import parse_settings
from ss_app import SSApp
from ss_client import SSClient
from ss_serial import TransmitterSerial


# Run the event loop
async def main():

    settings = parse_settings()

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
    delay_module = DelayModule()
    gps_module = GpsModule(delay_module)
    app = SSApp(root, serial_com, data_recorder, delay_module, gps_module)
    ws_client = SSClient(app, data_recorder, settings, gps_module)

    asyncio.create_task(app.run())
    
    asyncio.create_task(serial_com.read_messages())
    asyncio.create_task(ws_client.run())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

asyncio.run(main())        