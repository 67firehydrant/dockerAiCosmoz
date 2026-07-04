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

## Fitur Utama Masing-masing Lingkungan
| Fitur | Docker Sandbox | Microsandbox (KVM) | Modal Sandbox (Cloud) |
| :--- | :--- | :--- | :--- |
| **Lokasi** | Lokal | Lokal | Cloud |
| **Teknologi** | Kontainer Docker | MicroVM (libkrun) | Kontainer gVisor |
| **Kebutuhan Biaya** | Gratis | Gratis | Bayar (Batas Kredit $30/bulan) |
| **Batas Waktu** | Tidak ada | Tidak ada | Sesuai Timeout (maks. 1 jam) |
| **Persistensi File** | Ya (Mount & Writable overlay) | Ya (Writable overlay) | Tidak (Hilang saat exit) |
| **Mount Workspace** | Ya (Bisa akses folder proyek) | Tidak | Tidak |

---

## 4. Pilihan D: GitHub Actions (Testing & CI/CD di Runner GitHub)

Kami telah menambahkan konfigurasi alur kerja GitHub Actions di berkas [.github/workflows/test-sandbox.yml](file:///workspaces/dockerAiCosmoz/.github/workflows/test-sandbox.yml) yang dapat melakukan hal berikut:
1.  **Build & Push**: Membangun Docker image kustom Anda dan menyimpannya di **GitHub Container Registry (GHCR)** secara gratis.
2.  **KVM Runner Test**: Menjalankan pengujian MicroVM (`msb`) langsung di atas runner GitHub Actions (karena runner Linux GitHub mendukung virtualisasi hardware KVM!).

### Cara Memicu Pengujian di GitHub Actions:
1. Commit semua berkas baru ke repository Anda.
2. Push ke branch `main`.
3. Alur kerja akan berjalan secara otomatis, atau Anda dapat memicunya secara manual dari tab **Actions** di repositori GitHub Anda (melalui fitur *workflow_dispatch*).
