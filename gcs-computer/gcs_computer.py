import asyncio
import tkinter as tk

import data_recording
from gcs_app import GCSApp
from gcs_server import GCSServer


# Run the event loop
async def main():

    root = tk.Tk()
    #root.geometry("900x400")

    data_manager = data_recording.DataManager()

    server = GCSServer(data_manager)
    app = GCSApp(root, data_manager, server)
    
    server.setup(app)
    await server.start()
    
    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())
    asyncio.create_task(app.update_spectogram_task())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    

asyncio.run(main())