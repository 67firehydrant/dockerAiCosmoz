#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess

try:
    import modal
except ImportError:
    print("\033[91mError: Library 'modal' tidak ditemukan.\033[0m")
    print("Silakan install terlebih dahulu dengan menjalankan:")
    print("  pip install modal")
    print("Kemudian login ke akun Modal Anda dengan:")
    print("  modal setup")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Script untuk membuat Modal Sandbox dan masuk ke shell asli secara interaktif."
    )
    parser.add_argument(
        "--image",
        default="ubuntu",
        choices=["debian", "ubuntu", "python", "alpine"],
        help="Sistem operasi / Image dasar sandbox (default: ubuntu)"
    )
    parser.add_argument(
        "--cpu",
        type=float,
        default=2.0,
        help="Jumlah CPU yang dialokasikan (contoh: 0.5, 1.0, 2.0)"
    )
    parser.add_argument(
        "--memory",
        type=int,
        default=None,
        help="Jumlah memori dalam MB (contoh: 1024, 2048)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Batas waktu hidup sandbox dalam detik (default: 3600 / 1 jam)"
    )
    parser.add_argument(
        "--app-name",
        default="interactive-sandbox",
        help="Nama aplikasi Modal yang digunakan (default: interactive-sandbox)"
    )
    parser.add_argument(
        "--upload",
        nargs=2,
        metavar=("LOCAL_PATH", "REMOTE_PATH"),
        help="Salin file atau folder lokal ke dalam sandbox sebelum masuk ke shell"
    )
    parser.add_argument(
        "--volume",
        nargs=2,
        metavar=("VOLUME_NAME", "MOUNT_PATH"),
        help="Pasang (mount) Modal Volume persisten ke dalam sandbox (contoh: my-volume /data)"
    )
    parser.add_argument(
        "--region",
        default="eu",
        help="Wilayah/Region geografi tempat sandbox berjalan (default: eu)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Tampilkan daftar sandbox/kontainer yang sedang aktif saat ini"
    )
    
    args = parser.parse_args()

    # Opsi cepat untuk melist kontainer yang aktif
    if args.list:
        print("\033[94mMencari kontainer/sandbox yang aktif...\033[0m")
        try:
            subprocess.run(["modal", "container", "list"], check=True)
        except Exception as e:
            print(f"\033[91mGagal mengambil daftar kontainer: {e}\033[0m")
        sys.exit(0)

    # Memilih base image berdasarkan argumen dan menginstal tmux + fastfetch
    if args.image == "debian":
        image = (
            modal.Image.debian_slim()
            .apt_install("tmux", "curl", "ca-certificates")
            .run_commands(
                "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb",
                "apt-get install -y ./fastfetch-linux-amd64.deb",
                "rm fastfetch-linux-amd64.deb"
            )
        )
    elif args.image == "ubuntu":
        image = (
            modal.Image.from_registry("ubuntu:24.04", add_python="3.12")
            .apt_install("tmux", "curl", "ca-certificates")
            .run_commands(
                "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb",
                "apt-get install -y ./fastfetch-linux-amd64.deb",
                "rm fastfetch-linux-amd64.deb"
            )
        )
    elif args.image == "python":
        image = (
            modal.Image.from_registry("python:3.11-slim")
            .apt_install("tmux", "curl", "ca-certificates")
            .run_commands(
                "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb",
                "apt-get install -y ./fastfetch-linux-amd64.deb",
                "rm fastfetch-linux-amd64.deb"
            )
        )
    elif args.image == "alpine":
        image = modal.Image.from_registry("alpine:latest").run_commands("apk update", "apk add tmux fastfetch bash")
    else:
        image = (
            modal.Image.debian_slim()
            .apt_install("tmux", "curl", "ca-certificates")
            .run_commands(
                "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb",
                "apt-get install -y ./fastfetch-linux-amd64.deb",
                "rm fastfetch-linux-amd64.deb"
            )
        )

    # Memeriksa apakah Modal CLI terinstall dan terkonfigurasi
    try:
        subprocess.run(["modal", "profile", "list"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("\033[93mPeringatan: Modal CLI belum terkonfigurasi atau tidak ditemukan.\033[0m")
        print("Silakan jalankan perintah berikut untuk login:")
        print("  modal setup")
        print("Atau pastikan variabel lingkungan MODAL_TOKEN_ID dan MODAL_TOKEN_SECRET sudah diatur.")
        sys.exit(1)

    print(f"\033[94m[1/3] Menghubungkan ke Modal App: '{args.app_name}'...\033[0m")
    try:
        app = modal.App.lookup(args.app_name, create_if_missing=True)
    except Exception as e:
        print(f"\033[91mGagal terhubung ke Modal App: {e}\033[0m")
        sys.exit(1)

    # Konfigurasi parameter pembuatan sandbox
    create_kwargs = {
        "app": app,
        "image": image,
        "timeout": args.timeout,
    }
    
    if args.region:
        create_kwargs["region"] = [args.region]
    if args.cpu is not None:
        create_kwargs["cpu"] = args.cpu
    if args.memory is not None:
        create_kwargs["memory"] = args.memory

    # Menambahkan Volume jika dispesifikasikan
    if args.volume:
        vol_name, mount_path = args.volume
        print(f"\033[94m[Mount] Mempersiapkan Modal Volume '{vol_name}' pada path '{mount_path}'...\033[0m")
        try:
            volume = modal.Volume.from_name(vol_name, create_if_missing=True)
            create_kwargs["volumes"] = {mount_path: volume}
        except Exception as e:
            print(f"\033[91mGagal membuat/menghubungkan Volume: {e}\033[0m")
            sys.exit(1)

    print(f"\033[94m[2/3] Membuat Sandbox dengan image '{args.image}'...\033[0m")
    try:
        # Menjalankan command default "sleep" agar container tetap berjalan
        # sehingga kita dapat masuk ke shell aslinya.
        # Menggunakan 'modal.enable_output()' agar log build image dapat terlihat di terminal.
        with modal.enable_output():
            sb = modal.Sandbox.create(
                "sleep", str(args.timeout),
                **create_kwargs
            )
    except Exception as e:
        print(f"\033[91mGagal membuat sandbox: {e}\033[0m")
        sys.exit(1)

    print("\033[94mMenunggu kontainer siap dan aktif...\033[0m")
    try:
        # Menjalankan perintah dummy 'true' untuk memastikan container sudah berjalan
        process = sb.exec("true")
        process.wait()
        print("\033[92mKontainer siap!\033[0m")
    except Exception as e:
        print(f"\033[93mPeringatan: Gagal memverifikasi status kesiapan kontainer: {e}\033[0m")

    sandbox_id = sb.object_id
    dashboard_url = f"https://modal.com/containers/{sandbox_id}"
    
    print("\n\033[92m" + "="*60)
    print("SANDBOX BERHASIL DIBUAT!")
    print(f"Sandbox ID : {sandbox_id}")
    print(f"Dashboard  : {dashboard_url}")
    print("="*60 + "\033[0m\n")

    # Upload file/folder jika diminta
    if args.upload:
        local_path, remote_path = args.upload
        print(f"\033[94m[Upload] Menyalin '{local_path}' ke '{remote_path}' di dalam sandbox...\033[0m")
        try:
            # Memastikan direktori tujuan ada dengan menjalankan mkdir sebelum copy
            sb.exec("mkdir", "-p", os.path.dirname(remote_path))
            sb.filesystem.copy_from_local(local_path, remote_path)
            print("\033[92mSalin file selesai!\033[0m")
        except Exception as e:
            print(f"\033[91mGagal menyalin file ke sandbox: {e}\033[0m")

    print(f"\033[94m[3/3] Membuka shell asli di dalam sandbox...\033[0m")
    print("\033[93mTips: Tulis 'exit' atau tekan Ctrl+D untuk keluar dari shell.\033[0m\n")
    
    try:
        # Menggunakan 'modal shell' untuk masuk ke sandbox yang sudah berjalan secara interaktif
        subprocess.run(["modal", "shell", sandbox_id])
    except KeyboardInterrupt:
        print("\n\033[93mKoneksi dihentikan oleh pengguna.\033[0m")
    finally:
        print(f"\n\033[91mMembersihkan: Menghentikan Sandbox {sandbox_id}...\033[0m")
        try:
            sb.terminate()
            print("\033[92mSandbox berhasil dihentikan.\033[0m")
        except Exception as e:
            print(f"\033[91mGagal menghentikan sandbox secara otomatis: {e}\033[0m")
            print(f"Anda dapat menghentikannya secara manual di dashboard atau jalankan:")
            print(f"  modal app stop {args.app_name}")

if __name__ == "__main__":
    main()
