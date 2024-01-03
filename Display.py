import http.server
import socketserver
import threading
import numpy as np
import cv2
import time
import sys

class MJPEGHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, display):
        self.display = display
        super().__init__(request, client_address, server)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                frame = self.display.get_frame()
                self.wfile.write(b'--jpgboundary\r\n')
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(frame)
                time.sleep(1 / self.display.fps)

class Display:
    def __init__(self, frame_WH=[1280, 720], fps=30):
        self.frame_width = frame_WH[0]
        self.frame_height = frame_WH[1]
        self.fps = fps
        self.frame = b''
        self.frame_buffer = None
        self.frame_lock = threading.Lock()

    # 啟動MJEPG串流
    def start_mjpeg_server(self, event):
        with socketserver.TCPServer(("0.0.0.0", 8888), lambda *args, **kwargs: MJPEGHandler(*args, **kwargs, display=self)) as httpd:
            while not event.is_set():
                print("MJEPG server started on port 8888")
                httpd.serve_forever()

    def generate_frame(self, text=None, img_path=None, bbox=None):
        if img_path:
            frame = cv2.imread(img_path+'.png')
            text = img_path
        elif text:
            frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if bbox and bbox[0]=="2D":
            cv2.rectangle(frame, *bbox[1], (255,0,0), 3)
        elif bbox and bbox[0]=="Segmentation":
            cv2.drawContours(frame, [bbox[1]], -1, (0, 255, 0, 0), 3)
        _, buffer = cv2.imencode('.jpg', frame)

        with self.frame_lock:
            self.frame = buffer.tobytes()

    def get_frame(self):
        with self.frame_lock:
            return self.frame