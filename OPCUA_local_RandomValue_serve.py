# opcua_server.py
# 伺服器端自動產生隨機數：
#   - Weight、Tray1_vol～Tray4_vol：每秒更新為 100～800 的隨機值（彼此不同）
#   - 保留 m0 結構（Functions / Parameters / Tags）
#   - 預設 No-Security，可切換 USE_SECURITY=True

import os
import asyncio
import random
from asyncua import Server, ua

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Config ----------
USE_SECURITY = False
CERT_PATH = os.path.join(BASE_DIR, "server_cert.der")
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "server_key.pem")
# ----------------------------

async def main():
    server = Server()
    await server.init()

    # endpoint
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # security
    if not USE_SECURITY:
        server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        print("[OK] No-Security（Security=None）")
    else:
        try:
            server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
            if os.path.exists(CERT_PATH) and os.path.exists(PRIVATE_KEY_PATH):
                await server.load_certificate(CERT_PATH)
                await server.load_private_key(PRIVATE_KEY_PATH)
                print("[OK] 已啟用安全端點")
            else:
                print("[Warning] 缺憑證或私鑰，改用 No-Security")
                server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        except Exception as e:
            print(f"[Warning] Security 失敗：{e} -> No-Security")
            server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

    # 基本資訊
    server.set_server_name("Demo OPCUA Server by Afuku AI Nutrition OPCUA DATA")
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # ---------- m0: 基本功能/參數/標籤（保留結構） ----------
    m0 = await server.nodes.objects.add_object(idx, "m0")
    m0_funcs = await m0.add_object(idx, "Functions")
    m0_params = await m0.add_object(idx, "Parameters")
    m0_tags = await m0.add_object(idx, "Tags")

    # 佔位變數（可日後替換）
    m0_echo = await m0_funcs.add_variable(idx, "EchoEnabled", True)
    m0_mode = await m0_params.add_variable(idx, "Mode", "demo")
    m0_status = await m0_tags.add_variable(idx, "Status", "running")
    for v in (m0_echo, m0_mode, m0_status):
        await v.set_writable()

    # ---------- SensorData ----------
    sensor = await server.nodes.objects.add_object(idx, "SensorData")
    var_temp = await sensor.add_variable(idx, "Temperature", 0.0)  # 保留，不自動更新
    var_weight = await sensor.add_variable(idx, "Weight", 0.0)
    var_t1 = await sensor.add_variable(idx, "Tray1_vol", 0.0)
    var_t2 = await sensor.add_variable(idx, "Tray2_vol", 0.0)
    var_t3 = await sensor.add_variable(idx, "Tray3_vol", 0.0)
    var_t4 = await sensor.add_variable(idx, "Tray4_vol", 0.0)

    # 允許手動寫入（即使伺服器會每秒覆寫 Weight/Tray*_vol）
    for v in (var_temp, var_weight, var_t1, var_t2, var_t3, var_t4):
        await v.set_writable()

    print("[OK] Server @ opc.tcp://localhost:4840/freeopcua/server/")
    print("[DATA] 觀察：Objects → SensorData → Weight / Tray*_vol（每秒亂數 100~800）")

    async def update_random_values():
        """每秒更新 Weight 與 Tray1~4 為 100~800 的互異亂數。"""
        while True:
            # 產生 5 個互異隨機整數（100~800）
            w, t1, t2, t3, t4 = random.sample(range(100, 801), 5)

            # 寫入（用 Double 方便 client 當浮點處理）
            await var_weight.set_value(ua.Variant(float(w), ua.VariantType.Double))
            await var_t1.set_value(ua.Variant(float(t1), ua.VariantType.Double))
            await var_t2.set_value(ua.Variant(float(t2), ua.VariantType.Double))
            await var_t3.set_value(ua.Variant(float(t3), ua.VariantType.Double))
            await var_t4.set_value(ua.Variant(float(t4), ua.VariantType.Double))

            # m0.Tags.Status 也順便跳動一下（非必要）
            await m0_status.set_value(f"running@{w}-{t1}-{t2}-{t3}-{t4}")

            await asyncio.sleep(1.0)

    try:
        async with server:
            # 背景任務：定時更新亂數
            task = asyncio.create_task(update_random_values())
            await task  # 永不返回
    except Exception as e:
        print(f"[Error] Server 運行時發生錯誤：{e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Terminated_by_user] 使用者終止伺服器")
    except Exception as e:
        print(f"[Error] 主程序例外：{e}")
