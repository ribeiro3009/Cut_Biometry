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
    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 10)

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

        corrected_fingerprints.append({'x': int(x), 'yi': int(yi), 'yf': int(yf), 'w': int(w), 'color': cor})

    # Definir altura máxima permitida para digitais
    Y_max = int(0.15 * height) if height > 1500 else int(0.25 * height)

    # Calcula média das digitais normais (não azuis)
    normal_heights = [fp['yf'] - fp['yi'] for fp in corrected_fingerprints if (fp['yf'] - fp['yi']) <= Y_max]
    avg_normal_height = np.mean(normal_heights) if normal_heights else Y_max

    final_fingerprints = []

    for fp in corrected_fingerprints:
        yi, yf, x, w, cor = fp['yi'], fp['yf'], fp['x'], fp['w'], fp['color']
        altura_fp = yf - yi

        if cor == 'red' and altura_fp > Y_max:
            num_digitais = int(np.ceil(altura_fp / Y_max))

            cortes = [yi]

            for n in range(1, num_digitais):
                expected_y = yi + int(n * avg_normal_height)

                margin = 40
                faixa_inicio = max(yi, expected_y - margin)
                faixa_fim = min(yf, expected_y + margin)

                faixa = thresh[faixa_inicio:faixa_fim, x:x+w]
                proj_faixa = np.sum(faixa == 255, axis=1)

                if len(proj_faixa) == 0:
                    corte_y = expected_y
                else:
                    corte_local = np.argmin(proj_faixa)
                    corte_y = faixa_inicio + corte_local

                cortes.append(corte_y)

            cortes.append(yf)

            for idx in range(len(cortes)-1):
                yi_corr, yf_corr = cortes[idx], cortes[idx+1]
                
                final_fingerprints.append({
                            'x': int(x),
                            'yi': int(yi_corr),
                            'yf': int(yf_corr),
                            'w': int(w),
                            'color': "blue"
                        })

                cv2.rectangle(image, (x, yi_corr), (x+w, yf_corr), (255,0,0), 2)
        else:
            final_fingerprints.append({
                            'x': int(x),
                            'yi': int(yi),
                            'yf': int(yf),
                            'w': int(w),
                            'color': cor
                        })

            cor_retangulo = (0, 255, 0) if cor == 'green' else (0,0,255)
            cv2.rectangle(image, (x, yi), (x+w, yf), cor_retangulo, 2)

    cv2.imwrite(corrected_output_path, image)

    corrected_data = {
        'image_path': image_path,
        'fingerprints': final_fingerprints
    }
    with open(corrected_json_output, 'w') as f:
        json.dump(corrected_data, f, indent=4)

'''
for json_file in os.listdir(data_dir):
    if json_file.endswith(".json"):
        json_data_path = os.path.join(data_dir, json_file)

        base_name = os.path.splitext(json_file)[0]
        corrected_output_path = os.path.join(
            corrected_output_dir, f"corrected_{base_name}.png")

        corrected_json_output = os.path.join(
            corrected_data_dir, f"corrected_{json_file}")

        fixing_redbox(json_data_path, corrected_output_path, corrected_json_output)
'''