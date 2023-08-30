import asyncio
import functools
import signal
import sys
import tkinter as tk

from data_recording import DataRecorder
from gcs_app import GCSApp
from gcs_client import GCSClient
from gcs_server import GCSServer
from performance_recordings import PerformanceRecordings
from spacis_utils import parse_settings


def signal_handler(sig, frame, data_record):
    print('You pressed Ctrl+C! Exiting gracefully...')
    data_record.stop()
    sys.exit(0)

# Run the event loop
async def main():

    settings = parse_settings()

    root = tk.Tk()

    performance_recordings = PerformanceRecordings()
    data_record = DataRecorder()
    client = GCSClient(settings)
    server = GCSServer(data_record, client, settings)
    app = GCSApp(root, data_record, server, performance_recordings)

    signal.signal(signal.SIGINT, functools.partial(signal_handler, data_record=data_record))
    
    server.setup(app)
    await server.start()

    asyncio.create_task(server.periodic_heartbeat())

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