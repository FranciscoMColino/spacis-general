import spacis_utils


def test_unpack_sensor_data():
    data = ['\x0b\x15\x0b', '\x0c\x16\x0c', '\r\x17\r']
    print(spacis_utils.unpack_sensor_data(data))

test_unpack_sensor_data()

