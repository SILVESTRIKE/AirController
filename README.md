# AirController - Điều Khiển Máy Tính Bằng Cử Chỉ

Một dự án Python sử dụng OpenCV và MediaPipe để dùng webcam của bạn thành một thiết bị điều khiển ảo, cho phép bạn tương tác với máy tính mà không cần chạm vào chuột hay bàn phím.

---

### 🎬 Demo Hoạt Động


---

### ✅ Tính Năng Nổi Bật

*   **Điều Khiển Chuột Tương Đối:** Di chuyển tay ít nhưng chuột đi xa, mang lại cảm giác tự nhiên.
*   **Tăng Tốc Chuột Động:** Tự động điều chỉnh tốc độ chuột - di chuyển chậm để chính xác, di chuyển nhanh để vượt màn hình.
*   **Vùng Chết Thông Minh:** Loại bỏ hiện tượng con trỏ bị rung do tay run nhẹ.
*   **Đa Chế Độ:**
    *   **Chế độ Chuột:** Đầy đủ các thao tác cơ bản và nâng cao.
    *   **Chế độ Hệ Thống:** Điều khiển Âm lượng và Độ sáng màn hình trực quan.
*   **Bộ Cử Chỉ Phong Phú:** Hỗ trợ nhiều hành động từ cơ bản đến nâng cao.
*   **Giao Diện Trực Quan:** Hiển thị trạng thái hiện tại (hành động, chế độ, tạm dừng) ngay trên cửa sổ webcam.

---

### 🖐️ Danh Sách Cử Chỉ

| Cử Chỉ | Hành Động | Biểu Tượng |
| :--- | :--- | :---: |
| **Giơ 1 ngón trỏ** | Di chuyển con trỏ chuột | 👆 |
| **Giơ 2 ngón (trỏ, giữa)** | Nhấp chuột trái | ✌️ |
| **Giơ 2 ngón (cái, trỏ)** | Nhấp chuột phải | L |
| **Chụm ngón cái và trỏ** | Giữ để Kéo & Thả | 🤏 |
| **Giơ 3 ngón (trỏ, giữa, nhẫn)** | Cuộn lên |  |
| **Giơ 4 ngón (trừ ngón cái)** | Cuộn xuống |  |
| **Cử chỉ "Shaka" (cái, út)** | Chuyển ứng dụng (Alt+Tab) | 🤙 |
| **Nắm tay** | Tạm dừng / Tiếp tục điều khiển | ✊ |
| **Lòng bàn tay mở (5 ngón)** | Chuyển sang Chế độ Hệ Thống | 🖐️ |

---

### 🛠️ Cài Đặt

Dự án yêu cầu Python 3.8 trở lên.

1.  Clone repository này về máy của bạn:
    ```bash
    git clone https://github.com/[GitHub-Username-Cua-Ban]/AirController.git
    cd AirController
    ```
2.  Cài đặt các thư viện cần thiết bằng lệnh sau:
    ```bash
    pip install -r requirements.txt
    ```
    *(Để làm điều này, hãy tạo một file tên là `requirements.txt` và dán các dòng sau vào:)*
    ```
    opencv-python
    mediapipe
    pyautogui
    numpy
    pynput
    pycaw
    screen-brightness-control
    ```
    *(Lưu ý: `pycaw` để điều khiển âm lượng chỉ hoạt động trên Windows. Trên các hệ điều hành khác, tính năng này sẽ tự động bị vô hiệu hóa.)*

---

### 🚀 Sử Dụng

Chạy file chính để bắt đầu chương trình:
```bash
python app.py
```
Đưa tay của bạn vào trước webcam và bắt đầu điều khiển! Nhấn `ESC` để thoát.

---

### 🔧 Tùy Chỉnh

Bạn có thể dễ dàng thay đổi các thông số như tốc độ chuột, độ nhạy, ngưỡng cử chỉ, v.v. ngay trong khối `CONFIGURATION` ở đầu file `app.py`.

---

### ❤️ Ghi Nhận

Dự án này được lên ý tưởng và định hướng phát triển bởi **Duong Van**.

Quá trình hiện thực hóa code được tăng tốc và hoàn thiện với sự hỗ trợ của AI Assistant (Google AI). Mô hình hợp tác này thể hiện khả năng làm chủ công cụ AI hiện đại để biến ý tưởng thành sản phẩm một cách hiệu quả.

---
