# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from datetime import datetime



app = Flask(__name__)
CORS(app)  # 允許跨域

# 載入模型
print("🔍 正在載入模型...")
model = tf.keras.models.load_model("backend/model/model_0.93.keras")
print("✅ 模型載入成功！")
print("🔍 正在載入多類別模型...")
detailed_model = tf.keras.models.load_model("backend/model/model_0.84.keras")
detailed_classes = [
    'R_Glass', 'R_Paper', 'R_Papercontainer', 'R_can',
    'R_other', 'R_plastic', 'R_plasticcontainer'
]
detailed_label_map = {
    
    "R_Glass": "玻璃",
    "R_Paper": "紙類",
    "R_Papercontainer": "紙容器",
    "R_can": "金屬罐",
    "R_other": "其他回收物",
    "R_plastic": "塑膠",
    "R_plasticcontainer": "塑膠容器"
}
print("✅ 多類別模型載入成功！")
# 圖片預處理函數
def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

# API：上傳圖片並預測分類
@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    img_bytes = file.read()
    img_tensor = preprocess_image(img_bytes)
    pred = model.predict(img_tensor)[0][0]
    label = "可回收" if pred > 0.5 else "不可回收"
    return jsonify({"result": label, "confidence": float(pred)})

# backend/app.py 的开头
# …

# 定义一个项目外的存储路径
WRONG_ROOT = os.path.expanduser("~/smartbin_wrong_data")

@app.route("/collect_wrong", methods=["POST"])
def collect_wrong():
    file = request.files['file']
    label = request.form.get('label', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = os.path.join(WRONG_ROOT, label)
    os.makedirs(save_path, exist_ok=True)
    file.save(os.path.join(save_path, f"{timestamp}.jpg"))
    return jsonify({"status": "saved"})

@app.route("/predict_detailed", methods=["POST"])
def predict_detailed():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    img_bytes = file.read()
    img_tensor = preprocess_image(img_bytes)

    preds = detailed_model.predict(img_tensor)[0]
    idx = int(np.argmax(preds))
    eng_label = detailed_classes[idx]
    zh_label  = detailed_label_map.get(eng_label, eng_label)
    confidence = float(preds[idx])

    return jsonify({
        "eng_label":   eng_label,
        "label":       zh_label,   # 使用中文
        "confidence":  confidence
    })

if __name__ == '__main__':
    app.run(debug=True)
    
    
#conda activate smartbin
#cd "C:\Users\ajack\OneDrive\桌面\智慧垃圾桶專案"
#python backend/app.py

#C:\Users\ajack\smartbin_wrong_data