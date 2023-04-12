import asyncio

# serial mocks

async def mock_serial_signal_transmittion():
    
    while True:
        asyncio.sleep(1/1600)

# end

recorded_signals = []

async def read_and_record_from_serial():

    return

async def run():
    asyncio.create_task(mock_serial_signal_transmittion())

    # establish connection with serial port

    asyncio.create_task(read_and_record_from_serial())
    
asyncio.run(run())



