from CFinderClass import CFinderClass
import asyncio
from server import ServerThread

c_finder= CFinderClass("Galaxy Watch4")

loop = asyncio.get_event_loop()

server_thread = ServerThread('0.0.0.0', 5005, c_finder)
server_thread.start()

loop.run_until_complete(c_finder.start_to_find_threat())
