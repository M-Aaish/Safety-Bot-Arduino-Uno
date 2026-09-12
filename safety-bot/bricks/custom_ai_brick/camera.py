import cv2
import depthai as dai
import base64
import time
import socketio

sio = socketio.Client()

# Connect to the main Web UI container (it is named "main" and runs on port 7000)
while True:
    try:
        sio.connect('http://main:7000')
        print("Camera container connected to Web UI!")
        break
    except:
        print("Waiting for Web UI to start...")
        time.sleep(2)

try:
    with dai.Pipeline() as pipeline:
        cam = pipeline.create(dai.node.Camera).build()
        qRgb = cam.requestOutput(size=(416, 416), type=dai.ImgFrame.Type.BGR888p).createOutputQueue()
        pipeline.start()
        
        while pipeline.isRunning():
            inRgb = qRgb.get()
            if inRgb is not None:
                frame = inRgb.getCvFrame()
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    # Beam the image to the main container!
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    image_data = f"data:image/jpeg;base64,{jpg_as_text}"
                    sio.emit('relay_frame', {'image': image_data})
            time.sleep(0.03)
except Exception as e:
    print(f"OAK-D Error: {e}")