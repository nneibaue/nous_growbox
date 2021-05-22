from flask import Flask
import serial
import peripherals as p
from datetime import datetime

app = Flask(__name__)

PORT = '/dev/ttyACM0'

# Instantiate Serial object with 9600 baud rate (to match Arduino)
s = serial.Serial(PORT, 9600)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/current')
def show_current_readings():
    humidity, temp = p.get_sensor_data(s)
    now = datetime.now()
    html = f'''
    <h3>Reading at {now}</h3>
    <b>Temperature:</b> {temp} <br>
    <b>Humidity:</b> {humidity} <br>
    '''
    return html

