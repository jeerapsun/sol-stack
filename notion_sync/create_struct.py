import os
#!/usr/bin/env python3
import os, sys, datetime
from notion_client import Client

token = os.getenv("NOTION_TOKEN")
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
