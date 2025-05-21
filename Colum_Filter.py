import cv2
import numpy as np
import os
from glob import glob
from matplotlib import pyplot as plt

# Diretório com as imagens
input_dir = "cutted_colums_raw"

# Lista de imagens enviadas
image_paths = sorted(glob(os.path.join(input_dir, "*.jpg")))

def enhance_fingerprints(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro ao ler imagem: {image_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Contraste local para digitais mais claras
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Threshold adaptativo mais agressivo
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 10  # janelas maiores ajudam em regiões "vazias"
    )

    # Remoção de linhas (como antes)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    all_lines = cv2.bitwise_or(vertical_lines, horizontal_lines)

    no_lines = cv2.bitwise_and(thresh, cv2.bitwise_not(all_lines))

    # ***Preenchimento dos miolos das digitais*** com closing (fecha falhas finas)
    kernel_fill = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    filled = cv2.morphologyEx(no_lines, cv2.MORPH_CLOSE, kernel_fill)

    # ***Suavização final***: remove ruído isolado sem comer bordas
    smoothed = cv2.medianBlur(filled, 3)

    cv2.imwrite(output_path, smoothed)
    return smoothed


# Processa todas as imagens
filtered_images = []
for path in image_paths:
    filename = os.path.basename(path)
    output_path = os.path.join("filtered_colums_from_raw", f"filtered_{filename}")
    filtered = enhance_fingerprints(path, output_path)
    filtered_images.append((filename, filtered))

