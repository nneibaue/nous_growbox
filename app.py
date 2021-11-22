from flask import Flask, request, render_template, url_for, redirect, jsonify
import serial
import peripherals
import data_utils
from pathlib import Path
from datetime import datetime
import pandas as pd
import multiprocessing
import time
import re

app = Flask(__name__)
PORT = '/dev/ttyACM0'
DATA_BASE_DIR = 'data'
FILE_PATTERN = 'growbox_data_(sensor|fake)_(?P<date>\d{8})-(?P<hour>\d{1,2})\.csv'

collector = peripherals.Collector()


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
    

@app.route('/')
def show_current_readings():
    print(request.url)
    current_data = peripherals.get_sensor_datapoint()
    data = data_utils.get_data(collector.data_dir).to_json(orient='records')
    return render_template(
        'index.html',
        temp=current_data.temp,
        humidity=current_data.humidity,
        now=current_data.time,
        status=collector.status,
        plotdata=data,
    )

@app.route('/current')
def get_current_readings():
    current = peripherals.get_sensor_datapoint()
    payload =  {
        'temp': current.temp,
        'humidity': current.humidity,
        'time': current.time_nice
    }
    return jsonify(payload)


@app.route('/collection')
def get_collection_data():
    data = data_utils.get_data(collector.data_dir).to_json(orient='records')
    return jsonify(data)


@app.route('/fancontrol', methods=['POST'])
def actuate_fan():
    which = request.form['setButtonTo']
    if which == 'off':
        gpio.output(RELAY, gpio.HIGH)
    elif which == 'on':
        gpio.output(RELAY, gpio.LOW)
    return 'you got it'


@app.route('/graph/<collection_name>')
def render_graph(collection_name):
    data = data_utils.get_data(collection_name)
    template = render_template('graph.html', data=data.to_json(orient='records'))
    return template


if __name__ == "__main__":
    app.run(debug=True, port=28471, host="0.0.0.0", use_reloader=False)
