def loadFromFile(dnsFile):
    records = {}

    for line in dnsFile:
        split = line.strip().split()
        if len(split) < 3:
            continue
        if split[2] == 'NS':
            records['NS'] = split[0]
        else:
            records[split[0]] = {
                "ip": split[1],
                "flag": split[2]
            }
    return records