# put your python code here
import cv2
import depthai as dai
import base64
import threading
import time

class OAKDCamera:
    def __init__(self, web_ui):
        # We pass in the 'ui' object so the brick can send messages to the web
        self.ui = web_ui
        self.running = False

    def _camera_loop(self):
        try:
            with dai.Pipeline() as pipeline:
                cam = pipeline.create(dai.node.Camera).build()
                qRgb = cam.requestOutput(
                    size=(416, 416),
                    type=dai.ImgFrame.Type.BGR888p
                ).createOutputQueue()
                
                pipeline.start()
                print("Custom OAK-D Brick Started Successfully!")
                
                while self.running and pipeline.isRunning():
                    inRgb = qRgb.get()
                    if inRgb is not None:
                        frame = inRgb.getCvFrame()
                        
                        ret, buffer = cv2.imencode('.jpg', frame)
                        if ret:
                            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                            image_data = f"data:image/jpeg;base64,{jpg_as_text}"
                            self.ui.send_message('camera_frame', {'image': image_data})
                            
                    time.sleep(0.03) 
        except Exception as e:
            print(f"OAK-D Brick Error: {e}")

    def start(self):
        """Call this from your main.py to start the camera thread"""
        self.running = True
        thread = threading.Thread(target=self._camera_loop, daemon=True)
        thread.start()