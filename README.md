                    # Roaming Sol-Stack: AI-Powered Workflow Automation & Graph Memory

Roaming Sol‑Stack เป็นเครื่องมือ open‑source สำหรับ workflow automation (ใช้ n8n) และการประมวลผู้กลบข้อมูลกราฟ (Zep Graph) ที่ออกแบบมาให้ทำงานร่วมกับเอเจนต์ได้อย่างลงตัว รองรับการใช้งานข้ามแพลตฟอร์มระหว่าง Mac และ Windows มีระบบจัดการเวอร์ชันผ่าน Git และมีเส้นทาง I/O ที่ปรับแต่งได้เพื่อประสิทธิภาพสูงสุดสำหรับสำหรับเอเจนต์ AI เช่น SOL

## Features

- **Agent‑Driven Dev**: เอเจนต SOL สามารถสร้างและอัปเดตโค้ดและส่งขึ้น Git แบบอัตโนมัติ
- **Memory & Workflows**: ใช้ Zep สำหรับบันทึกความรู้ระยะยาว และใช้ n8n เชื่อมต่อนการทำงานจากหลายแห่งข้อมูล
- **I/O Optimization**: รองรับอินพุต/เอาต์พุตประเคษหลายรูปแบบ (APIs/ไฟล์) ส่งออกข้อมูลเป็น JSON หรือ YAML พร้อมระบบประมวลผู้อัตโนมัติ
- **Best Practices 2025**: ผสาน LangGraph สำหรับจัดการลำดับการทำงาน ใช้งานร่วมกับ Copilot และระบบที่ปลอดภัย ด้วยการเข้ารหัสโทเคน

## Quick Start

1. Clone repository: `git clone https://github.com/jeerapsun/sol-stack`
2. Setup environment: `./agentctl bootstrap-roaming-workstation`
3. Develop feature: `./agentctl agent-develop "add new feature"`
4. Push changes: การส่งขึ้น Git จะทำผ่านสคริปต์ `git-auto-commit.sh`

## License

This project is licensed under the MIT License.

