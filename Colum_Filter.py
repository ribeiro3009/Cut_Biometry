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
    # Carregar imagem
    img = cv2.imread(image_path)
    if img is None:
        print(f"Erro ao ler imagem: {image_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    # Binarização adaptativa para melhor definição das digitais
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 41, 8)

    # Kernel para linhas verticais e horizontais
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))

    # Detectar linhas
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)

    # Combinar linhas verticais e horizontais
    all_lines = cv2.bitwise_or(vertical_lines, horizontal_lines)

    # Remover linhas combinadas da imagem binarizada
    fingerprints_only = cv2.bitwise_and(thresh, cv2.bitwise_not(all_lines))

    # Remover pequenos ruídos
    kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fingerprints_only = cv2.morphologyEx(fingerprints_only, cv2.MORPH_OPEN, kernel_small)

    # Dilatação final para destacar digitais
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
    fingerprints_only = cv2.dilate(fingerprints_only, kernel_dilate, iterations=1)

    # Salvar resultado
    cv2.imwrite(output_path, fingerprints_only)
    return fingerprints_only



# Processa todas as imagens
filtered_images = []
for path in image_paths:
    filename = os.path.basename(path)
    output_path = os.path.join("filtered_colums_from_raw", f"filtered_{filename}")
    filtered = enhance_fingerprints(path, output_path)
    filtered_images.append((filename, filtered))

