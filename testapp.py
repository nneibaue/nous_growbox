from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)
PORT = '/dev/ttyACM0'


@app.route('/')
def render_graph():
    print(request.url)
    file = 'testfile.csv'
    df = pd.read_csv(file)
    template = render_template('graph.html', data=df.to_json(orient='records'))
    return template


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")