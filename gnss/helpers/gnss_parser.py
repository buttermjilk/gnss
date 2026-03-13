def parse_gnss_time(t):
    if not t:
        return None

    t = str(t)

    hours = int(t[0:2])
    minutes = int(t[2:4])
    seconds = float(t[4:])

    return hours * 3600 + minutes * 60 + seconds