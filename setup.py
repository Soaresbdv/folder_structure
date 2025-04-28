from cx_Freeze import setup, Executable

setup(
    name="Organizer",
    version="1.0",
    description="Organizador de arquivos zip",
    executables=[Executable("main.py", target_name="setOrganizer.exe", base="Win32GUI")],
)
