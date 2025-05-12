import os
import cv2
import numpy as np
import json

data_dir = "fingerprints_data"
corrected_output_dir = "corrected_marked_images"
corrected_data_dir = "corrected_fingerprints_data"
os.makedirs(corrected_output_dir, exist_ok=True)
os.makedirs(corrected_data_dir, exist_ok=True)
def fixing_redbox(json_data_path, corrected_output_path, corrected_json_output):
    # Carrega os dados originais
    with open(json_data_path, 'r') as f:
        data = json.load(f)

    image_path = data['image_path']
    fingerprints = data['fingerprints']

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10)

    fingerprints.sort(key=lambda fp: fp['yi'])

    corrected_fingerprints = []

    # Ajusta as digitais vermelhas, preserva verdes
    for i, fp in enumerate(fingerprints):
        yi, yf = fp['yi'], fp['yf']
        x, w, cor = fp['x'], fp['w'], fp['color']

        if cor == 'green':
            cv2.rectangle(image, (x, yi), (x+w, yf), (0,255,0), 2)
            corrected_fingerprints.append({'x': int(x), 'yi': int(yi), 'yf': int(yf), 'w': int(w), 'color': cor})
            continue

        # Ajuste superior usando digital anterior
        if i > 0:
            prev_fp = fingerprints[i-1]
            regiao_superior = thresh[prev_fp['yf']:yi, x:x+w]
            if regiao_superior.shape[0] > 5:
                proj = np.sum(regiao_superior == 255, axis=1)
                centro_escuro = np.argmin(proj)
                yi = prev_fp['yf'] + int(centro_escuro)

        # Ajuste inferior usando digital posterior
        if i < len(fingerprints)-1:
            next_fp = fingerprints[i+1]
            regiao_inferior = thresh[yf:next_fp['yi'], x:x+w]
            if regiao_inferior.shape[0] > 5:
                proj = np.sum(regiao_inferior == 255, axis=1)
                centro_escuro = np.argmin(proj)
                yf = yf + int(centro_escuro)

        cv2.rectangle(image, (x, yi), (x+w, yf), (0,0,255), 2)

        corrected_fingerprints.append({'x': int(x), 'yi': int(yi), 'yf': int(yf), 'w': int(w), 'color': cor})

    cv2.imwrite(corrected_output_path, image)

    # Salva os dados corrigidos no novo json
    corrected_data = {
        'image_path': image_path,
        'fingerprints': corrected_fingerprints
    }
    with open(corrected_json_output, 'w') as f:
        json.dump(corrected_data, f, indent=4)


# Aplicando automaticamente para todas as imagens JSON no diretório
for json_file in os.listdir(data_dir):
    if json_file.endswith(".json"):
        json_data_path = os.path.join(data_dir, json_file)

        # Nome da imagem com caixas corrigidas
        base_name = os.path.splitext(json_file)[0]
        corrected_output_path = os.path.join(
            corrected_output_dir, f"corrected_{base_name}.png")

        corrected_json_output = os.path.join(
            corrected_data_dir, f"corrected_{json_file}")

        fixing_redbox(json_data_path, corrected_output_path, corrected_json_output)


