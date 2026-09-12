# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI

motor_state = "STOPPED"

def get_motor_status():
    return {"motor_state": motor_state, "status_text": f"MOTOR IS {motor_state}"}

# ==========================================
# 1. ROBOT MOTOR CONTROLS
# ==========================================
def on_motor_forward(client, data):
    global motor_state
    motor_state = "FORWARD"
    try:
        Bridge.call("set_reverse", False) 
        Bridge.call("set_forward", True)
    except Exception as e:
        print(f"Bridge error (forward): {e}", flush=True)
        
    ui.send_message('motor_status_update', get_motor_status())

def on_motor_reverse(client, data):
    global motor_state
    motor_state = "REVERSE"
    try:
        Bridge.call("set_forward", False)
        Bridge.call("set_reverse", True)
    except Exception as e:
        print(f"Bridge error (reverse): {e}", flush=True)
        
    ui.send_message('motor_status_update', get_motor_status())

def on_motor_left(client, data):
    global motor_state
    motor_state = "TURNING LEFT"
    try:
        Bridge.call("set_forward", False) 
        Bridge.call("set_reverse", False)
        Bridge.call("set_left", True)
    except Exception as e:
        print(f"Arduino missing set_left command: {e}", flush=True)
        
    ui.send_message('motor_status_update', get_motor_status())

def on_motor_right(client, data):
    global motor_state
    motor_state = "TURNING RIGHT"
    try:
        Bridge.call("set_forward", False) 
        Bridge.call("set_reverse", False)
        Bridge.call("set_right", True)
    except Exception as e:
        print(f"Arduino missing set_right command: {e}", flush=True)
        
    ui.send_message('motor_status_update', get_motor_status())

def on_motor_stop(client, data):
    global motor_state
    motor_state = "STOPPED"
    try:
        Bridge.call("stop_motor", True)
    except Exception as e:
        print(f"Bridge error (stop): {e}", flush=True)
        
    ui.send_message('motor_status_update', get_motor_status())

# ==========================================
# 2. CAMERA PAN/TILT CONTROLS
# ==========================================
def on_camera_up(client, data):
    try: Bridge.call("cam_up", True)
    except: pass

def on_camera_down(client, data):
    try: Bridge.call("cam_down", True)
    except: pass

def on_camera_left(client, data):
    try: Bridge.call("cam_left", True)
    except: pass

def on_camera_right(client, data):
    try: Bridge.call("cam_right", True)
    except: pass

def on_get_initial_state(client, data):
    ui.send_message('motor_status_update', get_motor_status(), client)

# ==========================================
# 3. VIDEO STREAMING RELAY
# ==========================================
def on_incoming_frame(client, data):
    try:
        ui.send_message('camera_frame', data)
    except Exception as e:
        print(f"Crash prevented! Failed to relay frame: {e}", flush=True)

ui = WebUI()

# Register Robot Motor Events
ui.on_message('motor_forward', on_motor_forward)
ui.on_message('motor_reverse', on_motor_reverse)
ui.on_message('motor_left', on_motor_left)
ui.on_message('motor_right', on_motor_right)
ui.on_message('motor_stop', on_motor_stop)

# Register Camera D-Pad Events
ui.on_message('camera_up', on_camera_up)
ui.on_message('camera_down', on_camera_down)
ui.on_message('camera_left', on_camera_left)
ui.on_message('camera_right', on_camera_right)

ui.on_message('get_initial_state', on_get_initial_state)
ui.on_message('relay_frame', on_incoming_frame)

App.run()