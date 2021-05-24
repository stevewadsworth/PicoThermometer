def scan_bus(i2c):
    print('Scanning i2c bus', i2c, '...')
    devices = i2c.scan()

    if len(devices) == 0:
        print("No i2c device !")
    else:
        print('i2c devices found:', len(devices))

        for device in devices:
            print("Device address:", device, "(" + hex(device) + ")")

        print()

if (__name__ == '__main__'):
    import machine
    sda = machine.Pin(4)
    scl = machine.Pin(5)
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)

    scan_bus(i2c)
