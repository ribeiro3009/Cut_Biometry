import cv2
import numpy as np

# dada que é menor que o mínimo assume minimal_adition
def count_white_pixels_vertical_line(img, col):
    return np.sum(img[:, col] == 255)

def find_columns(img, side, n_pixels_start, n_pixels_end, minimal_length, additional_steps=10, minimal_adition=10):
    height, width = img.shape
    
    if side == 'left':
        range_start, range_end, step = 0, width//2, 1
    elif side == 'right':
        range_start, range_end, step = width - 1, width//2, -1

    n_pixels_begin, n_pixels_finish = None, None

    for col in range(range_start, range_end, step):
        count = count_white_pixels_vertical_line(img, col)
        if count >= n_pixels_start:
            n_pixels_begin = col
            break

    for col in range(n_pixels_begin + step, range_end, step):
        count = count_white_pixels_vertical_line(img, col)
        if count <= n_pixels_end:
            # Continua mais algumas iterações para evitar encerramento precoce
            final_candidate = col
            for extra in range(additional_steps):
                col += step
                if col == range_end:
                    break
                count = count_white_pixels_vertical_line(img, col)
                if count > n_pixels_end:
                    final_candidate = col
            n_pixels_finish = final_candidate
            break

    # Verifica o comprimento mínimo da coluna
    if abs(n_pixels_finish - n_pixels_begin) < minimal_length:
        if side == 'left':
            n_pixels_finish = n_pixels_begin + minimal_adition
        else:
            n_pixels_finish = n_pixels_begin - minimal_adition

    return n_pixels_begin, n_pixels_finish

def mark_columns(input_image_path, output_image_path, classification):
    n_pixels_start_5_5 = 100
    n_pixels_start_0_10 = 200
    n_pixels_end = 20
    minimal_length = 50
    additional_steps = 10
    img_original = cv2.imread(input_image_path)
    heigth, width = img_original.shape[:2]
    minimal_adition = int(width * 0.18)
    img_gray = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    _, img_bin = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)

    #print(f"{input_image_path}")

    if classification == '5-5':
        left_begin, left_end = find_columns(img_bin, 'left', n_pixels_start_5_5, n_pixels_end, minimal_length, additional_steps, minimal_adition)
        right_begin, right_end = find_columns(img_bin, 'right', n_pixels_start_5_5, n_pixels_end, minimal_length, additional_steps, minimal_adition)
        print(f"({left_begin},{left_end})")
        print(f"({right_end},{right_begin})")
        cv2.rectangle(img_original, (left_begin, 0), (left_end, img_original.shape[0]), (0, 255, 0), 2)
        cv2.rectangle(img_original, (right_end, 0), (right_begin, img_original.shape[0]), (0, 255, 0), 2)
        return f"{input_image_path}",(left_begin,left_end),(right_end,right_begin)

    elif classification == '10-0':
        left_begin, left_end = find_columns(img_bin, 'left', n_pixels_start_0_10, n_pixels_end, minimal_length, additional_steps, minimal_adition)
        print(f"(x={left_begin},{left_end})")
        cv2.rectangle(img_original, (left_begin, 0), (left_end, img_original.shape[0]), (0, 255, 0), 2)
        return f"{input_image_path}",(left_begin,left_end),(0,0)

    elif classification == '0-10':
        right_begin, right_end = find_columns(img_bin, 'right', n_pixels_start_0_10, n_pixels_end, minimal_length, additional_steps, minimal_adition)
        print(f"({right_end},{right_begin})")
        cv2.rectangle(img_original, (right_end, 0), (right_begin, img_original.shape[0]), (0, 255, 0), 2)
        return f"{input_image_path}",(0,0),(right_end,right_begin)

    ##cv2.imwrite(output_image_path, img_original)

# Exemplo de uso
#mark_columns("Filtradas/filtered_2_1.jpg", "Colunas_Marcadas/marked_columns_2_1.jpg", "5-5")
#mark_columns("Filtradas/filtered_2_2.jpg", "Colunas_Marcadas/marked_columns_2_2.jpg", "5-5")
#mark_columns("Filtradas/filtered_2_3.jpg", "Colunas_Marcadas/marked_columns_2_3.jpg", "0-10")
#mark_columns("Filtradas/filtered_2_1_1.jpg", "Colunas_Marcadas/marked_columns_2_1_1.jpg", "5-5")
#mark_columns("Filtradas/filtered_2_2_1.jpg", "Colunas_Marcadas/marked_columns_2_2_1.jpg", "5-5")
#mark_columns("Filtradas/filtered_2_3_1.jpg", "Colunas_Marcadas/marked_columns_2_3_1.jpg", "0-10")
