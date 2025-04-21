import asyncio
import logging
from tinyprint_x6h import printer
import sys

logging.basicConfig(level=logging.ERROR)
logging.getLogger("tinyprint_x6h").setLevel(logging.DEBUG)

async def main():
    client = await printer.connect()
    await printer.disconnect(client)

if __name__ == "__main__":
    asyncio.run(main())
