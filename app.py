# -*- coding: utf-8 -*-
"""
Gesture Control Advanced - Phiên bản Luôn Hoạt Động

Một chương trình điều khiển máy tính bằng cử chỉ tay qua webcam, tích hợp nhiều tính năng cao cấp.
Phiên bản này sẽ luôn chạy và không bị tạm dừng khi sử dụng chuột vật lý.

Chức năng:
- Điều khiển chuột tương đối (có tăng tốc và vùng chết).
- Nhiều cử chỉ: di chuyển, nhấp trái/phải, kéo thả, cuộn, alt-tab.
- Chế độ điều khiển hệ thống: tăng/giảm âm lượng và độ sáng.
- Giao diện hiển thị trạng thái trực quan.

Yêu cầu thư viện:
pip install opencv-python mediapipe pyautogui numpy pynput pycaw screen-brightness-control
"""
import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
from pynput.mouse import Controller, Button

# Cố gắng import thư viện hệ thống, nếu thất bại sẽ vô hiệu hóa tính năng liên quan.
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import screen_brightness_control as sbc
    SYSTEM_CONTROL_ENABLED = True
except ImportError:
    SYSTEM_CONTROL_ENABLED = False
    print("Cảnh báo: Không tìm thấy thư viện pycaw hoặc screen-brightness-control.")
    print("Tính năng điều khiển Âm lượng/Độ sáng sẽ bị vô hiệu hóa.")

# ================== CONFIGURATION ==================
# Điều khiển chuột
MOUSE_SPEED_NORMAL = 1.8      # Tốc độ chuột khi di chuyển chậm
MOUSE_SPEED_FAST = 4.0        # Tốc độ chuột khi di chuyển nhanh
FAST_MOVE_THRESHOLD = 0.03    # Ngưỡng (khoảng cách chuẩn hóa) để kích hoạt tốc độ nhanh
DEAD_ZONE_RADIUS = 0.005      # Bỏ qua các chuyển động tay rất nhỏ để tránh rung con trỏ
SMOOTHING_FACTOR = 0.3        # Làm mượt chuyển động (giảm để mượt hơn)

# Cuộn và Nhận diện cử chỉ
SCROLL_SENSITIVITY = 40       # Độ nhạy cuộn (tăng để cuộn nhanh hơn)
PINCH_THRESHOLD = 0.07        # Ngưỡng chụm để kéo
GESTURE_CONFIRM_FRAMES = 3    # Số khung hình liên tiếp cần để xác nhận một cử chỉ
ACTION_COOLDOWN = 0.5         # Thời gian chờ (giây) giữa các hành động nhấp chuột

# ===================================================

# Khởi tạo
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()
mouse = Controller()

# Khởi tạo điều khiển hệ thống
if SYSTEM_CONTROL_ENABLED:
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
    except Exception as e:
        print(f"Lỗi khởi tạo pycaw: {e}. Vô hiệu hóa điều khiển âm lượng.")
        SYSTEM_CONTROL_ENABLED = False

# Biến trạng thái
prev_pos = None; gesture_buffer = []; last_action_time = 0; paused = False; dragging = False
control_mode = "Mouse"; system_control_start_pos = None; last_gesture = "None"

# Hàm trợ giúp
def get_finger_states(hand_landmarks):
    """Xác định ngón tay nào đang giơ lên. Trả về list boolean [thumb, index, middle, ring, pinky]."""
    fingers = []
    hand_orientation = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x
    fingers.append(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x if hand_orientation else hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x)
    for tip_id, pip_id in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        fingers.append(hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y)
    return fingers

def calculate_distance(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def confirm_gesture(gesture):
    """Xác nhận cử chỉ nếu nó ổn định trong vài khung hình."""
    global last_gesture
    gesture_buffer.append(gesture)
    if len(gesture_buffer) > GESTURE_CONFIRM_FRAMES: gesture_buffer.pop(0)
    is_stable = len(set(gesture_buffer)) == 1
    new_confirmed = is_stable and gesture_buffer[0] != last_gesture and gesture_buffer[0] != "None"
    if new_confirmed:
        last_gesture = gesture_buffer[0]
        return True
    if is_stable and gesture_buffer[0] == "None" and last_gesture != "None":
        last_gesture = "None"
        return True
    return False

# ----- Vòng lặp chính -----
try:
    print("Khởi động thành công. Điều khiển bằng tay luôn hoạt động.")
    print("Nhấn ESC trong cửa sổ webcam để thoát.")
    while True:
        success, img = cap.read()
        if not success: continue

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            fingers = get_finger_states(hand_landmarks)
            index_tip = hand_landmarks.landmark[8]
            thumb_tip = hand_landmarks.landmark[4]
            current_gesture = "None"

            # 1. LOGIC NHẬN DIỆN CỬ CHỈ
            if fingers == [1, 1, 1, 1, 1] and SYSTEM_CONTROL_ENABLED: current_gesture = "SystemControl"
            elif fingers == [0, 0, 0, 0, 0]: current_gesture = "Pause"
            elif paused: pass
            elif fingers == [0, 1, 0, 0, 0]: current_gesture = "Move"
            elif fingers == [0, 1, 1, 0, 0]: current_gesture = "LeftClick"
            elif fingers == [1, 1, 0, 0, 0]: current_gesture = "RightClick"
            elif fingers == [1, 0, 0, 0, 1]: current_gesture = "AltTab"
            elif fingers == [0, 1, 1, 1, 0]: current_gesture = "ScrollUp"
            elif fingers == [0, 1, 1, 1, 1]: current_gesture = "ScrollDown"
            elif calculate_distance(index_tip, thumb_tip) < PINCH_THRESHOLD: current_gesture = "Drag"
            
            # 2. LOGIC THỰC THI HÀNH ĐỘNG
            is_confirmed = confirm_gesture(current_gesture)
            can_act = (time.time() - last_action_time) > ACTION_COOLDOWN

            if last_gesture == "SystemControl" and control_mode != "SystemControl":
                control_mode = "SystemControl"; system_control_start_pos = (index_tip.x, index_tip.y)
                print("Chế độ: Điều khiển Hệ thống")
            elif last_gesture != "SystemControl" and control_mode == "SystemControl":
                control_mode = "Mouse"; system_control_start_pos = None; print("Chế độ: Điều khiển Chuột")

            if control_mode == "Mouse":
                if last_gesture == "Move":
                    if prev_pos:
                        dx_raw, dy_raw = index_tip.x - prev_pos[0], index_tip.y - prev_pos[1]
                        if np.sqrt(dx_raw**2 + dy_raw**2) > DEAD_ZONE_RADIUS:
                            speed = MOUSE_SPEED_FAST if np.sqrt(dx_raw**2 + dy_raw**2) > FAST_MOVE_THRESHOLD else MOUSE_SPEED_NORMAL
                            mouse.move(dx_raw * screen_width * speed, dy_raw * screen_height * speed)
                    prev_pos = (index_tip.x, index_tip.y)
                    if dragging: mouse.release(Button.left); dragging = False
                else:
                    prev_pos = None
                    if last_gesture == "Drag":
                        if not dragging: mouse.press(Button.left); dragging = True
                        mouse.position = (index_tip.x * screen_width, index_tip.y * screen_height)
                    elif dragging: mouse.release(Button.left); dragging = False
                
                if is_confirmed and can_act:
                    actions = {
                        "LeftClick": lambda: mouse.click(Button.left),
                        "RightClick": lambda: mouse.click(Button.right),
                        "AltTab": lambda: pyautogui.hotkey('alt', 'tab'),
                        "ScrollUp": lambda: pyautogui.scroll(SCROLL_SENSITIVITY),
                        "ScrollDown": lambda: pyautogui.scroll(-SCROLL_SENSITIVITY),
                        "Pause": lambda: globals().update(paused=not paused)
                    }
                    if last_gesture in actions:
                        actions[last_gesture](); last_action_time = time.time()

            elif control_mode == "SystemControl":
                if system_control_start_pos:
                    dx, dy = index_tip.x - system_control_start_pos[0], system_control_start_pos[1] - index_tip.y
                    if SYSTEM_CONTROL_ENABLED:
                        vol_change = dx * 1.5; current_vol = volume.GetMasterVolumeLevelScalar(); new_vol = np.clip(current_vol + vol_change, 0.0, 1.0)
                        if abs(new_vol - current_vol) > 0.01: volume.SetMasterVolumeLevelScalar(new_vol, None)
                        bright_change = dy * 150; current_bright = sbc.get_brightness()[0]; new_bright = np.clip(current_bright + bright_change, 0, 100)
                        if abs(new_bright - current_bright) > 1: sbc.set_brightness(int(new_bright))
                    system_control_start_pos = (index_tip.x, index_tip.y)
        else:
            if dragging: mouse.release(Button.left); dragging = False
            prev_pos = None; last_gesture = "None"; gesture_buffer.clear()

        # 3. HIỂN THỊ TRẠNG THÁI
        display_text, color = "", (0, 255, 0)
        if paused:
            display_text, color = "DA TAM DUNG", (0, 0, 255)
        elif control_mode == "SystemControl":
            if SYSTEM_CONTROL_ENABLED:
                vol, bright = int(volume.GetMasterVolumeLevelScalar() * 100), sbc.get_brightness()[0]
                display_text, color = f"HE THONG: Am luong {vol}% | Sang {bright}%", (255, 150, 0)
            else:
                display_text, color = "HE THONG (BI LOI)", (255, 0, 0)
        elif dragging:
            display_text, color = "DANG KEO...", (0, 255, 255)
        else:
            display_text = last_gesture.upper()

        cv2.putText(img, f"Trang thai: {display_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow("Gesture Control Advanced", img)

        if cv2.waitKey(1) & 0xFF == 27: break

finally:
    print("\nĐang đóng chương trình và giải phóng tài nguyên...")
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("Đã đóng thành công.")