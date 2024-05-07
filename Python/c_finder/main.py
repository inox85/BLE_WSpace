from CFinderClass import CFinderClass
import asyncio

cfinder= CFinderClass("Galaxy Watch4")

loop = asyncio.get_event_loop()

loop.run_until_complete(cfinder.start_to_find_threat())


