import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

camera = Picamera2()
camera.configure(
	camera.create_preview_configuration(
		main={"size": (1920, 1080), "format": "RGB888"}
	)
)
camera.start()

writer = None

try:
	while True:
		frame = camera.capture_array()
		results = model(frame, imgsz=320, verbose=False)
		annotated = results[0].plot()

		if writer is None:
			h, w = annotated.shape[:2]
			writer = cv2.VideoWriter(
				"/home/geogr4ze/detection.mp4",
				cv2.VideoWriter_fourcc(*"mp4v"),
				10,
				(w, h)
			)

		writer.write(annotated)
		print(
			f"Detected {len(results[0].boxes)} objects",
			flush=True
		)
except KeyboardInterrupt:
	print("Stopping detection")
finally:
	camera.stop()
	if writer is not None:
		writer.release()

