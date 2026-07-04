#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def clear_screen():
    print("\033[H\033[J", end="")

def get_char():
    try:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except Exception:
        # Fallback jika bukan TTY
        return sys.stdin.read(1)

def print_header():
    clear_screen()
    print("\033[96m" + "="*65 + "\033[0m")
    print("\033[92m" + "           KVM MICROVM TERMINAL CONTROL PANEL (TUI)          " + "\033[0m")
    print("\033[90m" + "  Kelola sandbox virtualisasi hardware KVM Anda langsung dari terminal  " + "\033[0m")
    print("\033[93m" + "  TIP: Klik di dalam area terminal ini jika tombol tidak merespons.   " + "\033[0m")
    print("\033[96m" + "="*65 + "\033[0m\n")

def get_sandboxes():
    try:
        res = subprocess.run(["msb", "ls"], capture_output=True, text=True, check=True)
        lines = res.stdout.strip().splitlines()
        sandboxes = []
        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    sandboxes.append({
                        "name": parts[0],
                        "image": parts[1],
                        "status": parts[2],
                        "created": " ".join(parts[3:]) if len(parts) >= 4 else "-"
                    })
        return sandboxes
    except Exception:
        return []

def get_sandbox_status_direct(name):
    try:
        res = subprocess.run(["msb", "ls"], capture_output=True, text=True, check=True)
        for line in res.stdout.strip().splitlines()[1:]:
            parts = line.split()
            if parts and parts[0] == name:
                return parts[2].lower()
    except Exception:
        pass
    return None

def create_menu():
    print_header()
    print("\033[93m=== BUAT MICROVM LOKAL BARU ===\033[0m\n")
    
    # 1. Nama VM
    print("\033[92mMasukkan nama sandbox (default: local-vm): \033[0m", end="", flush=True)
    name = input().strip()
    if not name:
        name = "local-vm"
        
    # 2. Pilihan Image
    print("\n\033[93mPilih OCI / Docker Image:\033[0m")
    print("  [1] Ubuntu 24.04 (Noble Numbat) -- Default")
    print("  [2] Debian Slim")
    print("  [3] Alpine Linux (Sangat Ringan)")
    print("  [4] Python 3.11 Slim")
    print("\033[92mPilih nomor image [1-4, default: 1]: \033[0m", end="", flush=True)
    img_choice = get_char()
    print(img_choice)
    if img_choice == "2":
        image = "debian:slim"
    elif img_choice == "3":
        image = "alpine:latest"
    elif img_choice == "4":
        image = "python:3.11-slim"
    else:
        image = "ubuntu:24.04"
        
    # 3. CPU
    print("\n\033[93mPilih Alokasi CPU:\033[0m")
    print("  [1] 1 vCPU")
    print("  [2] 2 vCPU -- Default")
    print("  [3] 4 vCPU")
    print("\033[92mPilih CPU [1-3, default: 2]: \033[0m", end="", flush=True)
    cpu_choice = get_char()
    print(cpu_choice)
    cpu = "4" if cpu_choice == "3" else ("1" if cpu_choice == "1" else "2")
    
    # 4. RAM
    print("\n\033[93mPilih Alokasi RAM (Memory):\033[0m")
    print("  [1] 512 MB")
    print("  [2] 1 GB -- Default")
    print("  [3] 2 GB")
    print("  [4] 4 GB")
    print("\033[92mPilih RAM [1-4, default: 2]: \033[0m", end="", flush=True)
    ram_choice = get_char()
    print(ram_choice)
    if ram_choice == "1":
        ram = "512M"
    elif ram_choice == "3":
        ram = "2G"
    elif ram_choice == "4":
        ram = "4G"
    else:
        ram = "1G"

    print("\n" + "="*65)
    print(f"\033[94m[1/3] Menarik image '{image}'...\033[0m")
    subprocess.run(["msb", "pull", image])
    
    print(f"\033[94m[2/3] Membuat sandbox '{name}' ({cpu} vCPU, {ram} RAM)...\033[0m")
    res = subprocess.run([
        "msb", "create", 
        "--name", name, 
        "-c", cpu, 
        "-m", ram, 
        image
    ])
    
    if res.returncode == 0:
        if "ubuntu" in image or "debian" in image:
            print("\033[94m[3/3] Melakukan setup awal (install tmux, curl, ca-certificates, fastfetch)...\033[0m")
            setup_cmd = (
                "apt-get update && "
                "apt-get install -y tmux curl ca-certificates && "
                "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb && "
                "apt-get install -y ./fastfetch-linux-amd64.deb && "
                "rm fastfetch-linux-amd64.deb"
            )
            subprocess.run(["msb", "exec", name, "--", "sh", "-c", setup_cmd])
        print(f"\n\033[92m✓ Sandbox '{name}' berhasil dibuat dan dinyalakan!\033[0m")
    else:
        print(f"\n\033[91m✗ Gagal membuat sandbox.\033[0m")
        
    print("\nTekan tombol apa saja untuk kembali ke Menu Utama...")
    get_char()

def vm_operations_menu(vm):
    name = vm["name"]
    while True:
        status = get_sandbox_status_direct(name)
        if not status:
            print(f"\033[91mSandbox '{name}' sudah tidak ada.\033[0m")
            time.sleep(1.5)
            return

        print_header()
        status_color = "\033[92m" if status == "running" else "\033[91m"
        print(f"\033[93mKelola VM: {name}\033[0m \033[90m(Image: {vm['image']})\033[0m")
        print(f"Status   : {status_color}{status.upper()}\033[0m\n")
        
        if status == "running":
            print("  \033[93m[1]\033[0m 🐚 Masuk ke Shell (Bash/Sh) -- LANGSUNG")
            print("  \033[93m[2]\033[0m ⏹️  Hentikan (Stop)")
        else:
            print("  \033[93m[1]\033[0m ▶️  Nyalakan (Start)")
            
        print("  \033[93m[3]\033[0m 🗑️  Hapus Permanen (Remove)")
        print("  \033[93m[B]\033[0m Kembali ke Daftar VM")
        print("\n" + "="*65)
        print("\033[92mPilih opsi [1, 2, 3, B]: \033[0m", end="", flush=True)
        
        choice = get_char().upper()
        print(choice)
        
        if choice == 'B':
            return
            
        if status == "running":
            if choice == "1":
                clear_screen()
                print(f"\033[92mMenghubungkan ke shell '{name}'... Ketik 'exit' untuk kembali ke menu.\033[0m\n")
                try:
                    subprocess.run(["msb", "exec", name, "--", "fastfetch"])
                except Exception:
                    pass
                shell = "bash" if ("ubuntu" in vm["image"] or "debian" in vm["image"]) else "sh"
                subprocess.run(["msb", "exec", name, "--", shell])
            elif choice == "2":
                print(f"\n\033[94mMenghentikan sandbox '{name}'...\033[0m")
                subprocess.run(["msb", "stop", name])
            elif choice == "3":
                print(f"\n\033[91mApakah Anda yakin ingin menghapus {name}? (y/N): \033[0m", end="", flush=True)
                confirm = get_char().lower()
                print(confirm)
                if confirm == 'y':
                    subprocess.run(["msb", "stop", name])
                    subprocess.run(["msb", "rm", name])
                    return
        else:
            if choice == "1":
                print(f"\n\033[94mMenyalakan sandbox '{name}'...\033[0m")
                subprocess.run(["msb", "start", name])
            elif choice == "3":
                print(f"\n\033[91mApakah Anda yakin ingin menghapus {name}? (y/N): \033[0m", end="", flush=True)
                confirm = get_char().lower()
                print(confirm)
                if confirm == 'y':
                    subprocess.run(["msb", "rm", name])
                    return

def manage_menu():
    while True:
        print_header()
        print("\033[93m=== DAFTAR & KELOLA MICROVM ===\033[0m\n")
        
        sandboxes = get_sandboxes()
        if not sandboxes:
            print("  Belum ada sandbox yang dibuat.")
            print("\n" + "="*65)
            print("\nTekan tombol apa saja untuk kembali ke Menu Utama...")
            get_char()
            return
            
        for idx, vm in enumerate(sandboxes, 1):
            status_color = "\033[92m" if vm["status"] == "running" else "\033[91m"
            print(f"  \033[93m[{idx}]\033[0m {vm['name']} \033[90m(Image: {vm['image']})\033[0m - {status_color}{vm['status'].upper()}\033[0m")
            
        print(f"  \033[93m[B]\033[0m Kembali ke Menu Utama")
        print("\n" + "="*65)
        print("\033[92mPilih nomor VM untuk mengelolanya (atau B): \033[0m", end="", flush=True)
        
        choice = get_char().upper()
        print(choice)
        
        if choice == 'B':
            return
            
        try:
            val = int(choice)
            if 1 <= val <= len(sandboxes):
                vm = sandboxes[val - 1]
                vm_operations_menu(vm)
            else:
                print("\n\033[91mNomor tidak valid.\033[0m")
                time.sleep(1)
        except ValueError:
            print("\n\033[91mPilihan tidak valid.\033[0m")
            time.sleep(1)

def main():
    while True:
        print_header()
        print("  \033[93m[1]\033[0m 🚀 Buat (Create) MicroVM Kustom Baru")
        print("  \033[93m[2]\033[0m 🖥️  Daftar & Kelola (List/Manage) MicroVM")
        print("  \033[93m[3]\033[0m 🐚 Masuk ke Shell Host Runner (Normal Bash)")
        print("  \033[93m[4]\033[0m ⏹️  Keluar / Stop Terminal")
        print("\n" + "="*65)
        print("\033[92mPilih opsi [1-4]: \033[0m", end="", flush=True)
        
        choice = get_char()
        print(choice) # Echo karakter yang ditekan
        
        if choice == "1":
            create_menu()
        elif choice == "2":
            manage_menu()
        elif choice == "3":
            clear_screen()
            print("\033[93mMenjatuhkan Anda ke normal bash shell... Ketik 'exit' untuk kembali ke panel TUI.\033[0m\n")
            subprocess.run(["bash"])
        elif choice == "4":
            clear_screen()
            print("Terima kasih telah menggunakan KVM Terminal Panel. Sampai jumpa!")
            sys.exit(0)
        else:
            print("\n\033[91mPilihan tidak valid.\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    local_bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = f"{local_bin_path}:{os.environ.get('PATH', '')}"
    main()
