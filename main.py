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

def find_cnpj_in_xml(xml_folder, cnpj):
    for root, dirs, files in os.walk(xml_folder):
        for file in files:
            if file.lower().endswith('.xml'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if cnpj in content:
                            return True
                except:
                    continue
    return False

def move_txt_to_company_folder(txt_path, company_folders, cnpj):
    for folder in company_folders:
        if find_cnpj_in_xml(folder, cnpj):
            shutil.move(txt_path, os.path.join(folder, os.path.basename(txt_path)))
            return True
    return False

def reorganize_folders(base_path):
    company_folders = []
    txt_files = []

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            company_folders.append(item_path)
        elif item.lower().endswith('.txt'):
            txt_files.append(item_path)

    for company_folder in company_folders:
        cancelados_folder = os.path.join(company_folder, "Cancelados")

        if os.path.exists(cancelados_folder):
            for file in os.listdir(cancelados_folder):
                src = os.path.join(cancelados_folder, file)
                dst = os.path.join(company_folder, file)
                shutil.move(src, dst)
            shutil.rmtree(cancelados_folder)

    for txt_file in txt_files:
        cnpj = os.path.basename(txt_file).split('-')[2]
        found = move_txt_to_company_folder(txt_file, company_folders, cnpj)
        if not found:
            print(f"Aviso: CNPJ {cnpj} do arquivo {os.path.basename(txt_file)} nao encontrado em nenhum XML.")

def create_final_zip(base_folder, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(base_folder))
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

    reorganize_folders(temp_extract_path)

    zip_name_parts = os.path.basename(zip_file).replace('.zip', '').split('-')
    if len(zip_name_parts) >= 5:
        cnpj = zip_name_parts[2]
        ano = zip_name_parts[-1]
        final_zip_name = f"{cnpj}-INTEGRACAO-{ano}.zip"
    else:
        final_zip_name = "resultado_integracao.zip"

    final_zip_path = os.path.join(downloads_folder, final_zip_name)

    create_final_zip(temp_extract_path, final_zip_path)

    shutil.rmtree(temp_extract_path)

    print(f"Arquivo final gerado: {final_zip_path}")

if __name__ == "__main__":
    main()
