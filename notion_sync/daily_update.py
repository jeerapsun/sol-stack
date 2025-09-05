import os
#!/usr/bin/env python3
import os, datetime
from notion_client import Client

token = os.getenv("NOTION_TOKEN")
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
