import time
from datetime import datetime
import fire
from pathlib import Path
import serial
import boto3
import tqdm
from random import random


DATA_FILE = 'sensor_data_{date}'
BUCKET = 'nous-growbox'
PORT = '/dev/ttyACM0'
HEADER = 'time,humidity,temp'

def initialize_sensor():
    # Do stuff here with imports and serial?
    pass

def upload_to_bucket(bucket_name: str, local_filename: str, cloud_filename: str):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    print(f'Uploading {local_filename} to {bucket} as {cloud_filename}...')
    bucket.upload_file(local_filename, cloud_filename)
    print('Upload successful!')


class DataPoint:
    def __init__(self, temp: float, humidity: float):
        self.temp = temp
        self.humidity = humidity
        self._time = datetime.now()

        # Parse out useful time info
        self.time = self._time.isoformat()
        self.hour = self._time.hour
        self.day = self._time.day
        self.minute = self._time.minute
        self.year = self._time.year
        self.month = self._time.month

    
    def __repr__(self):
        return f'{self.time},{self.humidity},{self.temp}'


def get_fake_datapoint():
    humidity = random() 
    temp = random()*5.5
    return DataPoint(temp, humidity)


def get_sensor_datapoint(serial):
    '''Gets sensor data from arduino.'''
    serial.flush()
    serial.read_all()
    serial.write('getTempHumidity\n'.encode())
    time.sleep(0.2)
    s = serial.readline().strip().decode()
    humidity, temp = s.split(',')
    return DataPoint(float(humidity), float(temp))

    
def capture_loop(duration, upload=False, real=False):
    file = Path('testfile.csv')
    if not file.exists():
        with open(file, 'w') as f:
            f.write('time,humidity,temp\n')

    f = open(file, 'a')
    print(f'Performing a {duration} second test...')
    for _ in tqdm.tqdm(range(duration)):
        if real:
            PORT = '/dev/ttyACM0'
            s = serial.Serial(PORT, 9600)
            data = get_sensor_datapoint(s)
        else:
            data = get_fake_datapoint()

        f.write(f'{data}\n')
        time.sleep(1)
    f.close()

    if upload:
        cloud_filename = 'test1_11-6-2021'
        upload_to_bucket(BUCKET, str(file), cloud_filename)


# Every minute:
# take a data point. We have data now
# Decide where it goes -> based on data timestamp, group by hour

def capture_single_point(source: str):
    assert source in ['sensor', 'fake'], "`source` must be one of ['sensor', 'fake']"
    if source == 'sensor':
        # Open the serial port _only_ when we need to take a data point
        s = serial.Serial(PORT, 9600)
        data = get_sensor_datapoint(s)
    else:
        data = get_fake_datapoint()

    file = Path(f'growbox_data_{source}_{data.year}{data.month}{data.day}-{data.hour}.csv')
    if not file.exists():
        to_write = f'{HEADER}\n{data}\n'
    else:
        to_write = f'{data}\n'

    with open(file, 'a') as f:
        f.write(to_write)


if __name__ == '__main__':
    fire.Fire(capture_loop)
