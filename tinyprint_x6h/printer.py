from bleak import BleakClient, BleakError, BleakScanner
import logging

logger = logging.getLogger(__name__)

SUPPORTED_PRINTER_PREFIXES = ["x6h-", "X6h-"]
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0  # seconds

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
            logger.debug("Retrying connection (attempt %d of %d)", attempt, RETRY_ATTEMPTS)
            client = BleakClient(address)
            await client.connect()
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
    # TODO: Implement the print function
    logger.info("Sending data to device")
    logger.debug("Data: %s", data.hex())
