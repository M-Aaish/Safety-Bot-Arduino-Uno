#!/usr/bin/env python3

from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
import time
import base64
import socketio

print("=== YOLO OAK-D SCRIPT STARTING ===", flush=True)

# 1. Connect to the App Lab Web UI
sio = socketio.Client()
while True:
    try:
        print("Connecting to Web UI...", flush=True)
        sio.connect('http://192.168.100.101:7000')
        print("Connected to Web UI!", flush=True)
        break
    except:
        time.sleep(2)

# Get argument first
nnPath = str((Path(__file__).parent / Path("/app/python/hardhat.blob")).resolve().absolute())
if 1 < len(sys.argv):
    arg = sys.argv[1]
    if arg == "yolo3":
        nnPath = str((Path(__file__).parent / Path('../models/yolo-v3-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
    elif arg == "yolo4":
        nnPath = str((Path(__file__).parent / Path('../models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())
    else:
        nnPath = arg
else:
    print("Using Tiny Yolo model.")

if not Path(nnPath).exists():
    local_blob = Path(__file__).parent / "hardhat.blob"
    if local_blob.exists():
        nnPath = str(local_blob.resolve().absolute())
    else:
        raise FileNotFoundError(f'Required file/s not found: {nnPath}')

labelMap = ["head", "helmet"]
syncNN = True

# Create pipeline (V2 Syntax)
pipeline = dai.Pipeline()

# ColorCamera Setup
camRgb = pipeline.create(dai.node.ColorCamera)
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRgb.setPreviewSize(416, 416)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
camRgb.setFps(15) # Kept a bit lower to ensure smooth Web UI streaming

# YoloDetectionNetwork Setup
detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)
detectionNetwork.setConfidenceThreshold(0.4)
detectionNetwork.setNumClasses(2)
detectionNetwork.setCoordinateSize(4)
detectionNetwork.setAnchors(np.array([10, 14, 23, 27, 37, 58, 81, 82, 135, 169, 344, 319]))
detectionNetwork.setAnchorMasks({"side26": np.array([1, 2, 3]), "side13": np.array([3, 4, 5])})
detectionNetwork.setIouThreshold(0.1)
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)
detectionNetwork.input.setBlocking(False)

# XLinkOut Nodes
xoutRgb = pipeline.create(dai.node.XLinkOut)
nnOut = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")
nnOut.setStreamName("nn")

# Linking
camRgb.preview.link(detectionNetwork.input)
if syncNN:
    detectionNetwork.passthrough.link(xoutRgb.input)
else:
    camRgb.preview.link(xoutRgb.input)

detectionNetwork.out.link(nnOut.input)

# Device Context Manager
with dai.Device(pipeline) as device:
    
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)

    frame = None
    detections = []
    startTime = time.monotonic()
    counter = 0

    def frameNorm(frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    print("Camera started. Relaying annotated frames to Web UI...", flush=True)

    while True:
        if syncNN:
            inRgb = qRgb.get()
            inDet = qDet.get()
        else:
            inRgb = qRgb.tryGet()
            inDet = qDet.tryGet()

        if inRgb is not None:
            frame = inRgb.getCvFrame()
            
            # FPS counter
            fps = counter / (time.monotonic() - startTime) if (time.monotonic() - startTime) > 0 else 0
            cv2.putText(frame, f"NN fps: {fps:.2f}",
                        (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (255, 255, 255))

        if inDet is not None:
            detections = inDet.detections
            counter += 1

        if frame is not None:
            color = (255, 0, 0)
            # 1. DRAW BOUNDING BOXES ON THE FRAME
            for detection in detections:
                bbox = frameNorm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
                
                label = labelMap[detection.label] if detection.label < len(labelMap) else str(detection.label)
                
                cv2.putText(frame, label, (bbox[0] + 10, bbox[1] + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.putText(frame, f"{int(detection.confidence * 100)}%", (bbox[0] + 10, bbox[1] + 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # 2. COMPRESS AND SEND TO WEB UI
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            ret, buffer = cv2.imencode('.jpg', frame, encode_param)
            if ret:
                image_data = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
                try:
                    sio.emit('relay_frame', {'image': image_data})
                except:
                    pass