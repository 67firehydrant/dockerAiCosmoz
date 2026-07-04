# Sandbox CLI Helper

Repository ini berisi skrip untuk mempermudah pembuatan sandbox kontainer/VM secara interaktif dan langsung masuk ke shell asli dari kontainer tersebut. Terdapat tiga pilihan sandbox yang didukung:

1.  **Docker Sandbox (Lokal - Sangat Direkomendasikan)**: Menjalankan container Docker secara lokal. Sangat stabil, data persisten, dan secara otomatis memetakan folder `/workspaces` lokal Anda ke dalam container agar Anda dapat langsung memodifikasi proyek Anda.
2.  **Microsandbox (Lokal - Alternatif KVM)**: Berjalan secara lokal menggunakan teknologi **MicroVM (libkrun)** berbasis KVM. Sangat cepat (boot di bawah 100ms) dan sepenuhnya terisolasi secara hardware.
3.  **Modal Sandbox (Cloud - Berbayar/Quota-based)**: Berjalan secara serverless di cloud Modal.

---

## 1. Pilihan A: Docker Sandbox (Lokal - Terstabil & Direkomendasikan)

Skrip [run_docker.py](file:///workspaces/dockerAiCosmoz/modal/run_docker.py) akan otomatis membangun image lokal menggunakan [Dockerfile](file:///workspaces/dockerAiCosmoz/modal/Dockerfile) jika belum ada, membuat kontainer, memasang volume mount ke direktori kerja Anda, dan masuk ke shell asli.

### Cara Menjalankan
Cukup jalankan perintah berikut:
```bash
./run_docker.py
```
*Secara default skrip akan membuat kontainer bernama `local-docker-sandbox` menggunakan base **Ubuntu 24.04** dengan perkakas `tmux` dan `fastfetch` yang sudah terpasang otomatis.*

### Opsi Parameter Docker Sandbox
*   **Melihat status kontainer sandbox:** `./run_docker.py --list`
*   **Menghentikan kontainer:** `./run_docker.py --stop`
*   **Hapus dan buat ulang kontainer dari awal:** `./run_docker.py --recreate`

---

## 2. Pilihan B: Microsandbox (Lokal - Alternatif MicroVM KVM)

Skrip [run_microsandbox.py](file:///workspaces/dockerAiCosmoz/modal/run_microsandbox.py) akan secara otomatis menginstal `msb` CLI, mengatur izin KVM, menarik image, mengonfigurasi VM, dan menjatuhkan Anda langsung ke terminal interaktif.

### Cara Menjalankan
Cukup jalankan perintah berikut:
```bash
./run_microsandbox.py
```

---

## 3. Pilihan C: Modal Sandbox (Cloud - Memerlukan Kuota/Billing Aktif)

Skrip [run_sandbox.py](file:///workspaces/dockerAiCosmoz/modal/run_sandbox.py) digunakan untuk membuat sandbox di cloud Modal.

### Cara Penggunaan
1.  **Persiapan & Autentikasi**:
    ```bash
    ./setup.sh
    ```
2.  **Menjalankan Sandbox**:
    ```bash
    ./run_sandbox.py
    ```

---

## 4. Pilihan D: GitHub Actions (KVM Web Terminal di Browser & Test CI/CD)

Kami telah menambahkan dua alur kerja GitHub Actions:

### Alur 1: KVM Terminal Dashboard TUI ([interactive-sandbox.yml](file:///workspaces/dockerAiCosmoz/.github/workflows/interactive-sandbox.yml))
Alur ini akan meluncurkan web terminal (`ttyd`) di atas runner GitHub yang langsung menjalankan **TUI Control Panel (Dashboard Terminal)** berbasis menu teks yang ramah pengguna, kemudian men-tunnel port tersebut secara gratis menggunakan **Cloudflare Quick Tunnels** (`try.cloudflare.com`).
Ketika Anda membuka tautan Cloudflare di browser, Anda akan langsung melihat dashboard menu interaktif di dalam terminal tanpa perlu mengetikkan perintah manual untuk membuat, menyalakan, menghentikan, atau masuk ke dalam MicroVM (`msb`)!

#### Cara Menjalankan KVM Terminal Dashboard:
1. Pindahkan berkas (*commit* & *push*) ke repositori GitHub Anda.
2. Buka tab **Actions** di repositori GitHub Anda (di akun utama atau akun kedua hasil fork).
3. Pilih workflow **"Interactive KVM Web Terminal"** di sebelah kiri.
4. Klik **Run workflow**.
5. Buka detail pekerjaan (*Job*), dan Anda akan melihat **Tautan Cloudflare** yang tercetak di log atau di halaman **Job Summary** (contoh: `https://xxxx.trycloudflare.com`).
6. Buka tautan tersebut di browser Anda untuk langsung berinteraksi dengan dashboard terminal Anda (aktif hingga 6 jam)!

### Alur 2: Build & Test Sandbox ([test-sandbox.yml](file:///workspaces/dockerAiCosmoz/.github/workflows/test-sandbox.yml))
Digunakan untuk menguji pembangunan (*build*) image kustom dan melakukan tes fungsionalitas KVM secara otomatis di runner GitHub.

---

## Fitur Utama Masing-masing Lingkungan
| Fitur | Docker Sandbox | Microsandbox (KVM) | Modal Sandbox | GitHub Actions Web Terminal |
| :--- | :--- | :--- | :--- | :--- |
| **Lokasi** | Lokal | Lokal | Cloud | Cloud (Runner GitHub) |
| **Teknologi** | Kontainer Docker | MicroVM (libkrun) | Kontainer gVisor | VM Runner + Cloudflare Tunnel |
| **Kebutuhan Biaya** | Gratis | Gratis | Bayar (Batas $30/bln) | Gratis (Batas 6 jam/run) |
| **Batas Waktu** | Tidak ada | Tidak ada | Maks. 1 jam | Maks. 6 jam |
| **Persistensi File** | Ya (Volume Mount) | Ya (Writable overlay) | Tidak (Hilang saat exit) | Tidak (Hilang setelah 6 jam) |
| **Akses Browser** | Tidak (Lewat terminal) | Tidak (Lewat terminal) | Tidak (Lewat terminal) | **Ya (Terminal Web Interaktif)** |
| **Akses KVM** | Tidak | Ya | Tidak | **Ya (Hardware-isolated)** |

