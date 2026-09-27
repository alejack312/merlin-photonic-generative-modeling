# Slow Python imports on this host (owner action)

- **Found:** 2026-09-26, R0 closeout.
- **Symptom:** `import sklearn` takes ~24 s; `scripts/v4_tcdp/resource_pilot.py --memory-probe-worker` takes 34 s warm and 67 s cold. PR #10 raised that test's timeout; the underlying slowness remains.
- **Likely cause:** Windows Defender real-time scanning of `venv/` (unconfirmed).
- **Action:** owner decides whether to add a Defender exclusion for `C:\Users\cuqui\merlin-quantum-case-study\venv`. This is a security setting, so the owner makes the change. Then re-time `venv/Scripts/python.exe -X importtime -c "import sklearn"`.
- **Why it matters:** every test run and sweep pays this startup cost; R1/R4 pilots measure wall-clock time against resource caps.
