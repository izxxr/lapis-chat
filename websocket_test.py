import aiohttp
import asyncio

TOKEN = "MeRyszyGrDYvd_FAlNaH4VrXaqIMZzmlh4fTKf9d1jM"

async def main():
    session = aiohttp.ClientSession()
    ws = await session.ws_connect("ws://localhost:8000/websocket/", params={"token": TOKEN})
    
    try:
        while True:
            data = await ws.receive_json()
            print(">", data)
    except KeyboardInterrupt:
        await ws.close()
        await session.close()

asyncio.run(main())

