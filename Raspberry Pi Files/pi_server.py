
import cv2
import socket
import struct

from picamera2 import Picamera2
from ultralytics import YOLO

HOST = "0.0.0.0"
PORT = 5000

# Replace this with the model used by your detect.py
model = YOLO("yolo11n.pt")

camera = Picamera2()
config = camera.create_video_configuration(
    main={"size": (1920, 1080), "format": "RGB888"}
)
camera.configure(config)
camera.start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"Waiting for PC connection on port {PORT}...")

try:
    conn, addr = server.accept()
    print(f"Connected to {addr}")

    with conn:
        while True:
            # Capture camera frame
            frame = camera.capture_array()

            # Run object detection
            results = model.predict(
                frame, imgsz=320, conf=0.3, verbose=False
            )

            # Add detection bounding boxes
            annotated = results[0].plot()

            # Compress frame into JPEG
            success, encoded = cv2.imencode(
                ".jpg", annotated,
                [cv2.IMWRITE_JPEG_QUALITY, 70]
            )

            if not success:
                continue

            data = encoded.tobytes()

            # Send frame length followed by frame
            conn.sendall(struct.pack("!I", len(data)))
            conn.sendall(data)

except (BrokenPipeError, ConnectionResetError):
    print("PC disconnected.")

except KeyboardInterrupt:
    print("Stopping stream.")

finally:
    camera.stop()
    server.close()
