import os
import sys
import time
import subprocess
import psutil
import threading
import tkinter as tk
import tkinter.ttk as ttk

APP_NAMES = ["prevenda.exe", "flet.exe"]

def find_and_kill_all(process_names):
    found = False
    current_pid = os.getpid()
    print(f"[DEBUG] PID do updater: {current_pid}")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            print(f"[DEBUG] Encontrado processo: {proc.info}")
            if proc.info['name'] and proc.info['name'].lower() in [n.lower() for n in process_names]:
                if proc.info['pid'] != current_pid:
                    print(f"[DEBUG] Matando {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
                    found = True
        except Exception as e:
            print(f"[DEBUG] Erro ao finalizar {proc.info.get('name', '')}: {e}")
    return found

def wait_until_closed(process_names, timeout=30):
    print(f"[DEBUG] Esperando processos fecharem: {process_names}")
    start = time.time()
    while time.time() - start < timeout:
        running = [
            proc.info['name'].lower()
            for proc in psutil.process_iter(['name'])
            if proc.info['name'] and proc.info['name'].lower() in [n.lower() for n in process_names]
        ]
        print(f"[DEBUG] Ainda rodando: {running}")
        if not running:
            print("[DEBUG] Nenhum processo relevante rodando.")
            return True
        time.sleep(0.5)
    print("[DEBUG] Timeout ao esperar processos fecharem.")
    return False

def start_app(exe_name):
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_dir, exe_name)
    print(f"[DEBUG] Tentando iniciar: {exe_path}")
    print(f"[DEBUG] Diretório de trabalho: {base_dir}")
    print(f"[DEBUG] Existe? {os.path.exists(exe_path)}")
    try:
        proc = subprocess.Popen([exe_path], cwd=base_dir, shell=False)
        print(f"[DEBUG] {exe_name} iniciado. PID: {proc.pid}")
    except Exception as e:
        print(f"[DEBUG] Erro ao iniciar {exe_name}: {e}")

def show_loading_window():
    def disable_event():
        pass  # Desabilita fechar/minimizar

    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", disable_event)
    root.overrideredirect(True)  # Remove barra de título

    # Centralizar janela
    width, height = 300, 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    label = tk.Label(root, text="Atualizando...", font=("Arial", 14))
    label.pack(pady=15)
    pb = ttk.Progressbar(root, mode='indeterminate', length=200)
    pb.pack(pady=5)
    pb.start(10)

    return root

def main():
    # Inicia janela de loading em thread separada
    loading_window = [None]
    def start_loading():
        loading_window[0] = show_loading_window()
        loading_window[0].mainloop()
    t = threading.Thread(target=start_loading, daemon=True)
    t.start()
    time.sleep(0.2)  # Pequeno delay para garantir abertura da janela

    print("[DEBUG] Fechando instâncias antigas...")
    find_and_kill_all(APP_NAMES)
    print("[DEBUG] Aguardando fechamento completo...")
    if wait_until_closed(APP_NAMES):
        print("[DEBUG] Iniciando nova instância...")
        time.sleep(1)  # Pequeno delay extra para garantir liberação do arquivo
        start_app("prevenda.exe")
    else:
        print(f"[DEBUG] Não foi possível finalizar todos os processos: {APP_NAMES}")

    # Fecha janela de loading
    if loading_window[0]:
        loading_window[0].destroy()
    print("[DEBUG] Script finalizado. Console ficará aberto por 10 segundos...")
    time.sleep(10)

if __name__ == "__main__":
    main()