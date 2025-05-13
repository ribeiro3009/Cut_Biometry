import cv2
import numpy as np
import os
import json

def detect_and_mark_fingerprints(image_path, output_path, data_output):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Não foi possível carregar a imagem: {image_path}")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  kernel, iterations=1)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = gray.shape
    Y_min = int(0.05 * height) if height > 1500 else int(0.10 * height)
    Y_max = int(0.15 * height) if height > 1500 else int(0.20 * height)
    minimum_length = int(0.3 * width)

    fingerprint_data = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        yi, yf = y, y + h
        altura = yf - yi

        if altura < Y_min or w < minimum_length:
            continue

        if altura > Y_max:
            cor = 'red'
            roi = thresh[yi:yf, x:x+w]
            projection = np.sum(roi == 255, axis=1)

            min_val = np.min(projection)
            max_val = np.max(projection)
            threshold = min_val + 0.21* (max_val - min_val)

            splits = []
            start = None
            for i, val in enumerate(projection):
                if val > threshold:
                    if start is None:
                        start = i
                else:
                    if start is not None:
                        end = i
                        if end - start >= Y_min:
                            splits.append((start, end))
                        start = None

            for s_yi, s_yf in splits:
                abs_yi, abs_yf = yi + s_yi, yi + s_yf
                fingerprint_data.append({'x': x, 'yi': abs_yi, 'yf': abs_yf, 'w': w, 'color': cor})
                cv2.rectangle(image, (x, abs_yi), (x+w, abs_yf), (0,0,255),2)

        else:
            cor = 'green'
            fingerprint_data.append({'x': x, 'yi': yi, 'yf': yf, 'w': w, 'color': cor})
            cv2.rectangle(image, (x, yi), (x+w, yf), (0,255,0),2)

    cv2.imwrite(output_path, image)

    # Salva informações
    data = {'image_path': image_path, 'fingerprints': fingerprint_data}
    with open(data_output, 'w') as f:
        json.dump(data, f, indent=4)

# Execução em batch
input_dir = "filtered_colums_from_raw"
output_dir = "marked_images_raw"
data_dir = "fingerprints_data"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

input_files = [
    "filtered_Ficha1_colum1_5.jpg",
    "filtered_Ficha1_colum2_5.jpg",
    "filtered_Ficha2_1_colum1_5.jpg",
    "filtered_Ficha2_1_colum2_5.jpg",
    "filtered_Ficha2_colum1_5.jpg",
    "filtered_Ficha2_colum2_5.jpg",
    "filtered_Ficha3_1_colum2_10.jpg",
    "filtered_Ficha3_colum2_10.jpg",
    "filtered_ficha1_1_colum2_5.jpg",
    "filtered_ficha1_1_colum1_5.jpg",
]

for filename in input_files:
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, f"marked_{filename}")
    data_output = os.path.join(data_dir, f"{filename}.json")

    detect_and_mark_fingerprints(input_path, output_path, data_output)

print("Processamento completo! Imagens salvas em:", output_dir)
