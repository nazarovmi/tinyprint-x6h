import asyncio
from bleak import BleakClient, BleakError, BleakScanner
import logging
import math

from .protocol import create_print_commands

logger = logging.getLogger(__name__)

SUPPORTED_PRINTER_PREFIXES = ["x6h-", "X6h-"]
UUID_WRITE = "0000ae01-0000-1000-8000-00805f9b34fb"
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0  # seconds
PACKET_SIZE = 20
PACKET_DELAY = 4 / 1000  # seconds

async def find_printer_device():
    logger.info("Scanning for devices")
    devices = await BleakScanner.discover(timeout=5.0)
    logger.debug("Found %d devices", len(devices))

    for d in devices:
        name = d.name or ""
        logger.debug("Looking at device: %s (%s)", name, d.address)
        if any(name.startswith(prefix) for prefix in SUPPORTED_PRINTER_PREFIXES):
            logger.info("Discovered printer device: %s (%s)", name, d.address)
            return d.address

    logger.error("Failed to find a supported printer device nearby")
    raise RuntimeError("Could not found available devices nearby")

async def connect(address: str | None = None) -> BleakClient:
    if not address:
        address = await find_printer_device()

    logger.info("Connecting to %s", address)
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            logger.debug("Retrying connection (%d/%d)", attempt, RETRY_ATTEMPTS)
            client = BleakClient(address)
            await client.connect()
            logger.info("Connected to %s", address)
            return client
        except BleakError as e:
            logger.warning("Connection failed: %s", e)
            if attempt < RETRY_ATTEMPTS:
                await asyncio.sleep(RETRY_DELAY)

    logger.error("Failed to connect to %s after multiple attempts", address)
    raise RuntimeError("Could not connect to device")

async def disconnect(client: BleakClient):
    logger.info("Disconnecting from %s", client.address)
    await client.disconnect()

async def print(client: BleakClient, data: bytes):
    if not client.is_connected:
        logger.error("Printer is not connected")
        raise RuntimeError("Printer is not connected")

    logger.info("Starting print job")

    commands = create_print_commands(data)
    logger.debug("Hex data: %s", commands.hex(" "))

    for i in range(0, len(commands), PACKET_SIZE):
        chunk = commands[i:i + PACKET_SIZE]
        logger.debug("Writing bytes (%d:%d/%d): %s", i, i + PACKET_SIZE, len(commands), chunk.hex(" "))
        await client.write_gatt_char(UUID_WRITE, chunk, response=False)
        await asyncio.sleep(PACKET_DELAY)

    logger.info("Print job completed")
