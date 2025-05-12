import cv2
import numpy as np

def conta_objetos(img_crop):
    # Pré-processamento
    gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Remove ruídos internos
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Conta objetos externos
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contornos)

def classifica_ficha(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    altura, largura, _ = imagem.shape

    # Define regiões para análise (10% das bordas esquerda e direita)
    margem = int(largura * 0.1)
    esquerda = imagem[:, :margem]
    direita = imagem[:, -margem:]

    objetos_esquerda = conta_objetos(esquerda)
    objetos_direita = conta_objetos(direita)

    print(f"Objetos Esquerda: {objetos_esquerda}, Objetos Direita: {objetos_direita}")

    if objetos_direita/objetos_esquerda>4:
        return "0-10"
    if objetos_direita/objetos_esquerda<0.25:
        return "10-0"
    else:
        return "5-5"
# Exemplo de uso:
#caminhos = [
#    'Filtradas/filtered_2_1_1.jpg'
#]

#for caminho in caminhos:
 #   tipo = classifica_ficha(caminho)
 #   print(f"{caminho} -> {tipo}")
