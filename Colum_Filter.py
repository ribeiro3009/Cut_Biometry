import cv2
import numpy as np
import os
from glob import glob
from matplotlib import pyplot as plt

# Diretório com as imagens
input_dir = "cutted_colums_raw"

# Lista de imagens enviadas
image_paths = sorted(glob(os.path.join(input_dir, "*.jpg")))

# Filtro potente e refinado para realçar digitais
def enhance_fingerprints(image_path, output_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro ao ler imagem: {image_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold sensível a detalhes
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 7)

    # Remoção de linhas verticais/horizontais com kernel pequeno
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))

    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    all_lines = cv2.bitwise_or(vertical_lines, horizontal_lines)

    # Remove as linhas da binarizada
    no_lines = cv2.bitwise_and(thresh, cv2.bitwise_not(all_lines))

    # Remoção leve de ruído sem perder cristas
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    cleaned = cv2.morphologyEx(no_lines, cv2.MORPH_OPEN, kernel_clean)

    # 🚫 Sem dilatação — preserva os contornos reais
    cv2.imwrite(output_path, cleaned)
    return cleaned



# Processa todas as imagens
filtered_images = []
for path in image_paths:
    filename = os.path.basename(path)
    output_path = os.path.join("filtered_colums_from_raw", f"filtered_{filename}")
    filtered = enhance_fingerprints(path, output_path)
    filtered_images.append((filename, filtered))

