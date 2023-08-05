import tkinter as tk
from tkinter import filedialog
import cv2
import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk


def extract_rgb_vectors(image_path):
    try:
        # Read the image using opencv
        img = cv2.imread(image_path)

        # Extract RGB vectors from each pixel
        rgb_vectors = img.reshape((-1, 3))

        return rgb_vectors.tolist()
    except Exception as e:
        print(f"Error: {e}")
        return None

def on_upload_button_click():
    file_path = filedialog.askopenfilename()
    if file_path:
        image_path_var.set(file_path)
        update_image_preview()

def update_image_preview():
    path = image_path_var.get()
    if path:
        try:
            img = cv2.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (300, 300))
            photo = Image.fromarray(img)
            photo = ImageTk.PhotoImage(image=photo)
            image_preview_label.config(image=photo)
            image_preview_label.image = photo
        except Exception as e:
            print(f"Error: {e}")

def on_extract_button_click():
    image_path = image_path_var.get()
    if image_path:
        vectors = extract_rgb_vectors(image_path)
        if vectors is not None:
            print("RGB Vectors:")
            for vector in vectors:
                print(vector)

# Create the main application window
app = tk.Tk()
app.title("RGB Vector Extractor")

# Create and place widgets
image_path_var = tk.StringVar()
upload_button = tk.Button(app, text="Upload Image", command=on_upload_button_click)
upload_button.pack(pady=10)

extract_button = tk.Button(app, text="Extract RGB Vectors", command=on_extract_button_click)
extract_button.pack(pady=5)

image_preview_label = tk.Label(app)
image_preview_label.pack(pady=10)

app.mainloop()
