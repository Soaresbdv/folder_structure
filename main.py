import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def select_zip_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo ZIP",
        filetypes=[("Arquivos ZIP", "*.zip")]
    )
    return file_path

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def reorganize_folder(extracted_path):
    # Encontrar a pasta que tem "numero - nome empresa"
    subfolders = [f for f in os.listdir(extracted_path) if os.path.isdir(os.path.join(extracted_path, f))]
    if not subfolders:
        raise Exception("Nenhuma pasta encontrada dentro do ZIP!")

    empresa_folder = os.path.join(extracted_path, subfolders[0])
    cancelados_folder = os.path.join(empresa_folder, "Cancelados")

    if not os.path.exists(cancelados_folder):
        raise Exception("Pasta 'Cancelados' nao encontrada!")

    # Mover todos os arquivos XML de 'Cancelados' para 'empresa_folder'
    for file in os.listdir(cancelados_folder):
        if file.lower().endswith('.xml'):
            src = os.path.join(cancelados_folder, file)
            dst = os.path.join(empresa_folder, file)
            shutil.move(src, dst)

    # Remover a pasta Cancelados depois de mover tudo
    shutil.rmtree(cancelados_folder)

    return empresa_folder

def create_final_zip(folder_to_zip, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_to_zip):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_to_zip))
                zipf.write(file_path, arcname)

def main():
    zip_file = select_zip_file()
    if not zip_file:
        print("Nenhum arquivo selecionado.")
        return

    downloads_folder = get_downloads_folder()
    temp_extract_path = os.path.join(downloads_folder, "temp_extract")

    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)
    os.makedirs(temp_extract_path)

    extract_zip(zip_file, temp_extract_path)
    empresa_folder = reorganize_folder(temp_extract_path)

    # Nome do zip final será igual ao nome da pasta "numero-nomeempresa"
    final_zip_name = os.path.basename(empresa_folder) + ".zip"
    final_zip_path = os.path.join(downloads_folder, final_zip_name)

    create_final_zip(empresa_folder, final_zip_path)

    # Limpar pasta temporaria
    shutil.rmtree(temp_extract_path)

    print(f"Arquivo final gerado: {final_zip_path}")

if __name__ == "__main__":
    main()
