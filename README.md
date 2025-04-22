# tinyprint-x6h

Python API for the [X6h thermal printer](./docs/media/printer.jpg) over BLE, compatible with the TinyPrint app.

## Install

```sh
pip install tinyprint-x6h
```

## Example

```py
import asyncio
from tinyprint_x6h import printer

async def main():
  client = await printer.connect()  # or with address — printer.connect("XX:XX:XX:XX:XX:XX")
  await printer.print(client, bytes([0xFF] * 384 * 48))
  await printer.disconnect(client)

asyncio.run(main())
```

Since no address is passed to `connect()`, the library automatically scans for nearby BLE devices and connects to the first one whose name starts with `X6h-` or `x6h-`.

The `print()` function accepts a `bytes` object, where **each byte represents one pixel** encoded with 16 levels of grayscale. The printer uses only the upper 4 bits of each byte (`byte >> 4`) to determine the pixel value. This means `0x00` is white, `0xF0` or `0xFF` is black, and intermediate values produce shades of gray. The total number of bytes **must be divisible by 384**, which is the number of pixels per row. In this example, `384 * 48` bytes represent an image 48 lines tall and 384 pixels wide, filled entirely with black.

[More examples](./examples/)
