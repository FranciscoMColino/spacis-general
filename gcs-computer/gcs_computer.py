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

    app = GCSApp(root, data_manager)
    server = GCSServer(app, data_manager)

    await server.start()
    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())

    while True:
        try:
            print("Main loop")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    

asyncio.run(main())