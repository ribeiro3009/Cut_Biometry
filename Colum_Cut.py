from PIL import Image
import os

def cut_columns(file_path, col1_coords, col2_coords=None, output_dir="cutted_colums_raw"):
    from PIL import Image
    import os

    file_path = os.path.abspath(file_path)
    os.makedirs(output_dir, exist_ok=True)

    print(f"[cut_columns] file_path: {file_path}")
    print(f"[cut_columns] output_dir: {output_dir}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Imagem não encontrada: {file_path}")

    image = Image.open(file_path)
    basename = os.path.splitext(os.path.basename(file_path))[0]

    if col1_coords != (0, 0):
        col1 = image.crop((col1_coords[0], 0, col1_coords[1], image.height))
        col1_filename = f"{basename}_colum1_10.jpg" if col2_coords == (0, 0) else f"{basename}_colum1_5.jpg"
        col1.save(os.path.join(output_dir, col1_filename))

    if col2_coords != (0, 0):
        col2 = image.crop((col2_coords[0], 0, col2_coords[1], image.height))
        col2_filename = f"{basename}_colum2_10.jpg" if col1_coords == (0, 0) else f"{basename}_colum2_5.jpg"
        col2.save(os.path.join(output_dir, col2_filename))





cut_columns("Fichas/ficha1_1.jpg", (28,324), (1420,1699))
#cut_columns("Fichas/Ficha2.jpg", (0,264),(1413,1676))
#cut_columns("Fichas/Ficha3.jpg", (0,0), (1331,1610))
#cut_columns("Fichas/Ficha2_1.jpg",(28,324),(1420,1699))
#cut_columns("Fichas/Ficha2_1.jpg",(36,386),(1392,1698))
#cut_columns("Fichas/Ficha3_1.jpg",(0,0),(1430,1690))
