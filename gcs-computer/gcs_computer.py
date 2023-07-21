import asyncio
import functools
import signal
import sys
import tkinter as tk

from data_recording import DataRecorder
from gcs_app import GCSApp
from gcs_client import GCSClient
from gcs_server import GCSServer


def signal_handler(sig, frame, data_record):
    print('You pressed Ctrl+C! Exiting gracefully...')
    data_record.stop()
    sys.exit(0)

# Run the event loop
async def main():

    root = tk.Tk()
    #root.geometry("900x400")

    data_record = DataRecorder()
    client = GCSClient()
    server = GCSServer(data_record, client)
    app = GCSApp(root, data_record, server)

    signal.signal(signal.SIGINT, functools.partial(signal_handler, data_record=data_record))
    
    server.setup(app)
    await server.start()
    
    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())
    asyncio.create_task(app.update_spectogram_task())

    asyncio.create_task(client.connect())
    asyncio.create_task(client.periodic_dispatch())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    

asyncio.run(main())