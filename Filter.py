import cv2
import numpy as np

def remove_lines_keep_fingerprints(image_path):
    # Carregar imagem
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Binarização adaptativa para melhor definição das digitais
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 21, 5)

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
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fingerprints_only = cv2.dilate(fingerprints_only, kernel_dilate, iterations=1)

    return fingerprints_only

# Exemplo de uso
#result = remove_lines_keep_fingerprints("Fichas/Ficha1_1.jpg")
#cv2.imwrite("Filtradas/filtered_2_1_1.jpg", result)