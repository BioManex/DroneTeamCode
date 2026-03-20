# These two modules allow us to run a web server.
from flask import Flask, render_template
from flask_socketio import SocketIO
# This module lets us pick random numbers.
import random
# Add this line to import the BMP180 library:
from bmp180 import BMP180

from picamera2 import Picamera2

import io
import base64
import RPi.GPIO as GPIO

from bmp180 import BMP180

from mpu6050 import mpu6050

import RPi.GPIO as GPIO
from time import sleep

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()
timer=0
mpu = mpu6050(0x68) # 0x68 is a special value that points to the MPU-6050 on I2C. You don't need to touch this or worry about it.
# Define our motor controller pins
IN1 = 12
IN2 = 13
ENA = 18 # The new ENA pin

accel_data = mpu.get_accel_data()
print(accel_data['x'])
print(accel_data['y'])
print(accel_data['z'])
gyro_data = mpu.get_gyro_data()
print(gyro_data['x'])
print(gyro_data['y'])
print(gyro_data['z'])

#bmp = BMP180()

# Here, we create the neccesary base app. You don't need to worry about this.
app = Flask(__name__)
socketio = SocketIO(app)

bmp = BMP180()
# When someone requests the root page from our web server, we return 'index.html'.
@app.route('/')
def index():
    return render_template('index.html')
# ... after the app and socketio lines
app = Flask(__name__)
socketio = SocketIO(app)

# Create an object to represent our BMP180 sensor
bmp = BMP180()

# This function runs in the background to transmit data to connected clients.
def background_thread():
    while True:
        # We sleep here for a single second, but this can be increased or decreased depending on how quickly you want data to be pushed to clients.
        socketio.sleep(1)
        barometricPressure = bmp.get_pressure()
        # Then, we emit an event called "update_data" - but this can actually be whatever we want - with the data being a dictionary
        # where 'randomNumber' is set to a random number we choose here. You should replace the data being sent back with your sensor data
        # that you fetch from things connected to your Pi.
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
@socketio.on('do_a_thing')
def do_a_thing(msg):
    # 'msg' will contain the data sent from the client, like how we had it before.
    # Let's print what we just received to the console!
    print(msg['hello'])
# This function runs when someone connects to the server - and all we do is start the background thread to update the data.
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=background_thread)
    
@socketio.on('request_image')
def handle_image_request():
    stream = io.BytesIO()
    picam2.capture_file(stream, format='jpeg')
    stream.seek(0)
    b64_image = base64.b64encode(stream.read()).decode('utf-8')
    socketio.emit('new_image', {'image_data': b64_image})
    print("Sent new Image to client.")


# First, we define our two output pins that the motor controller is connected to.


# Set the GPIO numbering mode so that it knows how we're referring to the pins
GPIO.setmode(GPIO.BCM)

# Set up the GPIO pins as output
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Now, we define three functions to help us set the motor's state. These should be pretty self-explanatory.
def motor_forward():
    """Turns the motor forward"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def motor_backward():
    """Turns the motor backward"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

def motor_stop():
    """Stops the motor"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

# Now, to make the motor do things, for example:
from time import sleep
print("Moving forward...")
motor_forward()
sleep(3)

print("Moving backward...")
motor_backward()
sleep(3)

print("Stopping...")
motor_stop()
sleep(3)
# Easy peasy!



# Set the GPIO numbering mode
GPIO.setmode(GPIO.BCM)

# Set up the GPIO pins as output
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Create a PWM instance for the ENA pin
# The second argument is the frequency in Hertz. 100Hz is a good starting point.
pwm = GPIO.PWM(ENA, 100)

# Start PWM with a duty cycle of 0 (motor is off)
pwm.start(0)

def motor_forward(speed):
    """Turns the motor forward at a given speed (0-100)"""
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_backward(speed):
    """Turns the motor backward at a given speed (0-100)"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    """Stops the motor"""
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)

# Example usage:
print("Moving forward at 50% speed...")
motor_forward(50)
sleep(3)

print("Moving backward at 100% speed...")
motor_backward(100)
sleep(3)

print("Moving forward at 25% speed...")
motor_forward(25)
sleep(3)

print("Stopping...")
motor_stop()
sleep(3)

# Don't forget to clean up the GPIO pins and stop PWM
pwm.stop()
GPIO.cleanup()

def get_current_angle():
    tick30=0
    timer=0
    delta_time=0
    current_angle=0
    while 1:
        FPS(tick30)
        
def FPS(lastTick30):
    tick30=timer*30
    delta_time=tick30-lastTick30


# This function is called
def main():
    # These specific arguments are required to make sure the webserver is hosted in a consistent spot, so don't change them unless you know what you're doing.
    socketio.run(app, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
    

