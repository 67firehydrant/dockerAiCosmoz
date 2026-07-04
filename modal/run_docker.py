#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess

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

def check_docker():
    """Memeriksa apakah Docker daemon aktif dan dapat diakses."""
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\033[91mError: Docker tidak terdeteksi atau belum aktif.\033[0m")
        print("Silakan pastikan Docker daemon sudah berjalan di sistem Anda.")
        sys.exit(1)

def ensure_image_built():
    """Memastikan image Docker lokal sudah dibangun."""
    image_id = run_cmd(["docker", "images", "-q", "local-docker-sandbox"], capture=True)
    if not image_id:
        print("\033[94m[1/2] Image 'local-docker-sandbox' tidak ditemukan. Memulai proses pembangunan (build)...\033[0m")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dockerfile_path = os.path.join(script_dir, "Dockerfile")
        if not os.path.exists(dockerfile_path):
            print(f"\033[91mError: Dockerfile tidak ditemukan pada {dockerfile_path}\033[0m")
            sys.exit(1)
        
        # Jalankan docker build
        run_cmd(["docker", "build", "-t", "local-docker-sandbox", script_dir])
        print("\033[92mImage berhasil dibangun!\033[0m")
    else:
        print("\033[92m✓ Image 'local-docker-sandbox' sudah siap.\033[0m")

def get_container_status(name):
    """Mendapatkan status kontainer Docker (running, exited, atau None jika tidak ada)."""
    output = run_cmd([
        "docker", "ps", "-a", 
        "--filter", f"name=^{name}$", 
        "--format", "{{.State}}"
    ], capture=True)
    return output.strip().lower() if output else None

def main():
    parser = argparse.ArgumentParser(
        description="Script untuk meluncurkan Docker Sandbox lokal secara interaktif."
    )
    parser.add_argument(
        "--name",
        default="local-docker-sandbox",
        help="Nama kontainer Docker persisten Anda (default: local-docker-sandbox)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Hapus dan bangun ulang kontainer dari awal"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Hentikan kontainer yang sedang berjalan"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Tampilkan kontainer sandbox Docker yang aktif"
    )
    
    args = parser.parse_args()

    # Memeriksa dependensi Docker
    check_docker()

    # Opsi melihat daftar sandbox Docker
    if args.list:
        print("\033[94mMencari daftar kontainer Docker sandbox...\033[0m")
        run_cmd(["docker", "ps", "-a", "--filter", "ancestor=local-docker-sandbox"])
        sys.exit(0)

    # Opsi menghentikan kontainer
    if args.stop:
        status = get_container_status(args.name)
        if status == "running":
            print(f"\033[94mMenghentikan kontainer '{args.name}'...\033[0m")
            run_cmd(["docker", "stop", args.name])
            print("\033[92mKontainer berhasil dihentikan.\033[0m")
        else:
            print(f"\033[93mKontainer '{args.name}' tidak sedang berjalan (status: {status}).\033[0m")
        sys.exit(0)

    # Memastikan image Docker sudah dibuild
    ensure_image_built()

    # Mengecek status kontainer saat ini
    status = get_container_status(args.name)

    if args.recreate and status is not None:
        print(f"\033[93mMenghapus kontainer lama '{args.name}'...\033[0m")
        if status == "running":
            run_cmd(["docker", "stop", args.name])
        run_cmd(["docker", "rm", args.name])
        status = None

    print(f"\n\033[92m" + "="*60)
    print(f"DOCKER SANDBOX LOKAL BERHASIL DIHUBUNGKAN!")
    print(f"Container Name: {args.name}")
    print(f"Mount Path    : /workspaces -> /workspaces (Lokal)")
    print(f"Untuk keluar dari shell, ketik: exit")
    print(f"Semua data/file yang Anda ubah di dalam kontainer akan tetap persisten.")
    print("="*60 + "\033[0m\n")

    if status is None:
        # Menjalankan kontainer baru secara interaktif
        # Men-share direktori /workspaces agar user bisa mengakses kode proyek lokalnya
        try:
            subprocess.run([
                "docker", "run", "-it",
                "--name", args.name,
                "-v", "/workspaces:/workspaces",
                "local-docker-sandbox"
            ])
        except KeyboardInterrupt:
            print("\n\033[93mKoneksi dihentikan oleh pengguna.\033[0m")
    elif status == "running":
        # Jika kontainer sudah berjalan, gunakan docker exec untuk masuk kembali
        try:
            subprocess.run(["docker", "exec", "-it", args.name, "bash"])
        except KeyboardInterrupt:
            print("\n\033[93mKoneksi dihentikan oleh pengguna.\033[0m")
    else:
        # Jika kontainer ada tapi mati (stopped), nyalakan kembali dan pasang terminal (attach)
        try:
            subprocess.run(["docker", "start", "-ai", args.name])
        except KeyboardInterrupt:
            print("\n\033[93mKoneksi dihentikan oleh pengguna.\033[0m")

if __name__ == "__main__":
    main()
