import os
import subprocess
import threading
import time
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)

# Cache untuk terminal: {sandbox_name: {"port": port, "tunnel_url": url, "process": proc, "cf_process": cf_proc}}
terminals = {}
next_port = 8100

# Lock untuk sinkronisasi operasi msb
msb_lock = threading.Lock()

# Log progres pembangunan di latar belakang
build_logs = []

def run_cmd(cmd, check=True):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def get_sandboxes():
    output = run_cmd(["msb", "ls"])
    sandboxes = []
    lines = output.splitlines()
    if len(lines) > 1:
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                # NAME IMAGE STATUS CREATED
                name = parts[0]
                image = parts[1]
                status = parts[2]
                created = " ".join(parts[3:]) if len(parts) >= 4 else "-"
                sandboxes.append({
                    "name": name,
                    "image": image,
                    "status": status,
                    "created": created
                })
    return sandboxes

def get_system_stats():
    try:
        cpu = run_cmd(["sh", "-c", "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"], check=False)
        ram = run_cmd(["sh", "-c", "free -m | grep Mem | awk '{print int($3/$2 * 100)}'"], check=False)
        return {"cpu": cpu or "0.0", "ram": ram or "0"}
    except Exception:
        return {"cpu": "0.0", "ram": "0"}

# HTML/CSS UI Premium dengan Glassmorphism & Dark Mode
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KVM MicroVM Dashboard Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #080c14;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.06);
            --accent-color: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.35);
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            padding: 2.5rem;
            background-image: 
                radial-gradient(circle at 5% 10%, rgba(59, 130, 246, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 95% 90%, rgba(16, 185, 129, 0.06) 0%, transparent 45%);
            background-attachment: fixed;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            padding-bottom: 1.8rem;
            border-bottom: 1px solid var(--border-color);
        }

        .logo-group h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.3rem;
            letter-spacing: -0.5px;
        }

        .logo-group p {
            color: var(--text-muted);
            font-size: 0.95rem;
        }

        .stats-bar {
            display: flex;
            gap: 1.5rem;
        }

        .stat-badge {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 0.7rem 1.4rem;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        .stat-badge span {
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .stat-value {
            font-weight: 700;
            color: var(--accent-color);
            font-size: 1.1rem;
        }

        /* Grid Layout */
        .grid {
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 2.5rem;
        }

        @media (max-width: 950px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }

        /* Card styles */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2.2rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            margin-bottom: 2.5rem;
            transition: border-color 0.3s;
        }

        .card:hover {
            border-color: rgba(255, 255, 255, 0.09);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            letter-spacing: -0.3px;
        }

        /* VM Cards / List */
        .vm-list {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }

        .vm-item {
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.4rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .vm-item:hover {
            border-color: rgba(59, 130, 246, 0.4);
            background: rgba(255, 255, 255, 0.035);
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(59, 130, 246, 0.06);
        }

        .vm-info h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .vm-meta {
            font-size: 0.88rem;
            color: var(--text-muted);
            display: flex;
            gap: 1.5rem;
        }

        .vm-meta strong {
            color: var(--text-color);
            font-weight: 500;
        }

        .status-badge {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 0.25rem 0.7rem;
            border-radius: 8px;
            letter-spacing: 0.5px;
        }

        .status-running {
            background: rgba(16, 185, 129, 0.12);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.25);
        }

        .status-stopped {
            background: rgba(239, 44, 44, 0.12);
            color: var(--danger);
            border: 1px solid rgba(239, 44, 44, 0.25);
        }

        /* Action Buttons */
        .actions-group {
            display: flex;
            gap: 0.8rem;
        }

        .btn {
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--accent-color);
            color: white;
            box-shadow: 0 4px 15px var(--accent-glow);
        }

        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px var(--accent-glow);
        }

        .btn-danger {
            background: rgba(239, 44, 44, 0.08);
            color: var(--danger);
            border: 1px solid rgba(239, 44, 44, 0.2);
        }

        .btn-danger:hover {
            background: var(--danger);
            color: white;
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .btn-terminal {
            background: rgba(245, 158, 11, 0.12);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.25);
        }

        .btn-terminal:hover {
            background: var(--warning);
            color: #000;
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.25);
        }

        /* Forms */
        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-control {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            padding: 0.85rem 1.1rem;
            border-radius: 10px;
            color: white;
            font-family: inherit;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s;
        }

        .form-control:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }

        select.form-control {
            appearance: none;
            background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
            background-repeat: no-repeat;
            background-position: right 10px center;
        }

        /* Logs Console */
        .console-logs {
            background: rgba(0, 0, 0, 0.45);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.2rem;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.85rem;
            max-height: 250px;
            overflow-y: auto;
            color: #34d399;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.8);
        }

        .log-item {
            margin-bottom: 0.4rem;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <h1>Interactive KVM MicroVM Control Panel</h1>
                <p>Kelola sandbox virtualisasi hardware KVM Anda secara gratis di runner GitHub</p>
            </div>
            <div class="stats-bar">
                <div class="stat-badge">
                    <span>CPU</span>
                    <span class="stat-value" id="stat-cpu">{{ stats.cpu }}%</span>
                </div>
                <div class="stat-badge">
                    <span>RAM</span>
                    <span class="stat-value" id="stat-ram">{{ stats.ram }}%</span>
                </div>
            </div>
        </header>

        <div class="grid">
            <!-- Sisi Kiri: Daftar VM & Konsol Log -->
            <div class="main-content">
                <div class="card">
                    <div class="card-title">
                        <span>Daftar MicroVM Sandboxes</span>
                        <button class="btn btn-secondary" onclick="window.location.reload()">Refresh Panel</button>
                    </div>
                    
                    <div class="vm-list">
                        {% if sandboxes %}
                            {% for vm in sandboxes %}
                            <div class="vm-item">
                                <div class="vm-info">
                                    <h3>
                                        {{ vm.name }}
                                        <span class="status-badge status-{{ vm.status }}">{{ vm.status }}</span>
                                    </h3>
                                    <div class="vm-meta">
                                        <span>Image: <strong>{{ vm.image }}</strong></span>
                                        <span>Dibuat: {{ vm.created }}</span>
                                    </div>
                                </div>
                                <div class="actions-group">
                                    {% if vm.status == 'running' %}
                                        <button class="btn btn-terminal" onclick="openTerminal('{{ vm.name }}')">💻 Terminal Web</button>
                                        <form action="/stop/{{ vm.name }}" method="POST" style="display:inline;">
                                            <button class="btn btn-secondary" type="submit">⏹️ Stop</button>
                                        </form>
                                    {% else %}
                                        <form action="/start/{{ vm.name }}" method="POST" style="display:inline;">
                                            <button class="btn btn-primary" type="submit">▶️ Start</button>
                                        </form>
                                    {% endif %}
                                    <form action="/delete/{{ vm.name }}" method="POST" style="display:inline;" onsubmit="return confirm('Apakah Anda yakin ingin menghapus VM ini?')">
                                        <button class="btn btn-danger" type="submit">🗑️ Hapus</button>
                                    </form>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div style="text-align:center; padding: 3rem; color: var(--text-muted);">
                                Belum ada sandbox yang dibuat. Silakan gunakan panel di sebelah kanan untuk membuat sandbox baru.
                            </div>
                        {% endif %}
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Aktivitas & Log Pembangunan</div>
                    <div class="console-logs" id="console-logs">
                        {% if logs %}
                            {% for log in logs %}
                                <div class="log-item">{{ log }}</div>
                            {% endfor %}
                        {% else %}
                            <div class="log-item" style="color: var(--text-muted);">Menunggu aktivitas pembuatan VM baru...</div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Sisi Kanan: Panel Pembuatan VM Baru -->
            <div class="sidebar">
                <div class="card">
                    <div class="card-title">Buat MicroVM Baru</div>
                    <form action="/create" method="POST">
                        <div class="form-group">
                            <label for="name">Nama Sandbox</label>
                            <input type="text" id="name" name="name" class="form-control" placeholder="contoh: vm-utama" required>
                        </div>
                        <div class="form-group">
                            <label for="image">Docker Image</label>
                            <select id="image" name="image" class="form-control">
                                <option value="ubuntu:24.04">Ubuntu 24.04 (Noble)</option>
                                <option value="debian:slim">Debian Slim</option>
                                <option value="alpine:latest">Alpine Linux</option>
                                <option value="python:3.11-slim">Python 3.11 Slim</option>
                            </select>
                        </div>
                        <div class="form-group font-row" style="display: flex; gap: 1rem;">
                            <div style="flex: 1;">
                                <label for="cpu">Virtual CPU</label>
                                <select id="cpu" name="cpu" class="form-control">
                                    <option value="1">1 vCPU</option>
                                    <option value="2" selected>2 vCPU</option>
                                    <option value="4">4 vCPU</option>
                                </select>
                            </div>
                            <div style="flex: 1;">
                                <label for="memory">RAM (Memory)</label>
                                <select id="memory" name="memory" class="form-control">
                                    <option value="512M">512 MB</option>
                                    <option value="1G" selected>1 GB</option>
                                    <option value="2G">2 GB</option>
                                    <option value="4G">4 GB</option>
                                </select>
                            </div>
                        </div>
                        <button class="btn btn-primary" type="submit" style="width: 100%; justify-content: center; padding: 0.85rem; font-size: 1rem;">
                            ⚡ Bangun & Nyalakan VM
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Gulir konsol otomatis ke bawah
        const consoleLogs = document.getElementById("console-logs");
        consoleLogs.scrollTop = consoleLogs.scrollHeight;

        function openTerminal(name) {
            alert("Mempersiapkan terowongan Cloudflare untuk Terminal Web Anda... Tautan terminal web akan terbuka dalam tab baru sesaat lagi.");
            fetch('/terminal/' + name)
                .then(response => response.json())
                .then(data => {
                    if (data.url) {
                        window.open(data.url, '_blank');
                    } else {
                        alert("Gagal membuka terminal: " + data.error);
                    }
                })
                .catch(err => {
                    alert("Koneksi gagal: " + err);
                });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    stats = get_system_stats()
    sandboxes = get_sandboxes()
    return render_template_string(HTML_TEMPLATE, stats=stats, sandboxes=sandboxes, logs=build_logs)

@app.route("/create", methods=["POST"])
def create_vm():
    name = request.form.get("name")
    image = request.form.get("image")
    cpu = request.form.get("cpu")
    memory = request.form.get("memory")
    
    def build_thread():
        global build_logs
        with msb_lock:
            build_logs.append(f"[{time.strftime('%X')}] Memulai penarikan image {image}...")
            # Pull image
            subprocess.run(["msb", "pull", image])
            
            build_logs.append(f"[{time.strftime('%X')}] Membuat MicroVM '{name}' ({cpu} vCPU, {memory} RAM)...")
            subprocess.run([
                "msb", "create", 
                "--name", name, 
                "-c", str(cpu), 
                "-m", memory, 
                image
            ])
            
            # Setup paket jika bertipe ubuntu/debian
            if "ubuntu" in image or "debian" in image:
                build_logs.append(f"[{time.strftime('%X')}] Menjalankan setup awal kontainer (install tmux, curl, ca-certificates, fastfetch)...")
                setup_cmd = (
                    "apt-get update && "
                    "apt-get install -y tmux curl ca-certificates && "
                    "curl -sLO https://github.com/fastfetch-cli/fastfetch/releases/latest/download/fastfetch-linux-amd64.deb && "
                    "apt-get install -y ./fastfetch-linux-amd64.deb && "
                    "rm fastfetch-linux-amd64.deb"
                )
                subprocess.run(["msb", "exec", name, "--", "sh", "-c", setup_cmd])
                
            build_logs.append(f"[{time.strftime('%X')}] MicroVM '{name}' berhasil dikonfigurasi dan siap dijalankan!")

    thread = threading.Thread(target=build_thread)
    thread.start()
    
    return redirect(url_for("index"))

@app.route("/start/<name>", methods=["POST"])
def start_vm(name):
    run_cmd(["msb", "start", name])
    return redirect(url_for("index"))

@app.route("/stop/<name>", methods=["POST"])
def stop_vm(name):
    # Bersihkan terminal aktif
    if name in terminals:
        term = terminals[name]
        try:
            term["cf_process"].terminate()
            term["process"].terminate()
        except Exception:
            pass
        del terminals[name]
        
    run_cmd(["msb", "stop", name])
    return redirect(url_for("index"))

@app.route("/delete/<name>", methods=["POST"])
def delete_vm(name):
    # Bersihkan terminal aktif
    if name in terminals:
        term = terminals[name]
        try:
            term["cf_process"].terminate()
            term["process"].terminate()
        except Exception:
            pass
        del terminals[name]

    run_cmd(["msb", "stop", name])
    run_cmd(["msb", "rm", name])
    return redirect(url_for("index"))

@app.route("/terminal/<name>")
def open_terminal(name):
    global next_port
    
    if name in terminals:
        # Jika terminal lama masih berjalan, kirimkan URL-nya langsung
        if terminals[name]["process"].poll() is None:
            return jsonify({"url": terminals[name]["tunnel_url"]})
        else:
            del terminals[name]
            
    port = next_port
    next_port += 1
    
    # Jalankan ttyd di port dinamis yang dialokasikan dengan opsi -W (writable)
    shell = "bash" if ("ubuntu" in name or "debian" in name) else "sh"
    ttyd_cmd = ["ttyd", "-W", "-p", str(port), "msb", "exec", name, "--", shell]
    ttyd_proc = subprocess.Popen(ttyd_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Dapatkan path cloudflared secara dinamis relatif ke berkas ini
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cf_binary = os.path.abspath(os.path.join(script_dir, "..", "cloudflared"))
    
    # Gunakan nama binary langsung jika berada di root/PATH runner
    if not os.path.exists(cf_binary):
        cf_binary = "cloudflared"

    cf_log = f"/tmp/cf_{name}.log"
    if os.path.exists(cf_log):
        os.remove(cf_log)
        
    cf_cmd = [cf_binary, "tunnel", "--url", f"http://localhost:{port}"]
    cf_log_file = open(cf_log, "w")
    cf_proc = subprocess.Popen(cf_cmd, stdout=cf_log_file, stderr=cf_log_file)
    
    # Deteksi URL Cloudflare Tunnel
    url = None
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(cf_log):
            with open(cf_log, "r") as f:
                content = f.read()
                if "trycloudflare.com" in content:
                    import re
                    matches = re.findall(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", content)
                    if matches:
                        url = matches[0]
                        break
                        
    if url:
        terminals[name] = {
            "port": port,
            "tunnel_url": url,
            "process": ttyd_proc,
            "cf_process": cf_proc
        }
        return jsonify({"url": url})
    else:
        try:
            cf_proc.terminate()
            ttyd_proc.terminate()
        except Exception:
            pass
        return jsonify({"error": "Gagal membuat Cloudflare Tunnel untuk Web Terminal."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
