# 🚀 SafeRoute - Secure Reverse Proxy & API Gateway

SafeRoute is a FastAPI-based reverse proxy and API gateway that provides secure access to external services using API key authentication, per-user rate limiting, and flexible host-path routing.

---

## 📌 Features

- 🔐 API Key-based authentication per user
- 📊 Configurable API call limits (per minute)
- 🔁 Reverse proxy support with dynamic routing (`host + path`)
- 🧑‍💻 User-specific API keys and proxy mappings
- 🛡️ Admin APIs to create, delete, and manage proxies and paths
- 🗄️ MySQL as the primary backend for persistent storage

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/safe-route.git
cd safe-route
pip install -r requirements.txt