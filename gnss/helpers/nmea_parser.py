def parse_gga(line):
    if not line.startswith("$GPGGA"):
        return None

    parts = line.split(",")
    #extract useful / needed fields
    try:
        return {
            "time": parts[1],
            "fix": int(parts[6]) if parts[6] else 0,
            "satellites": int(parts[7]) if parts[7] else 0,
            "hdop": float(parts[8]) if parts[8] else None
        }
    except (IndexError, ValueError):
        return None