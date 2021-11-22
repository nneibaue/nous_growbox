function plot_sensor_data(data, element_id) {
	console.log(data);
	time = data.map(item => item.time);
	temp = data.map(item => item.temp);
	humidity = data.map(item => item.humidity);

	var temp_trace = {
		type: 'line',
		x: time,
		y: temp,
		name: 'Temperature',
        mode: 'lines+markers'
	};

	var humidity_trace = {
		type: 'line',
		x: time,
		y: humidity,
		name: 'Humidity',
        mode: 'lines+markers',
	};

	var layout = {
		// width: 600,
		// height: 400,
		title: 'Mushy Readings',
        margin: {
            t: 50, //top margin
            l: 20, //left margin
            r: 20, //right margin
            b: 20 //bottom margin
            }
	};

	Plotly.newPlot(element_id,[temp_trace, humidity_trace], layout);
}