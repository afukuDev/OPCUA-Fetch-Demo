# Vue Web UI Setup (Vite + Vue) — OPC UA Frontend Guide

This document explains how to create a Vue web UI on another machine that reads OPC UA values (via your Flask API) and displays `weight` and `Tray1_vol`–`Tray4_vol`.  
It includes commands, environment settings, and full component code you can copy/paste.

---

## Prerequisites

- Node.js installed (recommended v18+ or v20+). `npm` included.
- Terminal / PowerShell / Bash access.
- A running Flask API that exposes `/data` returning JSON like:
  ```json
  {
    "temperature": 23.4,
    "weight": 136.364,
    "tray1": 0.648,
    "tray2": 0.431,
    "tray3": 0.188,
    "tray4": 0.232
  }
  ```
- Ensure the Flask API is reachable on the network (e.g. `http://localhost:5000/data`).

---

## 1. Create a new Vite + Vue project

Open terminal and run:
```bash
# create project (Vite + Vue)
npm create vite@latest webui -- --template vue

cd webui
npm install
npm install axios
```

---

## 2. Add environment variable

Create `.env` in the project root:
```
# .env
VITE_API_BASE=http://localhost:5000
# Replace the IP above with the machine that runs your Flask API
```

> Vite requires env variables to start with `VITE_` to be available in the client via `import.meta.env`.

---

## 3. Replace `src/App.vue`

Overwrite `src/App.vue` with this component (reads `VITE_API_BASE` and shows weight + trays), the developers can get the same original [file](https://github.com/afukuDev/OPCUA-Fetch-Demo/blob/main/vue_demo/App.vue) in this folder:

```vue
<template>
  <div class="dashboard">
    <h1>🍱AI營養辨識測試用即時監測儀表板</h1>
    <h2>OPC UA 通訊暫存的重量與體積資料</h2>

    <div class="card-row">
      <div class="card">
        <h2>Weight ⚖️</h2>
        <p>{{ weight }} g</p>
      </div>

      <div class="card">
        <h2>Tray1 Volume 🍱</h2>
        <p>{{ tray1 }} ml</p>
      </div>

      <div class="card">
        <h2>Tray2 Volume 🍱</h2>
        <p>{{ tray2 }} ml</p>
      </div>

      <div class="card">
        <h2>Tray3 Volume 🍱</h2>
        <p>{{ tray3 }} ml</p>
      </div>

      <div class="card">
        <h2>Tray4 Volume 🍱</h2>
        <p>{{ tray4 }} ml</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const weight = ref("-");
const tray1 = ref("-");
const tray2 = ref("-");
const tray3 = ref("-");
const tray4 = ref("-");

// Read backend base URL from environment (.env)
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

// Format to 1 decimal place; return "-" if not numeric
const fmt1 = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? Number(n).toFixed(1) : "-";
};

async function fetchData() {
  try {
    const res = await axios.get(`${API_BASE}/data`, { timeout: 3000 });
    const d = res.data || {};
    weight.value = fmt1(d.weight);
    tray1.value   = fmt1(d.tray1);
    tray2.value   = fmt1(d.tray2);
    tray3.value   = fmt1(d.tray3);
    tray4.value   = fmt1(d.tray4);
  } catch (err) {
    console.error("Fetch error:", err);
    // Keep previous values to avoid UI flicker
  }
}

onMounted(() => {
  fetchData();
  setInterval(fetchData, 1000); // update every second
});
</script>

<style>
.dashboard {
  text-align: center;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  padding: 2rem;
}

h1 { margin-bottom: 0.25rem; }
h2 { margin-top: 0.1rem; margin-bottom: 1rem; font-weight: 400; color: #666; }

/* horizontal layout with wrap */
.card-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  width: 220px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  color: #000
}

.card h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.05rem;
}

.card p {
  margin: 0;
  font-weight: 700;
  font-size: 1.05rem;
}
</style>
```

---

## 4. `src/main.js` (if missing)

If `src/main.js` does not exist, create it:

```js
import { createApp } from 'vue'
import App from './App.vue'
createApp(App).mount('#app')
```

---

## 5. Start the dev server (allow remote access)

To allow other machines to access the dev server, start with `--host`:

```bash
# in project root
npm run dev -- --host 0.0.0.0 --port 8080
```

Or add to `package.json`:
```json
"scripts": {
  "dev": "vite --host 0.0.0.0 --port 8080",
  "build": "vite build",
  "preview": "vite preview --port 5000"
}
```

If the machine running the web UI has IP `192.168.0.50`, open from another machine:
```
http://192.168.0.50:8080
```

---

## 6. Ensure Flask API is reachable

- Flask must run with `app.run(host="0.0.0.0", port=5000)`.
- Allow TCP port 5000 through firewall.
- From web UI machine test:
```bash
curl http://localhost:5000/data
```

---

## 7. Optional: Build & deploy

```bash
npm run build
# quick test:
npm install -g serve
serve -s dist -l 3000
# then visit http://<webui-ip>:3000
```

For production use Nginx/Caddy + HTTPS.

