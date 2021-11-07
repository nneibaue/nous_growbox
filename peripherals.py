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

    
def upload_to_bucket(bucket_name, local_filename, cloud_filename):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    print(f'Uploading {local_filename} to {bucket} as {cloud_filename}...')
    bucket.upload_file(local_filename, cloud_filename)
    print('Upload successful!')


def get_sensor_data(serial):
    '''Gets sensor data from arduino.'''
    serial.flush()
    serial.read_all()
    serial.write('getTempHumidity\n'.encode())
    time.sleep(0.2)
    s = serial.readline().strip().decode()
    humidity, temp = s.split(',')
    return float(humidity), float(temp)

    
def capture_loop(duration, upload=False, real=False):
    PORT = '/dev/ttyACM0'
    s = serial.Serial(PORT, 9600)
    file = Path('testfile.csv')
    if not file.exists():
        with open(file, 'w') as f:
            f.write('time,humidity,temp\n')

    f = open(file, 'a')
    print(f'Performing a {duration} second test...')
    if real:
        for _ in tqdm.tqdm(range(duration)):
            timestamp = datetime.now().timestamp()
            humidity, temp = get_sensor_data(s)
            f.write(f'{timestamp},{humidity},{temp}\n')
            time.sleep(1)
        f.close()
    else:
        for _ in range(duration):
            timestamp = datetime.now().timestamp()
            fake_humidity = random() 
            fake_temp = random()*5.5
            f.write(f'{timestamp},{fake_humidity},{fake_temp}\n')
            time.sleep(1)
        f.close()
    cloud_filename = 'test1_11-6-2021'
    if upload:
        upload_to_bucket(BUCKET, str(file), cloud_filename)


if __name__ == '__main__':
    fire.Fire(capture_loop)
