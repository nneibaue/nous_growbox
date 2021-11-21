from flask import Flask, request, render_template, url_for, redirect
import serial
import peripherals
import data_utils
from pathlib import Path
from datetime import datetime
import RPi.GPIO as gpio
import pandas as pd
import multiprocessing
import time
import re

app = Flask(__name__)
PORT = '/dev/ttyACM0'
DATA_BASE_DIR = 'data'
FILE_PATTERN = 'growbox_data_(sensor|fake)_(?P<date>\d{8})-(?P<hour>\d{1,2})\.csv'

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

collector = peripherals.Collector() 


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/stop')
def stop_loop():
    collector.stop()
    return redirect(url_for('show_current_readings'))


@app.route('/start')
def start_collection():
    collector.data_dir = request.args.get('data_dir', '.', type=str)
    collector.sample_rate = request.args.get('sample_rate', 60, type=int)
    collector.source = request.args.get('source', 'sensor', type=str)
    collector.start()
    return redirect(url_for('show_current_readings'))
    

@app.route('/current')
def show_current_readings():
    print(request.url)
    current_data = peripherals.get_sensor_datapoint()
    data = get_data()
    return render_template(
        'index.html',
        temp=current_data.temp,
        humidity=current_data.humidity,
        now=current_data.time,
        status=collector.status,
        plotdata=data
    )


@app.route('/fancontrol', methods=['POST'])
def actuate_fan():
    which = request.form['setButtonTo']
    if which == 'off':
        gpio.output(RELAY, gpio.HIGH)
    elif which == 'on':
        gpio.output(RELAY, gpio.LOW)
    return 'you got it'


# @app.route('/data/<data_dir>')
def get_data(data_dir):
	data_dir = Path(DATA_BASE_DIR) / data_dir
	all_files =data_dir.glob('*.csv')
	dfs = [pd.read_csv(f) for f in all_files if re.match(FILE_PATTERN, f.name)]
	return pd.concat(dfs).to_json(orient='records')


@app.route('/graph/<collection_name>')
def render_graph(collection_name):
    data = data_utils.get_data(collection_name)
    template = render_template('graph.html', data=data.to_json(orient='records'))
    return template


if __name__ == "__main__":
    app.run(debug=True, port=28471, host="0.0.0.0", use_reloader=False)
