import cv2
import numpy as np
import os

def detect_and_mark_fingerprints(image_path, output_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Não foi possível carregar a imagem: {image_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 5000
    fingerprint_contours = [c for c in contours if cv2.contourArea(c) > min_area]

    for cnt in fingerprint_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(output_path, image)

# Caminhos relativos (recomendado para organização)
input_dir = "cutted_colums"
output_dir = "marked_images"
os.makedirs(output_dir, exist_ok=True)

input_files = [
    "filtered_2_1_1_colum1.jpg",
    "filtered_2_1_1_colum2.jpg",
    "filtered_2_1_colum1.jpg",
    "filtered_2_1_colum2.jpg",
    "filtered_2_2_1_colum1.jpg",
    "filtered_2_2_1_colum2.jpg",
    "filtered_2_2_colum1.jpg",
    "filtered_2_2_colum2.jpg",
    "filtered_2_3_1_colum2.jpg",
    "filtered_2_3_colum2.jpg"
]

for filename in input_files:
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, f"marked_{filename}")
    detect_and_mark_fingerprints(input_path, output_path)

print("Processamento completo! Imagens salvas em:", output_dir)
