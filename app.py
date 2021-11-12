from flask import Flask, request, render_template
import serial
import peripherals
from datetime import datetime
import RPi.GPIO as gpio
import pandas as pd

app = Flask(__name__)
PORT = '/dev/ttyACM0'

RELAY = 21
gpio.setmode(gpio.BCM)
gpio.setup(RELAY, gpio.OUT)

base = '''
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<h3>Reading at {now}</h3>
<b>Temperature:</b> {temp} <br>
<b>Humidity:</b> {humidity} <br>
<div style="border: 2px solid green;width: 25%">
    <input type="button" onclick="submit('on')" value="Fan on"/>
    <input type="button" onclick="submit('off')" value="Fan off"/>

<script>
function submit(which) {{
    console.log(which);
    $.post("/fancontrol", {{"setButtonTo": which}})
}}
</script>
'''

# Instantiate Serial object with 9600 baud rate (to match Arduino,
# which is also set at 9600)
arduino_comm = serial.Serial(PORT, 9600)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/current')
def show_current_readings():
    print(request.url)
    humidity, temp = peripherals.get_sensor_data(arduino_comm)
    now = datetime.now()
    return base.format(temp=temp, humidity=humidity, now=now)


@app.route('/fancontrol', methods=['POST'])
def actuate_fan():
    which = request.form['setButtonTo']
    if which == 'off':
        gpio.output(RELAY, gpio.HIGH)
    elif which == 'on':
        gpio.output(RELAY, gpio.LOW)
    return 'you got it'


@app.route('/current_temperature')
def get_current_temperature():
    ...
    return '5'

@app.route('/graph')
def render_graph():
    print(request.url)
    file = 'testfile.csv'
    df = pd.read_csv(file)
    template = render_template('graph.html', data=df.to_json(orient='records'))
    return template


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
