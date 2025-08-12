# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk
# import os
# import cv2

# # === Nếu dùng YOLOv8 (.pt)
# try:
#     from ultralytics import YOLO
# except ImportError:
#     YOLO = None

# # === Biến toàn cục ===
# model_path = None
# model = None

# # === Chọn model từ file ===
# def select_model():
#     global model_path, model
#     path = filedialog.askopenfilename(
#         title="Chọn file model",
#         filetypes=[
#             ("Tất cả model", "*.pt *.h5 *.onnx *.pkl"),
#             ("YOLOv8 model", "*.pt"),
#             ("TensorFlow (.h5)", "*.h5"),
#             ("ONNX model", "*.onnx"),
#             ("Pickle (.pkl)", "*.pkl"),
#             ("Tất cả", "*.*")
#         ]
#     )
#     if path:
#         model_path = path
#         ext = os.path.splitext(path)[1].lower()

#         try:
#             if ext == ".pt" and YOLO is not None:
#                 model = YOLO(model_path)
#                 label_model.config(text=f"✅ Đã chọn YOLO: {os.path.basename(path)}")
#             else:
#                 model = None
#                 label_model.config(text=f"⚠️ Đã chọn: {os.path.basename(path)} (chưa hỗ trợ load)")
#         except Exception as e:
#             model = None
#             messagebox.showerror("Lỗi", f"Không thể load model:\n{e}")
#     else:
#         model_path = None
#         model = None
#         label_model.config(text="❌ Chưa chọn model")

# # === Dự đoán từ ảnh bằng YOLO ===
# def detect_objects(image):
#     global model
#     if not model:
#         return image

#     try:
#         results = model.predict(source=image, save=False, conf=0.4, imgsz=640)[0]
#         names = model.names

#         for box in results.boxes:
#             cls_id = int(box.cls[0])
#             conf = float(box.conf[0])
#             label = f"{names[cls_id]} {conf:.2f}"
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(image, label, (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#     except Exception as e:
#         messagebox.showerror("Lỗi", f"Lỗi khi detect: {e}")

#     return image

# # === Chọn ảnh và dự đoán ===
# def open_image_and_predict():
#     if not model_path or not model:
#         messagebox.showwarning("Thiếu model", "Vui lòng chọn model trước.")
#         return

#     path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
#     if not path:
#         return

#     image = cv2.imread(path)
#     image = detect_objects(image)
#     cv2.imshow("Dự đoán ảnh", image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# # === Dự đoán qua camera ===
# def open_camera():
#     if not model_path or not model:
#         messagebox.showwarning("Thiếu model", "Vui lòng chọn model trước.")
#         return

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         messagebox.showerror("Lỗi", "Không thể mở camera")
#         return

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = detect_objects(frame)
#         cv2.imshow("Camera - Nhận diện", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# # === Giao diện Tkinter ===
# root = tk.Tk()
# root.title("Quản lý ra vào phòng - Object Detection")
# root.geometry("900x600")
# root.configure(bg="#e6f2ff")

# label_title = tk.Label(root, text="QUẢN LÝ RA VÀO PHÒNG CHUNG CƯ",
#                        font=("Arial", 16, "bold"), bg="#e6f2ff", fg="#003366")
# label_title.pack(pady=15)

# label_model = tk.Label(root, text="❌ Chưa chọn model", bg="#e6f2ff", fg="red", font=("Arial", 11))
# label_model.pack()

# frame_buttons = tk.Frame(root, bg="#e6f2ff")
# frame_buttons.pack(pady=30)

# btn_select_model = tk.Button(frame_buttons, text="📂 Chọn model (.pt, .h5...)", width=25, height=2,
#                              bg="#3399ff", fg="white", command=select_model)
# btn_select_model.grid(row=0, column=0, padx=10, pady=10)

# btn_camera = tk.Button(frame_buttons, text="📷 Mở camera & nhận diện", width=25, height=2,
#                        bg="#0080ff", fg="white", command=open_camera)
# btn_camera.grid(row=0, column=1, padx=10, pady=10)

# btn_file = tk.Button(frame_buttons, text="🖼️ Chọn ảnh & dự đoán", width=25, height=2,
#                      bg="#4da6ff", fg="white", command=open_image_and_predict)
# btn_file.grid(row=1, column=0, columnspan=2, pady=10)

# root.mainloop()

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import csv
from datetime import datetime
import sys

# === Nếu dùng YOLOv8 (.pt) ===
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

model_path = None
model = None
camera_running = False

# === Ghi log CSV ===
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "background.jpg")

# === Hàm hỗ trợ tìm ảnh khi đóng gói .exe ===

def save_success_log(name="Không rõ"):
    now = datetime.now()
    day = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")
    filename = f"{day}.csv"

    header = ['Tên', 'Ngày', 'Giờ']
    row = [name, day, time_str]

    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

# === Chọn model ===
def select_model():
    global model_path, model
    path = filedialog.askopenfilename(
        title="Chọn file model",
        filetypes=[
            ("YOLOv8 model", "*.pt"),
            ("Tất cả model", "*.pt *.h5 *.onnx *.pkl"),
            ("Tất cả", "*.*")
        ]
    )
    if path:
        model_path = path
        ext = os.path.splitext(path)[1].lower()

        try:
            if ext == ".pt" and YOLO is not None:
                model = YOLO(model_path)
                label_model.config(text=f"✅ Đã chọn YOLO: {os.path.basename(path)}")
            else:
                model = None
                label_model.config(text=f"⚠️ Đã chọn: {os.path.basename(path)} (chưa hỗ trợ load)")
        except Exception as e:
            model = None
            messagebox.showerror("Lỗi", f"Không thể load model:\n{e}")
    else:
        model_path = None
        model = None
        label_model.config(text="❌ Chưa chọn model")

# === Dự đoán ===
def detect_objects(image):
    global model
    if not model:
        return image, False, "Không rõ"

    found = False
    first_name = "Không rõ"
    try:
        results = model.predict(source=image, save=False, conf=0.4, imgsz=640)[0]
        names = model.names

        if results.boxes:
            found = True
            first_box = results.boxes[0]
            cls_id = int(first_box.cls[0])
            first_name = names[cls_id]

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{names[cls_id]} {conf:.2f}"
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi detect: {e}")

    return image, found, first_name

# === Overlay thông báo ===
def show_detection_result(window, success):
    msg = "✅ ĐÃ NHẬN DIỆN THÀNH CÔNG" if success else "❌ NHẬN DIỆN KHÔNG THÀNH CÔNG"
    color = "green" if success else "red"
    bg = "#ccffcc" if success else "#ffcccc"

    overlay = tk.Label(window, text=msg, font=("Arial", 16, "bold"), bg=bg, fg=color)
    overlay.place(relx=0.5, rely=0.95, anchor="center")


# === Căn giữa cửa sổ ===
def center_window(window, w, h):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

# === Ảnh + Nhận diện ===
def open_image_and_predict():
    if not model_path or not model:
        messagebox.showwarning("Thiếu model", "Vui lòng chọn model trước.")
        return

    path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if not path:
        return

    image = cv2.imread(path)
    image = cv2.resize(image, (640, 640))
    image, found, name = detect_objects(image)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    tk_img = ImageTk.PhotoImage(pil_img)

    img_window = tk.Toplevel(root)
    img_window.title("Kết quả nhận diện")
    center_window(img_window, 660, 700)
    img_window.configure(bg="#ffffff")
    img_window.resizable(False, False)

    img_label = tk.Label(img_window, image=tk_img)
    img_label.image = tk_img
    img_label.pack(pady=10)

    show_detection_result(img_window, success=found)
    if found:
        save_success_log(name)

# === Nhận diện từ camera ===
def open_camera():
    global camera_running
    if not model_path or not model:
        messagebox.showwarning("Thiếu model", "Vui lòng chọn model trước.")
        return

    if camera_running:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Lỗi", "Không thể mở camera")
        return

    camera_running = True

    cam_window = tk.Toplevel(root)
    cam_window.title("Camera - Nhận diện")
    center_window(cam_window, 660, 700)
    cam_window.resizable(False, False)

    lbl_cam = tk.Label(cam_window)
    lbl_cam.pack(pady=10)

    def update_frame():
        if not camera_running:
            return

        ret, frame = cap.read()
        if not ret:
            cap.release()
            return

        frame = cv2.resize(frame, (640, 640))
        frame, found, name = detect_objects(frame)

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        tk_img = ImageTk.PhotoImage(pil_img)

        lbl_cam.imgtk = tk_img
        lbl_cam.configure(image=tk_img)

        if not hasattr(update_frame, "shown"):
            show_detection_result(cam_window, success=found)
            if found:
                save_success_log(name)
            update_frame.shown = True

        cam_window.after(30, update_frame)

    def on_close():
        global camera_running
        camera_running = False
        cap.release()
        cam_window.destroy()

    cam_window.protocol("WM_DELETE_WINDOW", on_close)
    update_frame()

# === UI chính ===
root = tk.Tk()
root.title("Quản lý ra vào phòng - Object Detection")
root.geometry("900x600")

# Ảnh nền
try:
    bg_img = Image.open(BACKGROUND_PATH)
    bg_img = bg_img.resize((900, 600))
    bg_photo = ImageTk.PhotoImage(bg_img)

    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    print("⚠ Không thể tải ảnh nền.")

# Căn giữa UI chính
def center_main():
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
root.after(100, center_main)


# UI control
label_title = tk.Label(root, text="QUẢN LÝ RA VÀO PHÒNG CHUNG CƯ",
                       font=("Arial", 16, "bold"), bg="#e6f2ff", fg="#003366")
label_title.place(x=250, y=30)

label_model = tk.Label(root, text="❌ Chưa chọn model", bg="#e6f2ff", fg="red", font=("Arial", 11))
label_model.place(x=350, y=70)

btn_select_model = tk.Button(root, text="📂 Chọn model", width=20, height=2,
                             bg="#3399ff", fg="white", command=select_model)
btn_select_model.place(x=100, y=150)

btn_camera = tk.Button(root, text="📷 Camera & nhận diện", width=20, height=2,
                       bg="#0080ff", fg="white", command=open_camera)
btn_camera.place(x=350, y=150)

btn_file = tk.Button(root, text="🖼️ Ảnh & dự đoán", width=20, height=2,
                     bg="#4da6ff", fg="white", command=open_image_and_predict)
btn_file.place(x=600, y=150)

root.mainloop()
