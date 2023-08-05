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

    num_areas = len(selected_areas)
    color_frequency_matrix = np.zeros((num_areas, 256 * 14), dtype=int)

    for idx, (_, rgb_values) in enumerate(selected_areas):
        for r, g, b in rgb_values:
            color_frequency_matrix[idx, r] += 1
            color_frequency_matrix[idx, g + 256] += 1
            color_frequency_matrix[idx, b + 512] += 1

            c, m, y, k = cmyk_conversion((r, g, b))
            color_frequency_matrix[idx, int(c * 255) + 768] += 1
            color_frequency_matrix[idx, int(m * 255) + 1024] += 1
            color_frequency_matrix[idx, int(y * 255) + 1280] += 1
            color_frequency_matrix[idx, int(k * 255) + 1536] += 1

            h, s, i = rgb_to_hsi(r, g, b)
            color_frequency_matrix[idx, int(h * 255) + 1792] += 1
            color_frequency_matrix[idx, int(s * 255) + 2048] += 1
            color_frequency_matrix[idx, int(i * 255) + 2304] += 1

            h, s, l = rgb_to_hsl(r, g, b)
            color_frequency_matrix[idx, int(h * 255) + 2560] += 1
            color_frequency_matrix[idx, int(s * 255) + 2816] += 1
            color_frequency_matrix[idx, int(l * 255) + 3072] += 1

            gray = rgb_to_gray(r, g, b)
            color_frequency_matrix[idx, int(gray) + 3328] += 1

    df = pd.DataFrame(color_frequency_matrix)
    df.columns = (
        [f"R_{i}" for i in range(256)]
        + [f"G_{i}" for i in range(256)]
        + [f"B_{i}" for i in range(256)]
        + [f"C_{i}" for i in range(256)]
        + [f"M_{i}" for i in range(256)]
        + [f"Y_{i}" for i in range(256)]
        + [f"K_{i}" for i in range(256)]
        + [f"H_HSI_{i}" for i in range(256)]
        + [f"S_HSI_{i}" for i in range(256)]
        + [f"I_{i}" for i in range(256)]
        + [f"H_HSL_{i}" for i in range(256)]
        + [f"S_HSL_{i}" for i in range(256)]
        + [f"L_{i}" for i in range(256)]
        + [f"GRAY_{i}" for i in range(256)]
    )
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

def rgb_to_hsi(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0

    w = 0.5 * ((r-g)+(r-b)) / (np.sqrt((r-g)**2 + (r-b)*(g-b)) + 1e-6)
    cos_inverse = np.arccos(w)


    if b <= g:
        h = cos_inverse
    else:
        h = 2*np.pi - cos_inverse

    min_val = min([r, g, b])
    s = 1 - (3 * min_val / (r + g + b))

    i = (r + g + b) / 3

    return h, s, i

def hsi_conversion(rgb):
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    r_g_b_sum = r + g + b

    i = r_g_b_sum / 3
    s = 1 - 3 / (r_g_b_sum + 1e-6) * min(r, g, b)

    sqrt_val = ((r - g) ** 2 + (r - b) * (g - b)) ** 0.5
    if b <= g:
        h = np.arccos((0.5 * ((r - g) + (r - b))) / (sqrt_val + 1e-6)) / (2 * np.pi)
    else:
        h = 1 - np.arccos((0.5 * ((r - g) + (r - b))) / (sqrt_val + 1e-6)) / (2 * np.pi)

    if np.isnan(h):
        h = 0

    return h, s, i



def rgb_to_hsl(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    l = (max_val + min_val) / 2.0

    if max_val == min_val:
        h = 0
        s = 0
    else:
        diff = max_val - min_val
        if l > 0.5:
            s = diff / (2.0 - max_val - min_val)
        else:
            s = diff / (max_val + min_val)

        if max_val == r:
            h = (g - b) / diff + (g < b) * 6
        elif max_val == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4

        h /= 6

    return h, s, l

def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.5870 * g + 0.1140 * b


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

    cmky_frequency_matrix = np.zeros((len(selected_areas), 256 * 4), dtype=int)

    for idx, rgb_values in enumerate(selected_areas):
        for r, g, b in rgb_values[1]:
            c, m, y, k = cmyk_conversion((r, g, b))
            cmky_frequency_matrix[idx, int(c * 255)] += 1
            cmky_frequency_matrix[idx, int(m * 255) + 256] += 1
            cmky_frequency_matrix[idx, int(y * 255) + 512] += 1
            cmky_frequency_matrix[idx, int(k * 255) + 768] += 1

    df = pd.DataFrame(cmky_frequency_matrix)
    df.columns = [f"C_{i}" for i in range(256)] + [f"M_{i}" for i in range(256)] + [f"Y_{i}" for i in range(256)] + [f"K_{i}" for i in range(256)]
    display_sheet(df)





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
    root.title("Aaron's Insane Colorimetric app")

    header_label = tk.Label(root, text="Select an image to extract RGB values:")
    header_label.pack(pady=10)

    select_button = tk.Button(root, text="Select Image", command=select_image)
    select_button.pack(pady=5)

    canvas = tk.Canvas(root, bg="white")
    canvas.pack()

    sheet_button = tk.Button(root, text="RGB, CMYK, HSI, HSL and gray Values Sheet", command=show_rgb_sheet)
    sheet_button.pack(pady=5)
    
    
    cmyk_histogram_button = tk.Button(root, text="Plot CMYK Histogram", command=lambda: plot_cmyk_histogram(selected_areas[-1][1]))
    cmyk_histogram_button.pack(pady=5)

    root.mainloop()
