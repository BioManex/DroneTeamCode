# These two modules allow us to run a web server.
from flask import Flask, render_template
from flask_socketio import SocketIO
# This module lets us pick random numbers, you can remove it later.
import random

from bmp180 import BMP180

from picamera2 import Picamera2
import io
import base64

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# Here, we create the neccesary base app. You don't need to worry about this.
app = Flask(__name__)
socketio = SocketIO(app)

bmp = BMP180()
# When someone requests the root page from our web server, we return 'index.html'.
@app.route('/')
def index():
    return render_template('index.html')

# This function runs in the background to transmit data to connected clients.
def background_thread():
    while True:
        # We sleep here for a single second, but this can be increased or decreased depending on how quickly you want data to be pushed to clients.
        socketio.sleep(1)
        barometricPressure = bmp.get_pressure()
        # Then, we emit an event called "update_data" - but this can actually be whatever we want - with the data being a dictionary
        # where 'randomNumber' is set to a random number we choose here. You should replace the data being sent back with your sensor data
        # that you fet	ch from things connected to your Pi.
        socketio.emit(
            'update_data',
            {
                'randomNumber': random.randint(1, 100),
                'barometricPressure': barometricPressure
                # you can add more here! for instance, something along the lines of:
                # 'mySensor': mysensor.get_sensor_data(),
            }
        )
        # To add a your first new sensor, try giving https://docs.aerospacejam.org/getting-started/first-sensor a read!

# This function runs when someone connects to the server - and all we do is start the background thread to update the data.
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=background_thread)

socket.on('update_data', function(msg) {
    var randomNumberSpan = document.getElementById('randomNumber');
    randomNumberSpan.textContent = nsg.randomNumber;
    var barometricPressureSpan = document.getElementById('barometricPressure');
    barometricPressureSpan.textContent = msg.barometricPressure;
});

@socketio.on('do_a_thing')
def do_a_thing(msg):
    print(msg['hello'])

@socketio.on('request_image')
def handle_image_request():
    stream = io.BytesIO()
    picam2.capture_file(stream, format='jpeg')
    stream.seek(0)
    b64_image = base64.b64encode(stream.read()).decode('utf-8')
    socketio.emit('new_image', {'image_data': b64_image})
    print("Sent new Image to client.")

# This function is called
def main():
    # These specific arguments are required to make sure the webserver is hosted in a consistent spot, so don't change them unless you know what you're doing.
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
    