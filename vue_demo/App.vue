<template>
  <div class="dashboard">
    <h1>🍱AI IOT 測試用即時監測儀表板</h1>
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

// 從環境變數讀後端 base URL（在 .env 用 VITE_API_BASE）
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

// 轉小數 1 位；若不是數值回 "-"
const fmt1 = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? Number(n).toFixed(1) : "-";
};

async function fetchData() {
  try {
    // 後端的路由：/data （你的 Flask 程式）
    const res = await axios.get(`${API_BASE}/data`, { timeout: 3000 });
    const d = res.data || {};
    weight.value = fmt1(d.weight);
    tray1.value   = fmt1(d.tray1);
    tray2.value   = fmt1(d.tray2);
    tray3.value   = fmt1(d.tray3);
    tray4.value   = fmt1(d.tray4);
  } catch (err) {
    console.error("Fetch error:", err);
    // 顯示短暫連線失敗符號（保持畫面穩定）
    // 不要把值清空以免 UI 一直跳
  }
}

onMounted(() => {
  fetchData();
  setInterval(fetchData, 1000); // 每秒更新
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

/* 橫向排列＋自動換行 */
.card-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}

/* 卡片樣式 */
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
