import os
import shutil
import zipfile
import sys
import time
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

def find_cnpj_in_xml(xml_folder, cnpj):
    for root, _, files in os.walk(xml_folder):
        for file in files:
            if file.lower().endswith('.xml'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        if cnpj in f.read():
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

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def is_structure_valid(extracted_path):
    folders = [os.path.join(extracted_path, f) for f in os.listdir(extracted_path) if os.path.isdir(os.path.join(extracted_path, f))]
    txt_files = [f for f in os.listdir(extracted_path) if f.lower().endswith('.txt')]

    if not folders or not txt_files:
        return False

    for txt in txt_files:
        try:
            cnpj = txt.split('-')[2]
        except IndexError:
            return False

        if not any(find_cnpj_in_xml(folder, cnpj) for folder in folders):
            print(f"[ERRO] CNPJ do arquivo {txt} não foi encontrado em nenhuma pasta.")
            return False

    return True

def reorganize_folders(base_path, progress_callback, app):
    company_folders = [os.path.join(base_path, f) for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    txt_files = [os.path.join(base_path, f) for f in os.listdir(base_path) if f.lower().endswith('.txt')]

    total_steps = len(company_folders) + len(txt_files)
    current_step = 0

    for company_folder in company_folders:
        cancelados_folder = os.path.join(company_folder, "Cancelados")
        if os.path.exists(cancelados_folder):
            for file in os.listdir(cancelados_folder):
                shutil.move(os.path.join(cancelados_folder, file), os.path.join(company_folder, file))
            shutil.rmtree(cancelados_folder)
        current_step += 1
        progress_callback(current_step / total_steps)
        app.update()

    for txt_file in txt_files:
        cnpj = os.path.basename(txt_file).split('-')[2]
        move_txt_to_company_folder(txt_file, company_folders, cnpj)
        current_step += 1
        progress_callback(current_step / total_steps)
        app.update()

def create_final_zip(base_folder, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(base_folder)))

def reset_message(app, update_message_callback, text="Arraste e solte o arquivo aqui. Ou clique pra encontrar"):
    app.after(3000, lambda: update_message_callback(text))

def process_zip(zip_file, progress_callback, update_message_callback, app):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    temp_extract_path = os.path.join(downloads_folder, "temp_extract")

    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)
    os.makedirs(temp_extract_path)

    update_message_callback("Extraindo arquivo...")
    try:
        extract_zip(zip_file, temp_extract_path)
    except zipfile.BadZipFile:
        update_message_callback("Tipo de arquivo incorreto.", color=("#8B0000", "#FF7F7F"))
        progress_callback(0)
        reset_message(app, update_message_callback)
        return

    if not is_structure_valid(temp_extract_path):
        update_message_callback("Estrutura de arquivo incorreta!", color=("#8B0000", "#FF7F7F"))
        progress_callback(0)
        shutil.rmtree(temp_extract_path)
        reset_message(app, update_message_callback)
        return

    update_message_callback("Organizando pastas...")
    reorganize_folders(temp_extract_path, progress_callback, app)

    zip_name_parts = os.path.basename(zip_file).replace('.zip', '').split('-')
    final_zip_name = f"{zip_name_parts[2]}-INTEGRACAO-{zip_name_parts[-1]}.zip" if len(zip_name_parts) >= 5 else "resultado_integracao.zip"
    final_zip_path = os.path.join(downloads_folder, final_zip_name)

    update_message_callback("Compactando resultado...")
    create_final_zip(temp_extract_path, final_zip_path)
    shutil.rmtree(temp_extract_path)

    green_color = "#228B22" if ctk.get_appearance_mode() == "Light" else "#90EE90"
    update_message_callback("Arquivo gerado com sucesso!", color=green_color)
    progress_callback(0)
    reset_message(app, update_message_callback)

    print(f"Arquivo final gerado: {final_zip_path}")

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = TkinterDnD.Tk()
    app.title("OrganizeUP")

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_path, "favicon.ico")
    app.iconbitmap(icon_path)
    app.geometry("600x400")

    bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1] if ctk.get_appearance_mode() == "Dark" else ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0]
    app.configure(bg=bg_color)

    frame = ctk.CTkFrame(app, corner_radius=15)
    frame.pack(expand=True, fill="both", padx=0, pady=0)

    def toggle_mode():
        ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
        mode_switch.configure(text="Dark Mode" if ctk.get_appearance_mode() == "Light" else "Light Mode")
        app.configure(bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0 if ctk.get_appearance_mode() == "Light" else 1])

    mode_switch = ctk.CTkSwitch(frame, text="Dark Mode", command=toggle_mode, font=("Arial", 12))
    mode_switch.place(relx=0.05, rely=0.05)

    drop_area = ctk.CTkFrame(frame, width=400, height=200, corner_radius=20)
    drop_area.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

    drop_label = ctk.CTkLabel(drop_area, text="Arraste e solte o arquivo aqui. Ou clique pra encontrar", font=("Segoe UI", 13))
    drop_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    progress = ctk.CTkProgressBar(frame, width=300, height=10)
    progress.place(relx=0.5, rely=0.8, anchor=ctk.CENTER)
    progress.set(0)

    def update_progress(value):
        progress.set(value)

    def update_message(message, color=None):
        drop_label.configure(text=message, text_color=color or ("black", "white"))

    def handle_file(file_path):
        drop_area.configure(fg_color=("#E5E5E5", "#333333"))
        if file_path.lower().endswith('.zip'):
            process_zip(file_path, update_progress, update_message, app)
        else:
            update_message("Tipo de arquivo incorreto.", color=("#8B0000", "#FF7F7F"))
        progress.set(0)
        reset_message(app, update_message)
        reset_message(app, update_message)

    def on_drop(event):
        file_path = event.data.strip('{}')
        handle_file(file_path)
        drop_area.configure(fg_color=("#F0F0F0", "#2D2D2D"))

    def on_drag_enter(event):
        drop_area.configure(fg_color=("#D6F5FF", "#2A3D4F"))

    def on_drag_leave(event):
        drop_area.configure(fg_color=("#F0F0F0", "#2D2D2D"))
        
    def on_click(event):
        file_path = filedialog.askopenfilename(title="Selecione o arquivo ZIP", filetypes=[("Arquivos ZIP", "*.zip")])
        if file_path:
            handle_file(file_path)

    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", on_drop)
    drop_area.bind("<Enter>", on_drag_enter)
    drop_area.bind("<Leave>", on_drag_leave)
    drop_area.bind("<Button-1>", on_click)
    drop_label.bind("<Button-1>", on_click)

    app.mainloop()

if __name__ == "__main__":
    main()
