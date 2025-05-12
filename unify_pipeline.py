#!/usr/bin/env python3
import os
import cv2
import json
import argparse

import Filter
import Classification
import Colum_Marker
from Colum_Cut import cut_columns
from Colum_Filter import enhance_fingerprints
from identificador2 import detect_and_mark_fingerprints
from Red_box_fixer import fixing_redbox

def process_ficha(image_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]

    # 1) Filtragem geral da ficha
    filtered = Filter.remove_lines_keep_fingerprints(image_path)
    filtered_path = os.path.join(output_dir, f"{base}_filtered.png")
    cv2.imwrite(filtered_path, filtered)
    print("– imagem filtrada salva em", filtered_path)

    # 2) Classificação da ficha
    classification = Classification.classifica_ficha(filtered_path)
    print("– classificação:", classification)

    # 3) Marcação das colunas
    col1_coords, col2_coords = Colum_Marker.mark_columns(filtered_path, classification)
    print(f"– colunas em {col1_coords}, {col2_coords}")

    # 4) Corte das colunas na imagem original
    cols_raw_dir = os.path.join(output_dir, "columns_raw")
    os.makedirs(cols_raw_dir, exist_ok=True)
    cut_columns(image_path, col1_coords, col2_coords, output_dir=cols_raw_dir)
    print("– colunas cortadas em", cols_raw_dir)

    # 4.1) Filtragem refinada das colunas (realça digitais)
    cols_filt_dir = os.path.join(output_dir, "columns_filtered")
    os.makedirs(cols_filt_dir, exist_ok=True)
    filtered_cols = []
    for fname in os.listdir(cols_raw_dir):
        if not fname.lower().endswith((".jpg", ".png")):
            continue
        raw_path  = os.path.join(cols_raw_dir, fname)
        filt_path = os.path.join(cols_filt_dir, f"filtered_{fname}")
        enhance_fingerprints(raw_path, filt_path)
        filtered_cols.append(filt_path)
    print("– colunas filtradas em", cols_filt_dir)

    # 5) Detecção inicial e geração de JSON
    init_marked_dir = os.path.join(output_dir, "marked_initial")
    init_data_dir   = os.path.join(output_dir, "data_initial")
    os.makedirs(init_marked_dir, exist_ok=True)
    os.makedirs(init_data_dir,   exist_ok=True)
    for inp in filtered_cols:
        fname = os.path.basename(inp)
        out_img = os.path.join(init_marked_dir, f"marked_{fname}")
        out_json = os.path.join(init_data_dir, f"{os.path.splitext(fname)[0]}.json")
        detect_and_mark_fingerprints(inp, out_img, out_json)
    print("– detectado e marcado em", init_marked_dir, "com JSONs em", init_data_dir)

    # 6) Ajuste final das caixas (Red-box fixer)
    corr_img_dir  = os.path.join(output_dir, "corrected_images")
    corr_data_dir = os.path.join(output_dir, "corrected_data")
    os.makedirs(corr_img_dir,  exist_ok=True)
    os.makedirs(corr_data_dir, exist_ok=True)
    final_images, final_jsons = [], []
    for j in os.listdir(init_data_dir):
        if not j.endswith(".json"):
            continue
        in_json = os.path.join(init_data_dir, j)
        basej   = os.path.splitext(j)[0]
        out_img = os.path.join(corr_img_dir,  f"corrected_{basej}.png")
        out_json= os.path.join(corr_data_dir, f"corrected_{j}")
        fixing_redbox(in_json, out_img, out_json)
        final_images.append(out_img)
        final_jsons.append(out_json)

    return final_images, final_jsons

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline completo: ficha → imagens marcadas + JSONs corrigidos"
    )
    parser.add_argument("image", help="Caminho da imagem da ficha")
    parser.add_argument(
        "--output", "-o", default="output",
        help="Pasta de saída (cria subpastas automaticamente)"
    )
    args = parser.parse_args()

    imgs, jsns = process_ficha(args.image, args.output)
    print("\nSaída final:")
    print(" Imagens corrigidas:", *["\n\t"+i for i in imgs])
    print(" JSONs corrigidos:  ", *["\n\t"+j for j in jsns])
