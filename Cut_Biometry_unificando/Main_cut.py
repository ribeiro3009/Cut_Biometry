import os
import cv2
import json
import shutil
from datetime import datetime
from Filter import remove_lines_keep_fingerprints
from Classification import classifica_ficha
from Colum_Marker import mark_columns
from Colum_Cut import cut_columns
from Colum_Filter import enhance_fingerprints
from identificador2 import detect_and_mark_fingerprints
from Red_box_fixer import fixing_redbox

# Função principal para unificar todas as etapas
def processar_ficha(ficha_path):
    ficha_path = os.path.abspath(ficha_path)
    ficha_nome = os.path.splitext(os.path.basename(ficha_path))[0]

    # Criação de diretórios temporários
    temp_base = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ficha_nome}"
    os.makedirs(temp_base, exist_ok=True)
    colunas_raw = os.path.join(temp_base, "colunas_raw")
    colunas_filtradas = os.path.join(temp_base, "colunas_filtradas")
    jsons_raw = os.path.join(temp_base, "jsons_raw")
    jsons_corrigidos = os.path.join(temp_base, "jsons_corrigidos")
    os.makedirs(colunas_raw)
    os.makedirs(colunas_filtradas)
    os.makedirs(jsons_raw)
    os.makedirs(jsons_corrigidos)

    # 1. Filtragem da imagem original
    imagem_filtrada = remove_lines_keep_fingerprints(ficha_path)
    temp_filtrada_path = os.path.join(temp_base, f"{ficha_nome}_filtered.jpg")
    cv2.imwrite(temp_filtrada_path, imagem_filtrada)

    # 2. Classificação da ficha
    classificacao = classifica_ficha(temp_filtrada_path)

    # 3. Marcação das colunas
    _, coords_col1, coords_col2 = mark_columns(temp_filtrada_path, "", classificacao)

    # 4. Corte das colunas da ficha original
    cut_columns(ficha_path, coords_col1, coords_col2, output_dir=colunas_raw)

    # 5. Filtro nas colunas cortadas
    colunas_processadas = []
    for nome_arquivo in os.listdir(colunas_raw):
        if nome_arquivo.endswith(".jpg"):
            raw_path = os.path.join(colunas_raw, nome_arquivo)
            output_path = os.path.join(colunas_filtradas, f"filtered_{nome_arquivo}")
            enhance_fingerprints(raw_path, output_path)
            colunas_processadas.append(output_path)

    # 6. Identificação das digitais e salvamento dos dados
    jsons_gerados = []
    for coluna in colunas_processadas:
        nome_json = os.path.basename(coluna) + ".json"
        json_output_path = os.path.join(jsons_raw, nome_json)
        detect_and_mark_fingerprints(coluna, json_output_path)
        jsons_gerados.append(json_output_path)

    # 7. Correção das caixas vermelhas
    jsons_corrigidos_final = []
    for json_path in jsons_gerados:
        corrected_json_path = os.path.join(jsons_corrigidos, f"corrected_{os.path.basename(json_path)}")
        fixing_redbox(json_path, corrected_json_path)
        jsons_corrigidos_final.append(corrected_json_path)

    # Retorno: dicionário com os dados corrigidos de cada coluna
    dados_finais = {}
    for json_corrigido in jsons_corrigidos_final:
        with open(json_corrigido, 'r') as f:
            data = json.load(f)
            dados_finais[os.path.basename(json_corrigido)] = data

    return dados_finais

 
dados = processar_ficha(r"C:\Fichas\Ficha1.jpg")
# Salvando os dados em um arquivo .json
