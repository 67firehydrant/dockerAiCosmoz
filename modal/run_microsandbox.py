#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess

# Menambahkan path lokal ke PATH environment agar msb bisa ditemukan
local_bin_path = os.path.expanduser("~/.local/bin")
os.environ["PATH"] = f"{local_bin_path}:{os.environ.get('PATH', '')}"

def run_cmd(cmd, check=True, capture=False):
    """Fungsi pembantu untuk menjalankan perintah shell."""
    try:
        if capture:
            res = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return res.stdout.strip()
        else:
            subprocess.run(cmd, check=check)
            return True
    except subprocess.CalledProcessError as e:
        if capture:
            return ""
        raise e

def check_kvm():
    """Memeriksa dan mengatur izin /dev/kvm agar dapat diakses oleh user saat ini."""
    kvm_path = "/dev/kvm"
    if not os.path.exists(kvm_path):
        print("\033[91mError: /dev/kvm tidak ditemukan di sistem Anda.\033[0m")
        print("Pastikan virtualisasi KVM sudah aktif di mesin host Anda.")
        sys.exit(1)
        
    # Periksa apakah user memiliki akses write ke /dev/kvm
    if not os.access(kvm_path, os.W_OK):
        print("\033[93mMengatur izin akses /dev/kvm agar bisa dijalankan tanpa root...\033[0m")
        try:
            # Menggunakan sudo chmod 666 /dev/kvm
            run_cmd(["sudo", "chmod", "666", kvm_path])
            print("\033[92mIzin /dev/kvm berhasil dikonfigurasi!\033[0m")
        except Exception as e:
            print(f"\033[91mGagal mengatur izin /dev/kvm: {e}\033[0m")
            print("Anda mungkin perlu menjalankan: 'sudo chmod 666 /dev/kvm' secara manual.")
            sys.exit(1)

def ensure_msb_installed():
    """Memastikan msb CLI sudah terinstal di sistem."""
    try:
        # Periksa apakah msb terinstall
        subprocess.run(["msb", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\033[93mmsb CLI tidak ditemukan. Memulai instalasi Microsandbox...\033[0m")
        try:
            # Jalankan skrip installer resmi
            install_cmd = "curl -fsSL https://install.microsandbox.dev | sh"
            subprocess.run(install_cmd, shell=True, check=True)
            print("\033[92mInstalasi Microsandbox selesai!\033[0m")
        except Exception as e:
            print(f"\033[91mGagal menginstal msb CLI: {e}\033[0m")
            print("Silakan jalankan secara manual: 'curl -fsSL https://install.microsandbox.dev | sh'")
            sys.exit(1)

def get_sandbox_status(name):
    """Mendapatkan status sandbox berdasarkan namanya."""
    output = run_cmd(["msb", "ls"], capture=True)
    for line in output.splitlines()[1:]:
        parts = line.split()
        if parts and parts[0] == name:
            return parts[2].lower()  # Mengembalikan 'running' atau 'stopped'
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Script untuk meluncurkan Microsandbox (libkrun) lokal secara interaktif."
    )
    parser.add_argument(
        "--image",
        default="ubuntu:24.04",
        help="Docker/OCI Image yang ingin digunakan (default: ubuntu:24.04)"
    )
    parser.add_argument(
        "--cpu",
        type=int,
        default=2,
        help="Jumlah virtual CPU yang dialokasikan (default: 2)"
    )
    parser.add_argument(
        "--memory",
        default="2G",
        help="Jumlah RAM yang dialokasikan, e.g. 512M, 2G (default: 2G)"
    )
    parser.add_argument(
        "--name",
        default="local-ubuntu-sandbox",
        help="Nama untuk sandbox persisten Anda (default: local-ubuntu-sandbox)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Hapus dan buat ulang sandbox dari awal"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Hentikan sandbox yang sedang berjalan untuk menghemat RAM"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Tampilkan daftar sandbox lokal yang ada"
    )
    
    args = parser.parse_args()

    # Memeriksa dependensi sistem
    ensure_msb_installed()
    check_kvm()

    # Opsi melihat daftar sandbox
    if args.list:
        print("\033[94mMencari daftar Microsandbox lokal...\033[0m")
        run_cmd(["msb", "ls"])
        sys.exit(0)

    # Opsi menghentikan sandbox
    if args.stop:
        status = get_sandbox_status(args.name)
        if status == "running":
            print(f"\033[94mMenghentikan sandbox '{args.name}'...\033[0m")
            run_cmd(["msb", "stop", args.name])
            print("\033[92mSandbox berhasil dihentikan.\033[0m")
        else:
            print(f"\033[93mSandbox '{args.name}' sedang tidak aktif (status: {status}).\033[0m")
        sys.exit(0)

    # Mengecek status sandbox saat ini
    status = get_sandbox_status(args.name)

    if args.recreate and status is not None:
        print(f"\033[93mMenghapus sandbox lama '{args.name}' untuk membuat ulang...\033[0m")
        if status == "running":
            run_cmd(["msb", "stop", args.name])
        run_cmd(["msb", "rm", args.name])
        status = None

    if status is None:
        # Tahap Pembuatan Sandbox Baru
        print(f"\033[94m[1/3] Menarik image '{args.image}'...\033[0m")
        run_cmd(["msb", "pull", args.image])

        print(f"\033[94m[2/3] Membuat MicroVM '{args.name}' ({args.cpu} vCPU, {args.memory} RAM)...\033[0m")
        # msb create otomatis men-start container
        run_cmd([
            "msb", "create", 
            "--name", args.name, 
            "-c", str(args.cpu), 
            "-m", args.memory, 
            args.image
        ])

        # Menginstal tmux dan fastfetch pada saat pembuatan pertama kali (jika image ubuntu/debian)
        if "ubuntu" in args.image or "debian" in args.image:
            print("\033[94m[Setup] Memperbarui package list dan menginstal tmux + fastfetch...\033[0m")
            try:
                # Setup apt-get update dan tmux
                setup_cmd = (
                    "apt-get update && "
                    "apt-get install -y tmux curl ca-certificates && "
                    "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb && "
                    "apt-get install -y ./fastfetch-linux-amd64.deb && "
                    "rm fastfetch-linux-amd64.deb"
                )
                run_cmd(["msb", "exec", args.name, "--", "sh", "-c", setup_cmd])
                print("\033[92mSetup otomatis selesai!\033[0m")
            except Exception as e:
                print(f"\033[91mSetup awal gagal: {e}\033[0m")
                print("Anda mungkin perlu menginstal paket-paket secara manual di dalam shell.")
    else:
        # Jika sandbox sudah ada
        print(f"\033[94mMenghubungkan ke sandbox '{args.name}' (Status saat ini: {status})...\033[0m")
        if status == "stopped":
            print("\033[94mMenyalakan kembali MicroVM...\033[0m")
            run_cmd(["msb", "start", args.name])

    print(f"\n\033[92m" + "="*60)
    print(f"MICROVM LOKAL BERHASIL DIHUBUNGKAN!")
    print(f"Sandbox Name: {args.name}")
    print(f"Untuk keluar dari shell, ketik: exit")
    print(f"Data Anda akan tetap tersimpan di dalam VM ini.")
    print("="*60 + "\033[0m\n")

    # Jalankan fastfetch sesaat sebelum masuk shell
    try:
        run_cmd(["msb", "exec", args.name, "--", "fastfetch"])
    except Exception:
        pass

    # Masuk ke shell interaktif menggunakan msb exec
    try:
        shell_cmd = "bash" if ("ubuntu" in args.image or "debian" in args.image) else "sh"
        subprocess.run(["msb", "exec", args.name, "--", shell_cmd])
    except KeyboardInterrupt:
        print("\n\033[93mKoneksi shell dihentikan oleh pengguna.\033[0m")

if __name__ == "__main__":
    main()
