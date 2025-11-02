from flask import Flask, jsonify
from flask_cors import CORS
from asyncua import Client
import asyncio

app = Flask(__name__)
CORS(app)

OPCUA_URL = "opc.tcp://localhost:4840/freeopcua/server/"

@app.route("/data")
def get_data():
    try:
        data = asyncio.run(read_opcua())
        print(f"✅ 傳回資料: {data}")
        return jsonify(data)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return jsonify({"temperature": None, "weight": None, "error": str(e)})

async def read_opcua():
    async with Client(url=OPCUA_URL) as client:
        client.set_security_string("None")  # 關閉安全機制
        temp_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Temperature"])
        weight_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Weight"])
        tray1_vol_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Tray1_vol"])
        tray2_vol_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Tray2_vol"])
        tray3_vol_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Tray3_vol"])
        tray4_vol_node = await client.nodes.root.get_child(["0:Objects", "2:SensorData", "2:Tray1_vol"])

        temp = await temp_node.read_value()
        weight = await weight_node.read_value()
        tray1_vol = await tray1_vol_node.read_value()
        tray2_vol = await tray2_vol_node.read_value()
        tray3_vol = await tray3_vol_node.read_value()
        tray4_vol = await tray4_vol_node.read_value()
        return {"temperature": temp, "weight": weight, "tray1": tray1_vol, "tray2": tray2_vol, "tray3": tray3_vol, "tray4": tray4_vol}

if __name__ == "__main__":
    print("🚀 Flask API running at http://localhost:5000/data")
    app.run(host="0.0.0.0", port=5000, debug=True)
