
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
    gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)  # suaviza ruído preservando bordas
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Gabor filters
    gabor_sum = np.zeros_like(gray, dtype=np.float32)
    for theta in np.arange(0, np.pi, np.pi / 8):
        kernel = cv2.getGaborKernel((31, 31), 4.0, theta, 10.0, 0.5)
        filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
        gabor_sum = np.maximum(gabor_sum, filtered)

    gabor_norm = cv2.normalize(gabor_sum, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Remove linhas (como antes)
    vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
    horz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    vert_lines = cv2.morphologyEx(gabor_norm, cv2.MORPH_OPEN, vert_kernel)
    horz_lines = cv2.morphologyEx(gabor_norm, cv2.MORPH_OPEN, horz_kernel)
    all_lines = cv2.add(vert_lines, horz_lines)

    no_lines = cv2.subtract(gabor_norm, all_lines)
    no_lines = cv2.equalizeHist(no_lines)

    # Threshold leve
    _, binary = cv2.threshold(no_lines, 50, 255, cv2.THRESH_BINARY)

    # FILTRO DE ÁREA — remove contornos pequenos (ruído)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cleaned = np.zeros_like(binary)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # ajusta esse valor conforme a sua imagem
            cv2.drawContours(cleaned, [cnt], -1, 255, -1)

    cv2.imwrite(output_path, cleaned)
    return cleaned

# Processa todas as imagens
filtered_images = []
for path in image_paths:
    filename = os.path.basename(path)
    output_path = os.path.join("filtered_colums_from_raw", f"filtered_{filename}")
    filtered = enhance_fingerprints(path, output_path)
    filtered_images.append((filename, filtered))