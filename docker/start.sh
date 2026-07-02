#!/bin/sh
set -e

# Port internal aplikasi. Dibuat tetap 3000 agar cocok dengan ingress
# Cloudflare Tunnel (arahkan hostname tunnel -> http://localhost:3000).
export PORT="${PORT:-3000}"
export HOSTNAME="0.0.0.0"

# Jalankan Cloudflare Tunnel bila token tersedia.
# Token diset lewat ENV di Railway (JANGAN di-bake ke image publik).
if [ -n "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
  echo "[start] Menjalankan Cloudflare Tunnel (IP origin disembunyikan di balik Cloudflare)..."
  cloudflared tunnel --no-autoupdate run --token "$CLOUDFLARE_TUNNEL_TOKEN" &
else
  echo "[start] CLOUDFLARE_TUNNEL_TOKEN belum diset — tunnel dilewati, hanya menjalankan aplikasi."
fi

echo "[start] Menjalankan aplikasi Next.js di port ${PORT}..."
exec node server.js
