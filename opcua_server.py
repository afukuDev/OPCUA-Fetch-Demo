# opcua_server.py
# 建立一個簡單的 Async OPC UA Server
# 提供變數：Temperature (°C), Weight (g), Tray1~Tray4_vol (ml)
# 預設為 No-Security endpoint（開發測試最簡單）
# 若要開啟 Security，將 USE_SECURITY = True 並提供憑證與私鑰路徑

import os
import asyncio
from asyncua import Server, ua

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Config ----------
USE_SECURITY = False  # <- 改成 True 可啟用 server 端憑證/安全端點（需要先產生憑證與私鑰）
# 若 USE_SECURITY == True，請指定以下兩個檔案路徑（可用 openssl 產生）
CERT_PATH = os.path.join(BASE_DIR, "server_cert.der")   # 可以是 .der 或 .pem
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "server_key.pem")
# ----------------------------

async def main():
    server = Server()
    await server.init()

    # 設定 endpoint（對外綁定 0.0.0.0）
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # 若要只提供 No-Security endpoint（避免 secure endpoint 的 missing cert 警告）
    if not USE_SECURITY:
        # 只提供 NoSecurity policy（這樣 UAExpert 用 Security=None 的 endpoint 連線就會成功）
        server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        print("[OK] OPC UA Server 設為 No-Security（Security=None）")
    else:
        # 嘗試啟用安全（Sign+Encrypt）端點，並載入憑證與私鑰
        try:
            # 選擇一個安全 policy（這是常用且安全的選項）
            server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
            # 載入憑證與私鑰（asyncua 的伺服器 API 支援 await server.load_certificate / load_private_key）
            if not os.path.exists(CERT_PATH) or not os.path.exists(PRIVATE_KEY_PATH):
                print("[Warning] 找不到憑證或私鑰，請先產生並放在指定路徑：")
                print(f"  CERT_PATH = {CERT_PATH}")
                print(f"  PRIVATE_KEY_PATH = {PRIVATE_KEY_PATH}")
                print("[Warning] 目前沒有載入憑證 -> 仍會產生 non-secure endpoint，但 client 若選 secure endpoint 將會失敗")
            else:
                await server.load_certificate(CERT_PATH)
                await server.load_private_key(PRIVATE_KEY_PATH)
                print("[OK] 已載入憑證與私鑰，secure endpoints 已啟用")
        except Exception as e:
            print(f"[Warning] 啟用 Security 時發生錯誤：{e}")
            # 退回 NoSecurity（保證 server 可用）
            server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
            print("[Warning] 已退回 No-Security 模式以維持 server 可用性")

    # 基本資訊
    server.set_server_name("Demo OPCUA Server by Afuku WISE AI Nutrition OPCUA DATA")
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # 建立物件與變數
    obj = await server.nodes.objects.add_object(idx, "SensorData")
    var_temp = await obj.add_variable(idx, "Temperature", 0.0)
    var_weight = await obj.add_variable(idx, "Weight", 0.0)
    var_tray1_vol = await obj.add_variable(idx, "Tray1_vol", 0.0)
    var_tray2_vol = await obj.add_variable(idx, "Tray2_vol", 0.0)
    var_tray3_vol = await obj.add_variable(idx, "Tray3_vol", 0.0)
    var_tray4_vol = await obj.add_variable(idx, "Tray4_vol", 0.0)

    # 允許 Client 寫入（關鍵）
    await var_temp.set_writable()
    await var_weight.set_writable()
    await var_tray1_vol.set_writable()
    await var_tray2_vol.set_writable()
    await var_tray3_vol.set_writable()
    await var_tray4_vol.set_writable()

    # 啟動 server（async context）
    print("[OK] OPC UA Server 已啟動於 opc.tcp://localhost:4840/freeopcua/server/")
    print("[DATA] UA Expert 觀察節點：Objects → SensorData → Temperature / Weight / Tray*_vol")

    try:
        async with server:
            # server 啟動後維持運行（你可以在此做週期性寫入示範）
            while True:
                await asyncio.sleep(1)
    except Exception as e:
        print(f"[Error] Server 運行時發生錯誤：{e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Terminated_by_user] 使用者終止伺服器 (KeyboardInterrupt)")
    except Exception as e:
        print(f"[Error] 主程序例外：{e}")
