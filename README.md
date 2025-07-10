# 📞 Password Cracking Service (Pentera Home Assignment)

This project implements a distributed password cracking system for phone-based passwords (e.g., `05X-XXXXXXX`) that have been hashed using **MD5**.

The system consists of:
- **Minion Service** – Brute-forces a phone number range and returns a match if found.
- **Master Service** – Reads input hashes and distributes work among multiple Minions via REST.

---

## 🚀 How It Works

- The **master** reads one or more MD5 hashes (e.g., from a list or file).
- It splits the full phone number space into chunks (e.g., 4), each assigned to a **Minion**.
- Each **Minion** receives a hash and a phone number range, and checks all numbers in that range.
- If a Minion finds a matching password, it reports it back via REST.

---

## Running the Services

Start 4 Minion (each in a separate terminal)

uvicorn minion.main:app --port 8001
uvicorn minion.main:app --port 8002
uvicorn minion.main:app --port 8003
uvicorn minion.main:app --port 8004

Run the Master

python master/main.py
