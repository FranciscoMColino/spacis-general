import asyncio
import json

TELEMETRY_UPDATE_PERIOD = 10
HEAT_THRESHOLD = 100
CONFORT_ZONE = 60

class TelemetryControl:
    def __init__(self):
        self.temperature = 0
        self.override_mode = False
        self.fans_on = False
        self.turn_off_fans(self)

    #add synchronization ?
    def get_temperature(self):
        return self.temperature

    #TODO
    async def read_temperature_sensor(self):
        self.temperature = 50
        return self.temperature

    #TODO
    async def turn_on_fans(self):
        self.fans_on = True
        return 0

    #TODO
    async def turn_off_fans(self):
        self.fans_on = False
        return 0
    
    async def log(self):
        print(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))
        asyncio.sleep(TELEMETRY_UPDATE_PERIOD)
        
    async def run(self):
        
        while True:
            temperature = await self.read_temperature_sensor()
            
            if not self.override_mode:
                if temperature > HEAT_THRESHOLD and not self.fans_on:
                    await self.turn_on_fans()
                elif temperature <= CONFORT_ZONE and self.fans_on:
                    await self.turn_off_fans()

            asyncio.sleep(TELEMETRY_UPDATE_PERIOD)