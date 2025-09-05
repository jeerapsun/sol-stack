#!/usr/bin/env bash
# ----------------------------------------------------------
# setup_ops_center.sh  —  ONE-SHOT INITIALISER
# ----------------------------------------------------------
set -euo pipefail

PROJECT_ROOT="$HOME/sol-stack"
cd "$PROJECT_ROOT"

echo "==> 1. สร้างโครง ‘notion_sync’"
mkdir -p notion_sync

# ---------- requirements.txt ----------
cat > notion_sync/requirements.txt <<'REQ'
notion-client==2.3.0
python-dotenv==1.0.1
schedule==1.2.1
REQ

# ---------- create_struct.py ----------
cat > notion_sync/create_struct.py <<'PY'
#!/usr/bin/env python3
import os, sys, datetime
from notion_client import Client

token="$NOTION_TOKEN"
parent_page = "201e7ac56e9380a6a52dc093ce4ce205"

notion = Client(auth=token)

db = notion.databases.create(
    parent={"page_id": parent_page},
    title=[{"type":"text","text":{"content":"Ops Center Tasks"}}],
    properties={
        "Name":{"title":{}},
        "Status":{"select":{"options":[
            {"name":"Backlog","color":"default"},
            {"name":"In-Progress","color":"yellow"},
            {"name":"Blocked","color":"red"},
            {"name":"Done","color":"green"}]}},
        "Owner":{"people":{}},
        "Due Date":{"date":{}},
        "Priority":{"select":{"options":[
            {"name":"Critical","color":"red"},
            {"name":"High","color":"orange"},
            {"name":"Normal","color":"blue"},
            {"name":"Low","color":"gray"}]}},
        "Tags":{"multi_select":{}},
        "Created by Bot":{"checkbox":{}},
    },
)
db_id = db["id"]
print("Database ID:", db_id)

tasks = [("Daily Ops Checklist","Critical"),
         ("LLM Model Refresh","High"),
         ("Nightly Back-ups","High"),
         ("Docker Image Updates","Normal")]

for name,prio in tasks:
    notion.pages.create(
        parent={"database_id":db_id},
        properties={
            "Name":{"title":[{"type":"text","text":{"content":name}}]},
            "Status":{"select":{"name":"Backlog"}},
            "Priority":{"select":{"name":prio}},
            "Tags":{"multi_select":[{"name":"Bootstrap"}]},
            "Created by Bot":{"checkbox":True},
        })
print("Seed tasks inserted.")

with open("/data/ops_db_id.txt","w") as f:
    f.write(db_id)
PY

# ---------- daily_update.py ----------
cat > notion_sync/daily_update.py <<'PY'
#!/usr/bin/env python3
import os, datetime
from notion_client import Client

token="$NOTION_TOKEN"
db_id  = open("/data/ops_db_id.txt").read().strip()

notion = Client(auth=token)
today  = datetime.date.today().isoformat()
title  = f"Daily Checklist {today}"

existing = notion.databases.query(
    database_id=db_id,
    filter={"property":"Name","title":{"equals":title}}
)["results"]

if existing:
    print("Checklist already exists.")
else:
    notion.pages.create(
        parent={"database_id":db_id},
        properties={
            "Name":{"title":[{"type":"text","text":{"content":title}}]},
            "Status":{"select":{"name":"Backlog"}},
            "Priority":{"select":{"name":"Normal"}},
            "Tags":{"multi_select":[{"name":"Automation"}]},
            "Created by Bot":{"checkbox":True},
        })
    print("Checklist created.")
PY

# ---------- Dockerfile ----------
cat > notion_sync/Dockerfile <<'DOCKER'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY create_struct.py daily_update.py /app/
RUN mkdir /data
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
RUN echo "0 0 * * * root python /app/daily_update.py >> /var/log/cron.log 2>&1" > /etc/cron.d/notion-sync
RUN chmod 0644 /etc/cron.d/notion-sync && crontab /etc/cron.d/notion-sync
CMD cron -f
DOCKER

echo "==> 2. แก้ Dockerfile sol_agent เพื่อติดตั้ง openai"
grep -q "openai" sol_agent/Dockerfile || \
  echo 'RUN pip install --no-cache-dir openai==1.15.0' >> sol_agent/Dockerfile

echo "==> 3. เขียน docker-compose.override.yml"
cat > docker-compose.override.yml <<'YML'
services:
  notion_sync:
    build:
      context: ./notion_sync
    volumes:
      - notion-sync-data:/data
    restart: unless-stopped
    depends_on:
      - llm
volumes:
  notion-sync-data:
YML

echo "==> 4. สร้าง/อัปเดต .env (บันทึก Token ไว้เพื่อใช้ภายหลัง)"
cat > .env <<'ENV'
# สำหรับ service อื่น ๆ ในอนาคต
NOTION_TOKEN="$NOTION_TOKEN"
ENV

echo "==> 5. Build และสตาร์ต service"
docker compose build notion_sync sol_agent
docker compose up -d notion_sync sol_agent

echo "==> 6. รัน bootstrap เพื่อสร้าง Database + seed tasks"
docker compose run --rm notion_sync python /app/create_struct.py

echo "===== เสร็จสมบูรณ์ ====="
echo "ตรวจผลลัพธ์ได้ที่หน้า Notion ‘Ops Center Tasks’"
