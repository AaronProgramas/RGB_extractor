import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import ndimage
import matplotlib.colors as colors

selected_areas = []
image = None

def extract_rgb_values_from_area(selected_area):
    pixels = selected_area.getdata()
    rgb_values = [pixel[:3] for pixel in pixels]
    return rgb_values

def extract_rgb_values(image, x, y, radius=10):
    rgb_values = []
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            if 0 <= i < image.width and 0 <= j < image.height:
                pixel = image.getpixel((i, j))
                rgb_values.append(pixel[:3])
    return rgb_values

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
        rgb_values = extract_rgb_values(image, x, y, radius=10)
        selected_areas.append((selected_area, rgb_values))
        plot_area_histogram(rgb_values)

    canvas.bind("<Button-1>", on_click)

def draw_red_circle(x, y):
    x1, y1 = x - 10, y - 10
    x2, y2 = x + 10, y + 10
    canvas.create_oval(x1, y1, x2, y2, outline="red")

def show_rgb_sheet():
    if not selected_areas:
        messagebox.showinfo("No Areas Selected", "Please select areas on the image first.")
        return

    data = []
    for idx, (selected_area, rgb_values) in enumerate(selected_areas, 1):
        data.extend([[f"Selected Area {idx}", *rgb] for rgb in rgb_values])

    df = pd.DataFrame(data, columns=["Area", "R", "G", "B"])
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
    top.title("RGB Values Sheet")

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

    # Placeholder for the histogram plot function
    pass

def plot_area_histogram(rgb_values):
    plt.figure()
    np_rgb_values = np.array(rgb_values)
    plt.hist(np_rgb_values[:, 0], bins=256, color='r', histtype='step', alpha=0.7, label="R")
    plt.hist(np_rgb_values[:, 1], bins=256, color='g', histtype='step', alpha=0.7, label="G")
    plt.hist(np_rgb_values[:, 2], bins=256, color='b', histtype='step', alpha=0.7, label="B")
    plt.xlabel('color value')
    plt.ylabel('number of pixels')
    plt.legend()
    plt.show()

def cmyk_conversion(rgb):
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    k = 1 - max(r, g, b)
    c = (1 - r - k) / (1 - k) if (1 - k) != 0 else 0
    m = (1 - g - k) / (1 - k) if (1 - k) != 0 else 0
    y = (1 - b - k) / (1 - k) if (1 - k) != 0 else 0
    return c, m, y, k

def display_cmky_tab(rgb_values):
    top = tk.Toplevel(root)
    top.title("CMYK Values")

    table = tk.Text(top, wrap=tk.NONE)
    table.pack()

    cmky_data = []
    for idx, rgb in enumerate(rgb_values, 1):
        c, m, y, k = cmyk_conversion(rgb)
        cmky_data.append([f"Selected Area {idx}", c, m, y, k])

    cmky_df = pd.DataFrame(cmky_data, columns=["Area", "C", "M", "Y", "K"])

    table_str = cmky_df.to_string(index=False)
    table.insert(tk.END, table_str)

    save_text_button = tk.Button(top, text="Save to Text File", command=lambda: save_to_text_file(cmky_df))
    save_text_button.pack()

    save_excel_button = tk.Button(top, text="Save to Excel File", command=lambda: save_to_excel_file(cmky_df))
    save_excel_button.pack()

# ... (Previous code remains the same)

def plot_cmyk_histogram(rgb_values):
    if not selected_areas:
        messagebox.showinfo("No Areas Selected", "Please select areas on the image first.")
        return

    c_values = []
    m_values = []
    y_values = []
    k_values = []

    for rgb in rgb_values:
        c, m, y, k = cmyk_conversion(rgb)
        c_values.append(c)
        m_values.append(m)
        y_values.append(y)
        k_values.append(k)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 4, 1)
    plt.hist(c_values, bins=100, range=(0.0, 1.0), histtype='stepfilled', color='cyan', label='Cyan')
    plt.title("Cyan")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.subplot(1, 4, 2)
    plt.hist(m_values, bins=100, range=(0.0, 1.0), histtype='stepfilled', color='magenta', label='Magenta')
    plt.title("Magenta")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.subplot(1, 4, 3)
    plt.hist(y_values, bins=100, range=(0.0, 1.0), histtype='stepfilled', color='yellow', label='Yellow')
    plt.title("Yellow")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.subplot(1, 4, 4)
    plt.hist(k_values, bins=100, range=(0.0, 1.0), histtype='stepfilled', color='black', label='Key (Black)')
    plt.title("Key (Black)")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()

    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Professor Aaron's Magic RGB Extractor")

    header_label = tk.Label(root, text="Select an image to extract RGB values:")
    header_label.pack(pady=10)

    select_button = tk.Button(root, text="Select Image", command=select_image)
    select_button.pack(pady=5)

    canvas = tk.Canvas(root, bg="white")
    canvas.pack()

    sheet_button = tk.Button(root, text="Show RGB Values Sheet", command=show_rgb_sheet)
    sheet_button.pack(pady=5)
    
    cmky_button = tk.Button(root, text="Show CMYK Values", command=lambda: display_cmky_tab(selected_areas[-1][1]))
    cmky_button.pack(pady=5)
    
    cmyk_histogram_button = tk.Button(root, text="Plot CMYK Histogram", command=lambda: plot_cmyk_histogram(selected_areas[-1][1]))
    cmyk_histogram_button.pack(pady=5)

    root.mainloop()
