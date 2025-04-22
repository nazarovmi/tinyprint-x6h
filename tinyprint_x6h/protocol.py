import lzo
import struct

from .encoding import crc8

PAPER_WIDTH = 384
BLOCK_LINES = 20
GAP_LINES = 64

def create_command(command_id: int, payload: bytes) -> bytes:
    command = bytearray()
    command.extend([0x51, 0x78, command_id, 0x00])  # Header
    command.extend(struct.pack('<H', len(payload)))  # Payload length as two bytes in little-endian
    command.extend(payload)
    command.append(crc8(command, 6, len(payload)))  # Payload checksum
    command.append(0xFF)  # Final byte

    return bytes(command)

def create_feed_paper_command(lines: int) -> bytes:
    # Two bytes value in little-endian
    payload = struct.pack("<H", lines)

    return create_command(0xA1, payload)

def create_print_lines_command(data: bytes) -> bytes:
    # Compress data using LZO
    compressed = lzo.compress(data, 1, False)
    # Pack length of original and compressed data, and compressed data into payload
    payload = struct.pack('<HH', len(data), len(compressed)) + compressed

    return create_command(0xCF, payload)

def create_print_lines_commands(data: bytes, line_len: int, block_lines: int) -> bytes:
    total_len = len(data)
    block_len = line_len * block_lines

    if total_len % line_len != 0:
        raise ValueError(f"Printing data length must be a multiple of line len ({line_len})")

    # Add padding to prevent print artifacts like dark lines at the start
    prepared = bytes([0x00] * line_len) + data
    commands = bytearray()

    for block_start in range(0, total_len, block_len):
        block_end = block_start + block_len
        block = prepared[block_start:block_end]
        packed = bytearray()

        # Pack two pixels into one byte
        for i in range(0, len(block), 2):
            p0 = block[i]
            p1 = block[i + 1] if i + 1 < len(block) else 0
            packed.append((p0 >> 4) << 4 | (p1 >> 4))

        commands += create_print_lines_command(bytes(packed))

    return commands

def create_print_commands(data: bytes) -> bytes:
    commands = bytearray()
    # Add commands to print the image data in blocks
    commands += create_print_lines_commands(data, PAPER_WIDTH, BLOCK_LINES)
    # Add a command to feed the paper after printing
    commands += create_feed_paper_command(GAP_LINES)

    return bytes(commands)
