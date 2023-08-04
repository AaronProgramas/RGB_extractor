import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from colorsys import rgb_to_hsv, rgb_to_hls

selected_areas = []
image = None

def extract_color_values_from_area(selected_area):
    pixels = selected_area.getdata()
    color_values = []
    for pixel in pixels:
        rgb = pixel[:3]
        hsi = rgb_to_hsv(*rgb)
        hsl = rgb_to_hls(*rgb)
        cmyk = rgb_to_cmyk(*rgb)
        gray = rgb_to_gray(*rgb)
        color_values.append((*rgb, *hsi, *hsl, *cmyk, gray))
    return color_values

def rgb_to_cmyk(r, g, b):
    c = 1 - (r / 255)
    m = 1 - (g / 255)
    y = 1 - (b / 255)
    k = min(c, m, y)
    if k == 1:
        return 0, 0, 0, 1
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return c, m, y, k

def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.587 * g + 0.114 * b

def select_image():
    global image
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    if file_path:
        image = Image.open(file_path)
        display_image(image)

def display_image(image):
    canvas.image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

    def on_click(event):
        x, y = event.x, event.y
        selected_area = image.crop((x - 10, y - 10, x + 10, y + 10))
        draw_red_circle(x, y)
        color_values = extract_color_values_from_area(selected_area)
        selected_areas.append((selected_area, color_values))
        plot_area_histogram(color_values)

    canvas.bind("<Button-1>", on_click)

def draw_red_circle(x, y):
    x1, y1 = x - 10, y - 10
    x2, y2 = x + 10, y + 10
    canvas.create_oval(x1, y1, x2, y2, outline="red")

def show_color_sheet():
    if not selected_areas:
        messagebox.showinfo("No Areas Selected", "Please select areas on the image first.")
        return

    data = []
    for idx, (_, color_values) in enumerate(selected_areas, 1):
        data.extend([[f"Selected Area {idx}", *color] for color in color_values])

    df = pd.DataFrame(data, columns=[
        "Area", "R", "G", "B",
        "Hue", "Saturation (HSI)", "Value", 
        "Hue", "Saturation (HSL)", "Lightness",
        "Cyan", "Magenta", "Yellow", "Black (CMYK)",
        "Grayscale"
    ])
    display_sheet(df)

def save_to_text_file(df):
    file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(df.to_string(index=False))

def save_to_excel_file(df):
    file_path = filedialog.asksaveasfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)

def display_sheet(df):
    top = tk.Toplevel(root)
    top.title("Color Values Sheet")

    table = tk.Text(top, wrap=tk.NONE)
    table.pack()

    table_str = df.to_string(index=False)
    table.insert(tk.END, table_str)

    save_text_button = tk.Button(top, text="Save to Text File", command=lambda: save_to_text_file(df))
    save_text_button.pack()

    save_excel_button = tk.Button(top, text="Save to Excel File", command=lambda: save_to_excel_file(df))
    save_excel_button.pack()

def plot_histogram():
    if not selected_areas:
        messagebox.showinfo("No Areas Selected", "Please select areas on the image first.")
        return

def plot_area_histogram(color_values):
    plt.figure(figsize=(12, 8))
    np_color_values = np.array(color_values)
    
    for i, label in enumerate(["R", "G", "B", "Hue (HSI)", "Saturation (HSI)", "Value", 
                               "Hue (HSL)", "Saturation (HSL)", "Lightness", 
                               "Cyan (CMYK)", "Magenta (CMYK)", "Yellow (CMYK)", "Black (CMYK)", "Grayscale"]):
        plt.subplot(3, 5, i + 1)
        plt.hist(np_color_values[:, i], bins=256, histtype='step', alpha=0.7)
        plt.xlabel(label)
        plt.ylabel('number of pixels')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Professor Aaron's Magical Color Analyzer")

    header_label = tk.Label(root, text="Select an image to extract color values:")
    header_label.pack(pady=10)

    select_button = tk.Button(root, text="Select Image", command=select_image)
    select_button.pack(pady=5)

    canvas = tk.Canvas(root, bg="white")
    canvas.pack()

    sheet_button = tk.Button(root, text="Show Color Values Sheet", command=show_color_sheet)
    sheet_button.pack(pady=5)

    histogram_button = tk.Button(root, text="Plot Color Histogram", command=plot_histogram)
    histogram_button.pack(pady=5)

    root.mainloop()
