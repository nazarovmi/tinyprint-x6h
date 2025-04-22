import asyncio
import logging
from tinyprint_x6h import printer
import sys

logging.basicConfig(level=logging.ERROR)
logging.getLogger("tinyprint_x6h").setLevel(logging.DEBUG)

def generate_checkered_pattern(width: int = 384, height: int = 48, cell_size: int = 16) -> bytes:
    data = bytearray()

    for y in range(height):
        for x in range(width):
            if ((x // cell_size) + (y // cell_size)) % 2 == 0:
                ratio = x / (width - 1)
                color = int((1 - ratio) * 0xff)
                data.append(color)
            else:
                data.append(0x00)

    return bytes(data)

async def main():
    client = await printer.connect()
    await printer.print(client, generate_checkered_pattern())
    await printer.disconnect(client)

if __name__ == "__main__":
    asyncio.run(main())
