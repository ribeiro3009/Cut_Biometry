import os
import cv2
import numpy as np

# Parâmetros hipotéticos (ajuste conforme necessidade)
HEIGHT_THRESHOLD = 1500  # se altura < isso, classifica como 5-5
DELTA_Y = 300            # deslocamento mínimo do centro de massa para 5-5
RATIO = 1.2              # razão mínima para predominância lateral


def classifica_ficha(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        print(f"❌ Falha ao ler: {caminho_imagem}")
        return "Erro"

    altura, largura = imagem.shape[:2]

    # 1) Se a ficha for muito curta, assume-se balanceada
    if altura < HEIGHT_THRESHOLD:
        return "5-5"

    # 2) Binariza para encontrar pixels brancos (cristas)
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # 3) Calcula o centro de massa vertical dos pixels brancos
    ys, _ = np.where(bin_img == 255)
    if len(ys) == 0:
        return "5-5"
    y_center = np.mean(ys)
    print(y_center)
    # 4) Se o deslocamento do centro de massa vertical for alto, é balanceada
    midpoint = altura / 2
    if abs(y_center - midpoint) > DELTA_Y:
        return "5-5"

    # 5) Caso contrário, caracteriza como 10-10 e refina pela lateralidade
    # Divide imagem ao meio
    margem = int(largura * 0.1)
    esquerda = bin_img[:, :margem]
    direita = bin_img[:, -margem:]
    soma_esq = np.sum(esquerda == 255)
    soma_dir = np.sum(direita == 255)

    # 6) Decide predominância
    if soma_dir > soma_esq * RATIO:
        return "0-10"
    else: return "0-10"

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    INPUT_DIR = os.path.join(BASE_DIR, "Filtradas")

    if not os.path.isdir(INPUT_DIR):
        print(f"Pasta não encontrada: {INPUT_DIR}")
        exit(1)

    arquivos = sorted(
        [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".png", ".jpg"))]
    )
    print(f"{len(arquivos)} imagens encontradas em '{INPUT_DIR}'\n")

    for nome in arquivos:
        caminho = os.path.join(INPUT_DIR, nome)
        tipo = classifica_ficha(caminho)
        print(f"→ {nome} -> {tipo}")
