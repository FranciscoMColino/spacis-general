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

    data_recorder = DataRecorder()
    delay_module = DelayModule(settings)
    gps_module = GpsModule(delay_module)

    serial_com = TransmitterSerial(data_recorder, delay_module, settings)
    
    if serial_com.connect():
        print("Connected to INO serial")
    else:
        print("Failed to connect to INO serial")
        return
    
    
    app = SSApp(root, serial_com, data_recorder, delay_module, gps_module)
    ws_client = SSClient(app, data_recorder, settings, gps_module)

    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())
    asyncio.create_task(app.update_spectogram_task())
    asyncio.create_task(delay_module.calculate_delays())
    asyncio.create_task(serial_com.read_messages())
    asyncio.create_task(serial_com.periodic_send_delays())
    asyncio.create_task(ws_client.run())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

asyncio.run(main())        