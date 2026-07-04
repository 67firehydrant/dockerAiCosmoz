# Gunakan Ubuntu 24.04 sebagai base image
FROM ubuntu:24.04

# Hindari prompt interaktif saat instalasi paket
ENV DEBIAN_FRONTEND=noninteractive

# Update package list dan instal paket esensial
RUN apt-get update && apt-get install -y \
    tmux \
    curl \
    ca-certificates \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Unduh dan pasang fastfetch dari rilis GitHub resmi (karena tidak ada di repo bawaan Ubuntu 24.04)
RUN curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb \
    && apt-get install -y ./fastfetch-linux-amd64.deb \
    && rm fastfetch-linux-amd64.deb

# Atur working directory default
WORKDIR /workspace

# Jalankan fastfetch secara otomatis saat shell dibuka, lalu jalankan bash
CMD ["sh", "-c", "fastfetch && exec bash"]
