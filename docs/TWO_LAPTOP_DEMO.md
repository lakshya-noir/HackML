# Two-laptop setup: Mahesh runs the UI

Laptop 1 hosts data, trained model and FastAPI. Laptop 2 (Mahesh) serves the static evaluator UI. Both must join the same reachable network. A local one-machine check does not prove this network requirement.

Final default: **pathsnap-monotone-v1**, `artifacts/models/final_monotone_v1` plus `artifacts/decoder_config.json`. No environment overrides needed; clear any earlier `PATHSNAP_MODEL_DIR` override. `/health` must report this release and `model_loaded: true`, with hashes matching `artifacts/final_release.json`. Pull/restart the backend to adopt it; browser refresh alone does not replace a running API. The UI shows the release after prediction.

## Laptop 1 — Lakshya or Nakul

From the repository root, with local data imported:

```bash
git pull --ff-only origin main
python -m pip install -r requirements-demo.txt
python -m pathsnap.api.app --host 0.0.0.0 --port 8000
```

Use `.venv/bin/python` on Lakshya's Mac. On another machine activate its Python environment first. The default development partition is `data/student_test`, not reserved evaluator data. When organisers authorise final testing, restart with `--trips-dir data/evaluator_test` (or the actual provided directory). References remain server-side for metrics only.

Find Laptop 1's active Wi-Fi IPv4 address: macOS System Settings → Wi-Fi → Details → TCP/IP; Windows `ipconfig`. Do not use 127.0.0.1 or 0.0.0.0 as the address on Laptop 2.

## Laptop 2 — Mahesh

Only Python's standard library and the repository UI folder are needed. No ML installation, dataset or model is needed here.

```bash
git clone https://github.com/lakshya-noir/HackML.git
cd HackML
# If already cloned, use: git pull --ff-only origin main
python -m http.server 5500 --bind 127.0.0.1 --directory ui
```

On macOS/Linux use `python3` if `python` is unavailable; on Windows `py` also works. Open **http://localhost:5500** in Mahesh's browser. In the API box enter **http://LAPTOP_1_IP:8000**, click **Connect**, select a trip, leave **Run fresh inference** checked, then click **Predict route**.

Example only: if Laptop 1's actual IP is 192.168.1.20, enter `http://192.168.1.20:8000`. The UI also accepts `http://localhost:5500/?api=http://192.168.1.20:8000` for prefilling. Replace example IP with the real one.

Before opening the UI, open `http://LAPTOP_1_IP:8000/health` from Mahesh's browser. It must return `model_loaded: true` and the expected number of trips. This proves reachability, not full inference.

During prediction, show the receiving API terminal on Laptop 1. The request must arrive from Mahesh's LAN IP, not just 127.0.0.1. Capture this and Mahesh's rendered route/metrics as demo evidence. Bundled Leaflet works without internet; background street tiles still need internet. Road and GPS geometry remain visible without tiles.

Optional network smoke test from Mahesh's repository root (standard library only):

```bash
python scripts/smoke_test_api.py --api http://LAPTOP_1_IP:8000
```

## Troubleshooting

- Cannot reach health: confirm actual IP, same Wi-Fi, backend running with `--host 0.0.0.0`, and inbound TCP 8000 allowed on Laptop 1's private network. Campus Wi-Fi can isolate clients; use a shared hotspot if needed.
- Health works but model not loaded: check saved model and pinned ML dependencies on Laptop 1; read terminal error.
- UI shows code/file list: use the HTTP URL above, not an editor tab or the wrong served directory.
- Prediction errors: retain the actual error and server logs; do not display made-up routes.
- UI scores differ from the earlier five-model chart: API evaluation uses monotone route alignment on full trips, while the initial chart used nearest-reference labels on sampled points. Both remain geometric surrogates and are not directly interchangeable.
