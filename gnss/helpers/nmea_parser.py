def parse_gga(line):
    if not line.startswith("$GPGGA"):
        return None

    parts = line.split(",")

    try:
        lat_raw = parts[2]
        lat_dir = parts[3]
        lon_raw = parts[4]
        lon_dir = parts[5]

        def to_decimal(raw, direction):
            if not raw:
                return None

            deg = int(raw[:2 if direction in ("N", "S") else 3])
            minutes = float(raw[2 if direction in ("N", "S") else 3:])

            dec = deg + minutes / 60

            if direction in ("S", "W"):
                dec = -dec

            return dec

        lat = to_decimal(lat_raw, lat_dir)
        lon = to_decimal(lon_raw, lon_dir)

        return {
            "time": parts[1],
            "lat": lat,
            "lon": lon,
            "fix": int(parts[6]) if parts[6] else 0,
            "satellites": int(parts[7]) if parts[7] else 0,
            "hdop": float(parts[8]) if parts[8] else None
        }

    except (IndexError, ValueError):
        return None