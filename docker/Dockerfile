# Menggunakan base image Node.js berbasis Debian Bookworm Slim
FROM node:20-slim

# Menentukan direktori kerja di dalam container
WORKDIR /app

# Install utility dasar Debian yang sering dibutuhkan untuk troubleshooting/testing
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Menyalin file package.json dan package-lock.json (jika ada)
COPY package*.json ./

# Menginstall dependencies aplikasi
# Gunakan npm ci jika ada package-lock.json untuk build yang lebih konsisten
RUN npm install

# Menyalin seluruh kode aplikasi Next.js ke dalam container
COPY . .

# Build aplikasi Next.js untuk produksi
RUN npm run build

# Menentukan environment variable untuk produksi
ENV NODE_ENV=production
ENV PORT=3000

# Mengekspos port 3000 (port default Next.js)
EXPOSE 3000

# Menjalankan aplikasi Next.js
CMD ["npm", "start"]
