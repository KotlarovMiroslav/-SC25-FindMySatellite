def data_formatter(data_bytes):
    if isinstance(data_bytes, bytes):
        data = list(data_bytes)
    elif isinstance(data_bytes, list) and len(data_bytes) == 9:
        data = data_bytes
    else:
        raise ValueError("Input must be a 9-byte sequence.")

    if data[0] != 0x59 or data[1] != 0x59:
        raise ValueError("Invalid frame header.")

    checksum = sum(data[:8]) & 0xFF
    if checksum != data[8]:
        raise ValueError("Checksum mismatch.")

    distance = float((data[3] << 8) | data[2])
    return distance

while True:
    try:
        reading = data_formatter(ser.read(9))
    except Exception:
        continue
    print(f"Reading: {reading}")