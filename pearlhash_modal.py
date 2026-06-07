"""
Pearlhash Miner on Modal.com — H100
"""
import modal
import base64
import urllib.request

app = modal.App("pearlhash-miner")
WALLET = "prl1p4c86af87x6xlyqynnk7gd9px3tdrq9uvck4c7hlfefd82cn2jp8qfw6gew"
POOL_HOST = "pool.pearlhash.xyz:9000"
WORKER = "modal-h100"

pearlhash_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.4.0-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install("curl", "libgomp1")
    .run_commands(
        "curl -L --retry 5 --retry-delay 3 "
        "-H 'User-Agent: curl/7.88.1' "
        "-H 'Accept: */*' "
        "https://pearlhash.xyz/downloads/pearl-miner-v12 "
        "-o /opt/pearl-miner && "
        "chmod +x /opt/pearl-miner && "
        "ls -la /opt/pearl-miner"
    )
)

@app.function(
    gpu="H100",
    image=pearlhash_image,
    timeout=86400,
    scaledown_window=300,
)
def mine():
    import subprocess
    print("[Modal] Pearlhash Miner on H100")
    print(f"[Modal] Pool: {POOL_HOST}")
    print(f"[Modal] Wallet: {WALLET}")
    proc = subprocess.Popen(
        ["/opt/pearl-miner", "--host", POOL_HOST, "--user", WALLET, "--worker", WORKER],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in iter(proc.stdout.readline, b""):
        print(line.decode().strip(), flush=True)
    return proc.wait()

@app.local_entrypoint()
def main():
    mine.remote()
