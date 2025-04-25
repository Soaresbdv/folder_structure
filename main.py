import os
import shutil

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def generate_folder_name(base_path, base_name="teste"):
    count = 0 # Gera nome único como teste, e também coloca uma numeração se já existir
    folder_name = base_name
    new_path = os.path.join(base_path, folder_name)
    
    while os.path.exists(new_path):
        count += 1
        folder_name = f"{base_name} ({count})"
        new_path = os.path.join(base_path, folder_name)
    
    return new_path

def create_txt_inside(folder_path):
    txt_path = os.path.join(folder_path, "info.txt")
    with open(txt_path, "w") as f:
        f.write("Este é um arquivo gerado automaticamente.\n")
    return txt_path

def process_folder(input_folder_path):
    downloads_path = get_downloads_folder()
    final_folder_path = generate_folder_name(downloads_path)

    shutil.move(input_folder_path, final_folder_path)
    create_txt_inside(final_folder_path)

    return final_folder_path

if __name__ == "__main__":
    # Altere aqui para o caminho da sua pasta original:
    pasta_origem = r"C:\Users\bruno.lima\Desktop\pasta1"

    if os.path.exists(pasta_origem):
        resultado = process_folder(pasta_origem)
        print(f"Pasta movida e atualizada em: {resultado}")
    else:
        print("A pasta de origem não existe.")
