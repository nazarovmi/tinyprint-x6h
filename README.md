# tinyprint-x6h

Python API for the X6h thermal printer over BLE, compatible with the TinyPrint app.

## Install

```sh
pip install tinyprint-x6h
```

## Example

```py
from tinyprint_x6h import printer

client = printer.connect() # or with address — printer.connect("XX:XX:XX:XX:XX:XX")
printer.print(client, bytes([0xff] & 384))
printer.disconnect(client)
```
