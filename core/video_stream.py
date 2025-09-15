import time
import threading
import struct
import cv2
import numpy as np

class VideoStreamHandler:
    HEADER_FMT = "!IHH"  # frame_id:uint32, total:uint16, index:uint16
    HEADER_SIZE = struct.calcsize(HEADER_FMT)

    def __init__(self, udp_sock, frame_callback, timeout=2.0):
        self.udp_sock = udp_sock
        self.frame_callback = frame_callback
        self.timeout = timeout
        self.buffers = {}
        self.buffers_lock = threading.Lock()

    def receive_loop(self, running_flag):
        while running_flag():
            try:
                data, _ = self.udp_sock.recvfrom(65535)
                if len(data) <= self.HEADER_SIZE:
                    continue
                frame_id, total, index = struct.unpack(self.HEADER_FMT, data[:self.HEADER_SIZE])
                chunk = data[self.HEADER_SIZE:]

                with self.buffers_lock:
                    buf = self.buffers.get(frame_id)
                    if buf is None:
                        if total == 0 or total > 65535:
                            continue
                        buf = {"total": total, "parts": [None]*total, "received": 0, "last_seen": time.time()}
                        self.buffers[frame_id] = buf

                    if 0 <= index < buf["total"] and buf["parts"][index] is None:
                        buf["parts"][index] = chunk
                        buf["received"] += 1
                        buf["last_seen"] = time.time()

                    if buf["received"] == buf["total"]:
                        frame_bytes = b"".join(buf["parts"])
                        del self.buffers[frame_id]
                        self._process_frame(frame_id, frame_bytes)

            except Exception as e:
                print(f"⚠️ Erro no receive_loop: {e}")

    def cleanup(self):
        """Remove buffers de frames incompletos expirados."""
        now = time.time()
        with self.buffers_lock:
            old = [fid for fid, buf in self.buffers.items() if now - buf["last_seen"] > self.timeout]
            for fid in old:
                print(f"🧹 Limpando frame {fid} (timeout)")
                del self.buffers[fid]

    def _process_frame(self, frame_id, frame_bytes):
        try:
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame_callback(frame_rgb)
        except Exception as e:
            print(f"⚠️ Erro ao processar frame {frame_id}: {e}")
