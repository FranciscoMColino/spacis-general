import asyncio
import tkinter as tk

from gcs_app import GCSApp
from gcs_server import GCSServer


# Run the event loop
async def main():

    global root
    root = tk.Tk()
    root.geometry("400x400")

    app = GCSApp(root)
    server = GCSServer(app)

    await server.start()
    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    

asyncio.run(main())