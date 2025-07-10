# Pentera Password Cracking Service

This project is a multicomponent password cracking system for MD5 hashes of Israeli phone numbers (format: `05X-XXXXXXX`).  
It simulates a distributed system using one **master** and multiple **minions**.

## 📦 Components

### 1. Minion
A FastAPI service that receives:
- `hash`: MD5 to crack
- `prefix`: phone prefix (e.g., `050`)
- `range_start`, `range_end`: the phone number range

Each minion processes a range and returns the cracked password (if found).

### 2. Master
Reads hashes from an input file and distributes the work among minions via REST calls.

- Supports crash-handling and task retrying.
- Uses `asyncio.Queue` and multiple workers.
- Saves results to `results.txt`.

---

## 🚀 Running the System

### 1. Setup virtualenv
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt

### 2. Run Minions
uvicorn app.minion.main:app --port 8001
uvicorn app.minion.main:app --port 8002
uvicorn app.minion.main:app --port 8003
uvicorn app.minion.main:app --port 8004
# etc.

### 2. Run Master
python -m app.master.main



