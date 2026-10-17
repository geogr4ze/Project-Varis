
import socket
import struct
import cv2
import numpy as np

PI_IP = "192.168.1.104"
PORT = 5000

def receive_exact(sock, size):
    data = bytearray()

    while len(data) < size:
        packet = sock.recv(size - len(data))

        if not packet:
            return None

        data.extend(packet)

    return bytes(data)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((PI_IP, PORT))
    print("Connected to Raspberry Pi!")

    while True:
        # Receive the 4-byte frame size
        header = receive_exact(client, 4)

        if header is None:
            break

        frame_size = struct.unpack("!I", header)[0]
        frame_data = receive_exact(client, frame_size)  # Receive the full JPEG frame

        if frame_data is None:
            break

        # Decode into an OpenCV image
        frame = cv2.imdecode(
            np.frombuffer(frame_data, dtype=np.uint8),         
            cv2.IMREAD_COLOR
        )

        if frame is None:
            continue

        cv2.imshow("Raspberry Pi Object Detection", frame) # Display in a separate window

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except ConnectionRefusedError:
    print("Connection refused. Start pi_server.py first.")

except OSError as error:
    print(f"Connection error: {error}")

finally:
    client.close()
    cv2.destroyAllWindows()
