from flask import Flask, Response
from picamera2 import Picamera2
import cv2

app = Flask(__name__)
camera = Picamera2()
camera.configure(camera.create_video_configuration(
	main={"size": (1920,1080), "format": "RGB888"}
))
camera.start()

def generate_frames():
	while True:
		frame = camera.capture_array()
		ok, buffer = cv2.imencode(
			".jpg", frame,
			[cv2.IMWRITE_JPEG_QUALITY, 80]
		)
		if not ok:
			continue
		yield (
			b"--frame\r\n"
			b"Content-Type: image/jpeg\r\n\r\n" +
			buffer.tobytes() + b"\r\n"
		)
@app.route("/video")
def video():
	return Response(
		generate_frames(),
		mimetype="multipart/x-mixed-replace; boundary=frame"
	)

app.run(host="0.0.0.0", port=5000, threaded=True)
