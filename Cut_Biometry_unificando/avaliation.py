import os
import json
import shutil

# Configurações de pasta
ROOT_DIR     = r"C:/Users/rj0369870548/Desktop/Projects_VsCode/Corte_fichas/Cut_Biometry/Cut_Biometry_unificando/saida"
OUTPUT_OK    = "Yeah"
OUTPUT_FAIL  = "Noo"
COLUMN_OK    = "colum_correct"
COLUMN_FAIL  = "colum_fail"

# Garante existência das pastas de destino
for d in (OUTPUT_OK, OUTPUT_FAIL, COLUMN_OK, COLUMN_FAIL):
    os.makedirs(d, exist_ok=True)


def contar_digitais_em_json(json_path):
    """Retorna total de impressões e contagem por cor no JSON."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    total = len(data.get("fingerprints", []))
    cores = {'red': 0, 'green': 0, 'blue': 0}
    for fp in data.get("fingerprints", []):
        c = fp.get("color")
        if c in cores:
            cores[c] += 1
    return total, cores


def avaliar_fichas(root):
    resumo = {
        'digitais': 0, 'red': 0, 'green': 0, 'blue': 0,
        'fichas_ok': 0, 'fichas_fail': 0,
        'colunas_ok': 0, 'colunas_fail': 0
    }

    for ficha in os.listdir(root):
        ficha_path = os.path.join(root, ficha)
        if not os.path.isdir(ficha_path):
            continue

        # Pastas dentro da ficha
        json_dir = os.path.join(ficha_path, "corrected_data")
        img_dir  = os.path.join(ficha_path, "corrected_images")
        class_file = os.path.join(ficha_path, "class.txt")

        # Valida existência
        if not os.path.isdir(json_dir) or not os.path.isdir(img_dir) or not os.path.isfile(class_file):
            print(f"[PULANDO] {ficha}: estrutura inválida.")
            continue

        # Lê classificação (5-5 ou outra)
        with open(class_file, 'r') as f:
            cls = f.read().strip()
        esperado_por_coluna = 5 if cls == "5-5" else 10

        # Contadores para esta ficha
        total_ficha = 0
        cores_ficha = {'red': 0, 'green': 0, 'blue': 0}

        # Percorre cada JSON / coluna
        for fn in os.listdir(json_dir):
            if not fn.endswith(".json"):
                continue
            json_path = os.path.join(json_dir, fn)
            tot, cores = contar_digitais_em_json(json_path)
            total_ficha += tot
            for c in cores_ficha:
                cores_ficha[c] += cores[c]

            # Localiza imagem marcada correspondente
            base = os.path.splitext(fn)[0]  # inclui o prefixo 'corrected_'
            img_path = None
            for ext in (".png", ".jpg", ".jpeg"):  # tenta extensões
                cand = os.path.join(img_dir, f"{base}{ext}")
                if os.path.exists(cand):
                    img_path = cand
                    break
            if not img_path:
                print(f"[AVISO] Imagem não encontrada para {fn}")

            # Copia a imagem de coluna para ok/fail
            if tot == esperado_por_coluna:
                resumo['colunas_ok'] += 1
                if img_path:
                    shutil.copy2(img_path, os.path.join(COLUMN_OK, os.path.basename(img_path)))
            else:
                resumo['colunas_fail'] += 1
                if img_path:
                    shutil.copy2(img_path, os.path.join(COLUMN_FAIL, os.path.basename(img_path)))

        # Print do resultado da ficha
        print(f"{ficha}: {total_ficha} digitais → red={cores_ficha['red']}, green={cores_ficha['green']}, blue={cores_ficha['blue']}")

        # Atualiza resumo geral
        resumo['digitais'] += total_ficha
        for c in ('red','green','blue'):
            resumo[c] += cores_ficha[c]
        if total_ficha == 10:
            resumo['fichas_ok'] += 1
            shutil.copytree(ficha_path, os.path.join(OUTPUT_OK, ficha), dirs_exist_ok=True)
        else:
            resumo['fichas_fail'] += 1
            shutil.copytree(ficha_path, os.path.join(OUTPUT_FAIL, ficha), dirs_exist_ok=True)

    # Exibe resumo final
    print("\n===== RESUMO FINAL =====")
    print(f"Total digitais:     {resumo['digitais']}")
    print(f"  - Vermelhas:      {resumo['red']}")
    print(f"  - Verdes:         {resumo['green']}")
    print(f"  - Azuis:          {resumo['blue']}")
    print(f"Fichas OK (10):     {resumo['fichas_ok']}")
    print(f"Fichas FAIL:        {resumo['fichas_fail']}")
    print(f"Colunas OK:         {resumo['colunas_ok']}")
    print(f"Colunas FAIL:       {resumo['colunas_fail']}")

if __name__ == "__main__":
    avaliar_fichas(ROOT_DIR)
