import os
from datetime import datetime
import time
import cv2

# ÉP OPENCV DÙNG GIAO THỨC TCP
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

CAMERA_IP = "192.168.1.181"
CAMERA_VERIFY_CODE = "Longym2004"
RTSP_URL = f"rtsp://admin:{CAMERA_VERIFY_CODE}@{CAMERA_IP}:554/Streaming/Channels/101"

INTERVAL_SECONDS = 10  # Chụp mỗi 10 giây
FPS = 15

start_time_file = datetime.now().strftime("%H%M%S_%d%m%Y")
OUTPUT_VIDEO = f"timelapse_{start_time_file}.mp4"

def get_camera_stream(url):
    """Hàm khởi tạo kết nối tới camera"""
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

print(f"Đang thử kết nối tới camera {CAMERA_IP}...")
cap = get_camera_stream(RTSP_URL)

out = None
frame_count = 0
fail_count = 0

try:
    while True:
        if cap.isOpened():
            # Xả 1 frame cũ để lấy hình ảnh mới nhất tại thời điểm hiện tại
            cap.grab()
            ret, frame = cap.retrieve()

            if ret:
                fail_count = 0  # Reset đếm lỗi khi nhận được khung hình chuẩn

                if out is None:
                    height, width, _ = frame.shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))

                out.write(frame)
                frame_count += 1
                
                now_str = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                print(f"Đã lưu frame {frame_count} lúc {now_str}")
                
                time.sleep(INTERVAL_SECONDS)
                continue

        # Xử lý khi mất kết nối hoặc không đọc được frame
        fail_count += 1
        print(f"Mất khung hình ({fail_count}/3), đang thử lại...")
        time.sleep(2)

        # Nếu lỗi 3 lần liên tiếp -> Khởi tạo lại kết nối RTSP
        if fail_count >= 3:
            print("→ Luồng RTSP bị ngắt. Đang tự động kết nối lại camera...")
            if cap:
                cap.release()
            time.sleep(1)
            cap = get_camera_stream(RTSP_URL)

except KeyboardInterrupt:
    print("\nĐã dừng chương trình.")

finally:
    if cap and cap.isOpened():
        cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()

    print("\n==========================================")
    print(f"✓ Video time-lapse đã tạo thành công!")
    print(f"✓ Đường dẫn file: {os.path.abspath(OUTPUT_VIDEO)}")
    print(f"✓ Tổng số frame đã lưu: {frame_count} frame")
    print("==========================================")
