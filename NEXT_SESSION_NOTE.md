# Next Session Note (2026-02-18)

## Current status
- Working branch: `branch2`
- Docker Desktop is installed.
- Project imports were fixed for Docker runtime:
  - `backend.app...` -> `app...`
  - `bot.app...` -> `app...`
- `AGENTS.md` is now ignored in git (`.gitignore` updated).
- `.env` was created from `.env.example` locally.

## Main blocker before running project
- Docker engine cannot start yet.
- Root cause from Docker logs: virtualization is unavailable and `VirtualMachinePlatform`/WSL prerequisites are not active for runtime.

## What to do after reboot
1. Enter BIOS on MSI laptop (`Delete` at boot) and enable:
   - `Intel Virtualization Technology` = `Enabled`
2. Boot into Windows.
3. Confirm in Task Manager -> Performance -> CPU:
   - `Virtualization: Enabled`
4. Run PowerShell as Administrator:
   ```powershell
   wsl --install --no-distribution
   ```
5. Reboot if Windows asks.
6. Start Docker Desktop and wait until it says engine is running.
7. In project folder run:
   ```powershell
   cd D:\JSONStatham
   docker compose -f docker-compose.dev.yml up --build
   ```
8. Verify backend:
   - `http://localhost:8000/health`

## First task after environment starts
- Continue Day 1 validation:
  - Backend health endpoint OK.
  - Bot container starts without import errors.
  - Then proceed to next plan item (subscription flow hardening).
