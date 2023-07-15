import asyncio
import tkinter as tk

import data_recording
from gcs_app import GCSApp
from gcs_client import GCSClient
from gcs_server import GCSServer


# Run the event loop
async def main():

    root = tk.Tk()
    #root.geometry("900x400")

    data_record = data_recording.DataRecorder()

    client = GCSClient()
    server = GCSServer(data_record, client)
    app = GCSApp(root, data_record, server)
    
    
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