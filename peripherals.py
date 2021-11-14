import time
from datetime import datetime
import fire
from pathlib import Path
import serial
import boto3
import tqdm
from random import random
import multiprocessing


DATA_FILE = 'sensor_data_{date}'
BUCKET = 'nous-growbox'
PORT = '/dev/ttyACM0'
HEADER = 'time,humidity,temp'

# Basically, this initializes the serial comm object and opens the port whenever this
# module is called or imported. The 2 second delay is to allow all of the serial 
# 'handshaking' to initialize properly
ARDUINO = serial.Serial(PORT, 9600)
print('Initializing serial port')
time.sleep(2)

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


def get_sensor_datapoint(serial=ARDUINO):
    '''Gets sensor data from arduino.'''
    serial.flush()
    serial.read_all()
    serial.write('getTempHumidity\n'.encode())
    time.sleep(0.5)
    s = serial.readline().strip().decode()
    humidity, temp = s.split(',')
    return DataPoint(float(humidity), float(temp))

    
def capture_loop(sample_rate: int, source: str, data_dir='.'):
    while True:
        try:
            capture_single_point(source, data_dir)
        except ValueError:  #TODO fix this nasty code
            breakpoint()
            continue
        time.sleep(sample_rate)


def capture_single_point(source: str, data_dir='.'):
    assert source in ['sensor', 'fake'], "`source` must be one of ['sensor', 'fake']"
    if source == 'sensor':
        data = get_sensor_datapoint()
    else:
        data = get_fake_datapoint()

    fname = f'growbox_data_{source}_{data.year}{data.month}{data.day}-{data.hour}.csv'
    data_dir = Path(data_dir)
    if not data_dir.exists():
        data_dir.mkdir()

    file = Path(data_dir) / fname

    if not file.exists():
        to_write = f'{HEADER}\n{data}\n'
    else:
        to_write = f'{data}\n'

    with open(file, 'a') as f:
        f.write(to_write)


class Collector:
    '''Simple collector object that allows you to start and stop a collection.

    Once a Collector is instantiated, collections can be started and stopped by
    calling the `start` and `stop` methods. Under the hood, the object is creating
    `multiprocessing.Process` objects that point to the `capture_loop` function
    defined above in `peripherals.py`.

    Example:
    ```
    >>> c1 = Collector(data_dir='testing', source='fake', sample_rate=1) 
    >>> c1.start()  # Starts the collect
    >>> time.sleep(60)  # Collect for 60 seconds
    >>> c1.stop()  # Stop the collection
    >>> c1.data_dir = 'testing2'  # Switch to a new data dir
    >>> c1.source = 'sensor'  # Now collect from the sensor
    >>> c1.sample_rate = 3  # Change sample rate
    >>> c1.start()
    >>> time.sleep(50)
    >>> c1.stop()
    ```

    '''
    def __init__(self, data_dir='.', source='sensor', sample_rate=60):
        self.is_running = False
        self.data_dir = data_dir
        self.source = source
        self.sample_rate = sample_rate 

        self._p = None  # Variable to hold a multiprocessing.Process instance

    def start(self):
        '''Starts a new collection at one sample every <sample_rate> seconds.'''
        if self.is_running:
            print(f'This process is already running')

        else:  # Create and start a new process
            self._p = multiprocessing.Process(
                target=capture_loop,
                args=(self.sample_rate, self.source, self.data_dir)
            )
            self._p.start()
            self.is_running=True
            print(f'Started a collection at {60/self.sample_rate} points per minute in {self.data_dir}')


    def stop(self):
        '''Stops the current process'''
        if not self.is_running:
            print('No currently running process')
        
        else:  # Stop the current process
            self._p.terminate()
            self.is_running = False
            print(f'{self} stopped')


    def __repr__(self):
        s = self.sample_rate
        d = self.data_dir
        return f'Collector({s}, {d})'



if __name__ == '__main__':
    fire.Fire()
