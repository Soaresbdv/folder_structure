import os
import shutil
import zipfile
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import time

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")

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

def reorganize_folders(base_path, progress_callback, app):
    company_folders = []
    txt_files = []

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            company_folders.append(item_path)
        elif item.lower().endswith('.txt'):
            txt_files.append(item_path)

    total_steps = len(company_folders) + len(txt_files)
    current_step = 0

    for company_folder in company_folders:
        cancelados_folder = os.path.join(company_folder, "Cancelados")

        if os.path.exists(cancelados_folder):
            for file in os.listdir(cancelados_folder):
                src = os.path.join(cancelados_folder, file)
                dst = os.path.join(company_folder, file)
                shutil.move(src, dst)
            shutil.rmtree(cancelados_folder)

        current_step += 1
        progress_callback(current_step / total_steps)
        app.update()

    for txt_file in txt_files:
        cnpj = os.path.basename(txt_file).split('-')[2]
        found = move_txt_to_company_folder(txt_file, company_folders, cnpj)
        if not found:
            print(f"Aviso: CNPJ {cnpj} do arquivo {os.path.basename(txt_file)} nao encontrado em nenhum XML.")

        current_step += 1
        progress_callback(current_step / total_steps)
        app.update()

def create_final_zip(base_folder, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(base_folder))
                zipf.write(file_path, arcname)

def process_zip(zip_file, progress_callback, update_message_callback, app):
    if not zip_file:
        return

    downloads_folder = get_downloads_folder()
    temp_extract_path = os.path.join(downloads_folder, "temp_extract")

    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)
    os.makedirs(temp_extract_path)

    update_message_callback("Extraindo arquivo...")
    extract_zip(zip_file, temp_extract_path)

    update_message_callback("Organizando pastas...")
    reorganize_folders(temp_extract_path, progress_callback, app)

    zip_name_parts = os.path.basename(zip_file).replace('.zip', '').split('-')
    if len(zip_name_parts) >= 5:
        cnpj = zip_name_parts[2]
        ano = zip_name_parts[-1]
        final_zip_name = f"{cnpj}-INTEGRACAO-{ano}.zip"
    else:
        final_zip_name = "resultado_integracao.zip"

    final_zip_path = os.path.join(downloads_folder, final_zip_name)

    update_message_callback("Compactando resultado...")
    create_final_zip(temp_extract_path, final_zip_path)

    shutil.rmtree(temp_extract_path)

    update_message_callback("Arquivo gerado com sucesso!", color="#90EE90")
    progress_callback(0)
    app.after(3000, lambda: update_message_callback("Arraste e solte o arquivo ZIP aqui"))

    print(f"Arquivo final gerado: {final_zip_path}")

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = TkinterDnD.Tk()
    app.title("Organizador de Integra\u00e7\u00e3o")
    app.geometry("600x400")

    if ctk.get_appearance_mode() == "Dark":
        app.configure(bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1])
    else:
        app.configure(bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0])

    frame = ctk.CTkFrame(app, corner_radius=15)
    frame.pack(expand=True, fill="both", padx=0, pady=0)

    def toggle_mode():
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
            mode_switch.configure(text="Dark Mode")
            app.configure(bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0])
        else:
            ctk.set_appearance_mode("Dark")
            mode_switch.configure(text="Light Mode")
            app.configure(bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1])

    mode_switch = ctk.CTkSwitch(frame, text="Dark Mode", command=toggle_mode, font=("Arial", 12))
    mode_switch.place(relx=0.05, rely=0.05)

    drop_area = ctk.CTkFrame(frame, width=400, height=200, corner_radius=20)
    drop_area.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

    drop_label = ctk.CTkLabel(drop_area, text="Arraste e solte o arquivo ZIP aqui", font=("Arial", 16))
    drop_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    progress = ctk.CTkProgressBar(frame, width=300, height=10)
    progress.place(relx=0.5, rely=0.8, anchor=ctk.CENTER)
    progress.set(0)

    def update_progress(value):
        progress.set(value)

    def update_message(message, color=None):
        if color:
            drop_label.configure(text=message, text_color=color)
        else:
            drop_label.configure(text=message, text_color=("black", "white"))

    def on_drop(event):
        file_path = event.data.strip('{}')
        if file_path.lower().endswith('.zip'):
            process_zip(file_path, update_progress, update_message, app)

    def on_click(event):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo ZIP",
            filetypes=[("Arquivos ZIP", "*.zip")]
        )
        if file_path:
            process_zip(file_path, update_progress, update_message, app)

    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", on_drop)
    drop_area.bind("<Button-1>", on_click)
    drop_label.bind("<Button-1>", on_click)

    app.mainloop()

if __name__ == "__main__":
    main()
