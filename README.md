#Historical Court Multi-Agent System
#Built with Google ADK + Gemini + Wikipedia Tool


##1. ภาพรวมของระบบ (System Overview)

โปรเจกต์นี้เป็นระบบ Multi-Agent Architecture ที่จำลอง “ศาลประวัติศาสตร์ (Historical Court)”
โดยใช้แนวคิดการแยกบทบาทของ Agent เพื่อสร้างรายงานเชิงเปรียบเทียบอย่างสมดุล

ระบบทำงานเป็นลำดับขั้นดังนี้:

Initializer → เตรียม State เริ่มต้น

Inquiry → รับหัวข้อประวัติศาสตร์จากผู้ใช้

Parallel Investigation → เก็บข้อมูลด้านบวกและด้านลบแบบขนาน

Judge Loop → ตรวจสอบความสมดุลของข้อมูล

Verdict Writer → เขียนรายงานเชิงวิเคราะห์แบบเป็นกลาง

Verdict Saver → บันทึกผลลัพธ์ลงไฟล์

สถาปัตยกรรมถูกออกแบบให้:

แยกหน้าที่ชัดเจน (Separation of Concerns)

ใช้ State เป็นศูนย์กลาง (State-driven orchestration)

ป้องกัน infinite loop

บังคับให้ข้อมูลมีความสมดุลก่อนเขียนรายงาน
