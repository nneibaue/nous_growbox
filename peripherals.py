import time

def get_sensor_data(serial):
    '''Gets sensor data from arduino.'''
    serial.flush()
    serial.read_all()
    serial.write('getTempHumidity\n'.encode())
    time.sleep(0.2)
    s = serial.readline().strip().decode()
    humidity, temp = s.split(',')
    return float(humidity), float(temp)