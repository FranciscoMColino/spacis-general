import asyncio
import tkinter as tk

from ss_app import SSApp
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
    
    app = SSApp(root, serial_com)

    asyncio.create_task(app.run())
    asyncio.create_task(serial_com.read_messages())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

asyncio.run(main())        