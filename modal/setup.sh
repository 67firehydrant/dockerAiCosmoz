#!/usr/bin/env bash

# Skrip Setup Lingkungan Modal Sandbox
# Dibuat oleh Antigravity

set -e

# Warna untuk output terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Setup Lingkungan Modal Sandbox ===${NC}"

# 1. Periksa python3 dan pip
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 tidak ditemukan. Harap install Python3 terlebih dahulu.${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 tidak ditemukan. Harap install pip3 terlebih dahulu.${NC}"
    exit 1
fi

# 2. Install library Modal
echo -e "${BLUE}[1/3] Menginstal library modal via pip...${NC}"
pip3 install -U modal

# 3. Berikan permission execute ke run_sandbox.py
echo -e "${BLUE}[2/3] Mengatur izin eksekusi run_sandbox.py...${NC}"
chmod +x "$(dirname "$0")/run_sandbox.py"

# 4. Membantu autentikasi modal
echo -e "${BLUE}[3/3] Memverifikasi autentikasi Modal...${NC}"
if ! modal profile list &> /dev/null; then
    echo -e "${YELLOW}Anda belum masuk (login) ke Modal.${NC}"
    echo -e "Silakan ikuti instruksi browser yang akan terbuka untuk masuk ke akun Modal Anda."
    echo -e "Menjalankan 'modal setup'..."
    modal setup
else
    echo -e "${GREEN}Autentikasi Modal sudah terkonfigurasi dengan benar!${NC}"
fi

echo -e "\n${GREEN}=== Setup Selesai! ===${NC}"
echo -e "Sekarang Anda dapat menjalankan sandbox dengan perintah:"
echo -e "  ${YELLOW}./run_sandbox.py${NC}"
echo -e "\nContoh parameter lain yang bisa digunakan:"
echo -e "  - Menggunakan ubuntu: ${YELLOW}./run_sandbox.py --image ubuntu${NC}"
echo -e "  - Alokasi memori & CPU spesifik: ${YELLOW}./run_sandbox.py --cpu 2 --memory 2048${NC}"
echo -e "  - Menyalin folder lokal sebelum masuk shell: ${YELLOW}./run_sandbox.py --upload ./kode_lokal /workspace/app${NC}"
echo -e "  - Menggunakan Modal Volume persisten: ${YELLOW}./run_sandbox.py --volume my-vol-name /data${NC}"
