# ใช้ Python image เป็นฐาน (แนะนำให้ใช้เวอร์ชันเดียวกับโค้ดของคุณ)
FROM python:3.9-slim

# กำหนด working directory
WORKDIR /app

# --- ส่วนที่สำคัญที่สุด ---
# ก๊อปปี้ไฟล์ requirements.txt เข้ามาก่อน
COPY requirements.txt .

# สั่งติดตั้ง library จากไฟล์นี้เท่านั้น
RUN pip install -r requirements.txt
# -------------------------

# ก๊อปปี้โค้ดที่เหลือทั้งหมดเข้ามา
COPY . .

# คำสั่งสุดท้ายที่จะรัน
CMD ["python", "main.py"]