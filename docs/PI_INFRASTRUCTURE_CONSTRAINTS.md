# 🚫 DO NOT BREAK — Sentinel-Pi Infrastructure Constraints

This system runs **Home Assistant Supervised** on top of Raspberry Pi OS, alongside
other services (Pi-hole, Ollama, DuckDB, NAS, Docker workloads, Kubernetes, etc.).

**If a change affects networking, containers, IPv6, storage, or the virtual environment — stop and check this file first.**

---

## 1. NetworkManager MUST remain installed and active

Home Assistant Supervisor depends on NetworkManager for:
- network configuration
- mDNS / multicast discovery
- IPv6 link-local addressing (required for Matter)

### ❗ Do NOT:
- replace NetworkManager with systemd-networkd
- disable NetworkManager
- let Kubernetes CNI override or remove NetworkManager
- use netplan to replace NM

Kubernetes is allowed **as long as NetworkManager stays in control of the host network**.

---

## 2. Docker MUST remain the container runtime

Supervisor manages add-ons through Docker.

### ❗ Do NOT:
- uninstall Docker
- replace Docker with Podman
- replace Docker with containerd as the primary runtime
- let Kubernetes remove or override Docker

You may install containerd for Kubernetes, but Docker must remain installed and functional.

---

## 3. IPv6 MUST remain enabled

Matter requires:
- IPv6 link-local addresses
- IPv6 multicast
- mDNS over IPv6

### ❗ Do NOT:
- disable IPv6 globally
- disable IPv6 on interfaces used by Home Assistant
- block IPv6 multicast in firewall rules
- let Pi-hole disable IPv6 networking

If IPv6 is disabled, **Matter Bridge will not work**.

---

## 4. Avahi (mDNS) and Multicast MUST remain active

Home Assistant, Matter, and many integrations rely on:
- mDNS service discovery
- multicast DNS advertisements

### ❗ Do NOT:
- disable Avahi
- block mDNS (UDP 5353)
- block multicast traffic
- let firewall rules drop mDNS packets

---

## 5. NAS Mount MUST persist across reboots

All pipeline scripts reference `/mnt/data/sentinel-pi` via `config.py`.
This path is a platform constant — hardcoded across all scripts.

**fstab entry (permanent):**
```
UUID=c28c2621-fe58-4591-8009-84983b3938bf /mnt/data ext4 defaults,nofail 0 2
```

### ❗ Do NOT:
- remount NAS to a different path
- remove or modify the fstab entry without updating `config.py`
- replace NAS device without updating UUID in fstab

**`nofail` is required** — without it, Pi hangs on boot if NAS is unavailable.

**Verify after any storage change:**
```bash
sudo mount -a
ls /mnt/data/sentinel-pi
```

**Incident reference:** ADR-014 (2026-03-08)

---

## 6. Virtual Environment MUST remain intact

Pipeline cron runs via:
```
/mnt/data/sentinel-pi/.venv/bin/python3
```

Dependencies are pinned in `requirements.txt`.

### ❗ Do NOT:
- run server upgrades without checking venv afterwards
- install system Python packages that conflict with venv
- delete or recreate venv without reinstalling from requirements.txt

**Recovery command if venv breaks:**
```bash
/mnt/data/sentinel-pi/.venv/bin/python3 -m pip install -r requirements.txt
```

**Verify venv health:**
```bash
/mnt/data/sentinel-pi/.venv/bin/python3 -c "import duckdb; import xarray; print('venv OK')"
```

**Permanent solution:** Docker Phase 2 — containers isolate dependencies from host entirely.

**Incident reference:** ADR-013 (2026-03-08)

---

## ✔ Summary

As long as you keep the following intact and running — the platform remains stable:

| Constraint | Why |
|------------|-----|
| NetworkManager | Home Assistant Supervisor |
| Docker | Home Assistant Add-ons |
| IPv6 | Matter Bridge |
| Avahi/mDNS | Service discovery |
| /mnt/data mount | All pipeline scripts |
| .venv | Cron pipeline execution |

This setup supports:
- Home Assistant Supervised
- Pi-hole
- Ollama + Phi3
- DuckDB / Parquet / Iceberg
- NAS services
- Docker workloads
- Kubernetes (with care)
- Matter Bridge
- Alexa local control
- Zigbee2MQTT
- Sentinel-Pi data platform

### ❗ Do NOT run unattended system upgrades
System Python upgrades break venv dependencies.
Before any apt upgrade:
1. Note current venv state
2. Run upgrade
3. Immediately verify venv:
   /mnt/data/sentinel-pi/.venv/bin/python3 -c "import duckdb; print('OK')"
4. If broken: pip install -r requirements.txt