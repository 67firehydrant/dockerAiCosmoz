# Next.js Docker Deployment Guide (Debian + GHCR + Railway)

Repositori ini menyediakan kerangka dasar untuk men-deploy aplikasi Next.js menggunakan **Docker image berbasis Debian (Node Slim)**, dipublikasikan melalui **GHCR (GitHub Container Registry)**, dan di-deploy ke **Railway**.

---

## 📂 Struktur File

1. **`Dockerfile`**: File konfigurasi Docker berbasis `node:20-slim` (Debian Bookworm). File ini bertugas untuk meng-install dependensi, menyalin kode Next.js Anda, mem-build aplikasi (`npm run build`), dan menjalankannya pada port `3000`.
2. **`package.json`**: Berisi dependensi minimal Next.js & React untuk keperluan testing build awal.
3. **`pages/index.js`**: Halaman landing page uji coba dengan desain premium dark mode yang responsif.
4. **`.github/workflows/deploy.yml`**: GitHub Actions Workflow yang akan otomatis men-build dan melakukan push ke GHCR setiap kali ada push ke branch `main` atau `master`.

---

## 🚀 Langkah 1: Push Kode Anda ke GitHub

Agar GitHub Actions berjalan dan otomatis mem-push image ke GHCR, Anda cukup mengunggah seluruh kode ini ke repositori GitHub Anda sendiri:

1. Buat repositori baru di GitHub.
2. Hubungkan repositori lokal Anda dan lakukan push:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Docker Next.js setup"
   git branch -M main
   git remote add origin git@github.com:USERNAME/NAMA_REPOSITORI.git
   git push -u origin main
   ```
3. Buka tab **Actions** di repositori GitHub Anda untuk memantau proses build.
4. Setelah selesai, Docker image Anda akan muncul di halaman profil GitHub Anda di bawah menu **Packages** dengan alamat:
   `ghcr.io/username/nama-repositori:latest`

> [!IMPORTANT]
> Secara default, GitHub membuat package/image baru di GHCR menjadi **Private**. Jika Anda ingin Railway dapat mengaksesnya secara langsung tanpa credential login, Anda bisa mengubah visibilitas Package tersebut menjadi **Public** melalui halaman pengaturan package di GitHub (Package Settings -> Danger Zone -> Change visibility -> Public).

---

## 🛠️ Langkah 2: Deploy ke Railway

Setelah Docker image terunggah ke GHCR, ikuti langkah berikut untuk men-deploy di Railway:

### Opsi A: Jika Image GHCR Bersifat Public
1. Masuk ke dashboard [Railway](https://railway.app/).
2. Klik **New Project** -> **Deploy from Image**.
3. Masukkan alamat image GHCR Anda, contohnya:
   ```text
   ghcr.io/username/nama-repositori:latest
   ```
4. Railway akan langsung mengunduh image tersebut dan mendeploy-nya.

### Opsi B: Jika Image GHCR Tetap Private (Direkomendasikan untuk Production)
Jika Anda ingin image tetap private, Railway membutuhkan akses ke registry GHCR Anda:
1. Di GitHub, buat **Personal Access Token (Classic)** baru dengan scope `read:packages` melalui [GitHub Token Settings](https://github.com/settings/tokens). Salin token tersebut.
2. Di dashboard Railway, klik **New Project** -> **Deploy from Image**.
3. Klik **Add Registry Credential** atau konfigurasikan credential di bagian settings.
4. Isi data berikut:
   - **Registry**: `ghcr.io`
   - **Username**: Username GitHub Anda.
   - **Password/Token**: Masukkan Personal Access Token (Classic) yang telah Anda salin tadi.
5. Setelah terhubung, masukkan alamat image GHCR Anda dan jalankan deploy.

---

## 🧪 Menguji Docker Secara Lokal (Opsional)

Jika Anda ingin melakukan build dan menjalankan container ini di komputer lokal Anda terlebih dahulu:

1. **Build Docker Image:**
   ```bash
   docker build -t nextjs-docker-test .
   ```

2. **Jalankan Container:**
   ```bash
   docker run -p 3000:3000 nextjs-docker-test
   ```

3. Buka browser dan akses [http://localhost:3000](http://localhost:3000) untuk melihat hasilnya.

---

## 📝 Tips Mengunggah Kode Next.js Anda Sendiri

Ketika Anda siap menguji aplikasi Next.js Anda yang sesungguhnya:
1. Hapus folder `pages` bawaan ini (jika Anda menggunakan App Router Next.js seperti folder `app`).
2. Salin seluruh file kode aplikasi Next.js Anda ke dalam folder ini.
3. Pastikan file `.gitignore` Anda mengabaikan folder `node_modules` dan `.next` agar tidak terunggah ke GitHub.
4. Lakukan commit dan push ke GitHub. GitHub Actions akan memperbarui Docker image Anda di GHCR secara otomatis!
