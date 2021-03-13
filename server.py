from aiohttp import web
import socketio
import json
import Adafruit_PCA9685


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

from motorkit import MotorKit
kit = MotorKit(0x40)

camera_pwm = Adafruit_PCA9685.PCA9685(0x42)
h_channel = 0
v_channel = 1

v_min = 100
v_max = 250

h_min = 100
h_max = 580
h_middle = 320

def drive(l, r):
  kit.motor1.throttle = 0-r
  kit.motor2.throttle = 0-l

def adjust_camera(h, v):
  h = min(h_max, max(h_min, h))
  v = min(v_max, max(v_min, v))

  camera_pwm.set_pwm(h_channel, 0, h)
  camera_pwm.set_pwm(v_channel, 0, v)

def reset():
  drive(0, 0)

@sio.event
async def connect(sid, environ):
  print("connect ", sid)
  reset()
  await sio.emit("calibrate", {"camera": {
    "h": h_middle,
    "v": v_min,
    "h_min": h_min,
    "h_middle": h_middle,
    "h_max": h_max,
    "v_min": v_min,
    "v_max": v_max
  }})

@sio.event
async def steer(sid, data):
  drive(data['left'], data['right'])

@sio.event
async def camera(sid, data):
  adjust_camera(data['horizontal'], data['vertical'])

@sio.event
def disconnect(sid):
  print('disconnect ', sid)
  reset()

import atexit
atexit.register(reset)

if __name__ == '__main__':
  reset()
  adjust_camera(h_middle, v_min)
  web.run_app(app)
