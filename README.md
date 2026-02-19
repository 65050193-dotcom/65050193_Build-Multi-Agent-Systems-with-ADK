# Historical Court: Multi-Agent Analysis Framework (Google ADK)

---

## **1) Introduction**

โครงงานนี้เป็นการพัฒนาระบบ **Multi-Agent Analytical Framework** โดยใช้ **Google Agent Development Kit (ADK)** เพื่อจำลองกระบวนการวิเคราะห์เชิงเหตุผลของบุคคลหรือเหตุการณ์ทางประวัติศาสตร์ในลักษณะ “ศาลวิเคราะห์” (Analytical Court Model)

แนวคิดหลักของระบบคือ การแยกบทบาทการวิเคราะห์ออกเป็นหลาย Agent ที่มีหน้าที่แตกต่างกันอย่างชัดเจน เพื่อสร้างผลลัพธ์ที่มีความสมดุล (Balanced Evaluation) และลดอคติจากมุมมองเดียว

ระบบแบ่งโครงสร้างเชิงบทบาทออกเป็น 3 กลไกหลัก:

- **Admirer Agent** – วิเคราะห์ผลงานและคุณูปการ  
- **Critic Agent** – วิเคราะห์ข้อโต้แย้งและประเด็นวิพากษ์  
- **Judge Agent** – ตรวจสอบความครบถ้วนและควบคุมรอบการทำงาน  

ผลลัพธ์สุดท้ายคือรายงานวิเคราะห์เชิงเปรียบเทียบที่เป็นกลาง และบันทึกลงไฟล์ `verdict.txt`

---

## **2) Design Principles**

ระบบนี้ออกแบบตามหลักสถาปัตยกรรมดังต่อไปนี้:

### **2.1 Separation of Concerns**
แต่ละ Agent มีหน้าที่เฉพาะ ไม่ทำงานทับซ้อนกัน

### **2.2 Parallel Reasoning**
การวิเคราะห์ด้านบวกและด้านลบเกิดขึ้นพร้อมกันเพื่อลด bias

### **2.3 Controlled Iteration**
ใช้ LoopAgent เพื่อตรวจสอบคุณภาพข้อมูลก่อนสรุปผล

### **2.4 Deterministic Flow Control**
ควบคุมลำดับการทำงานด้วย SequentialAgent อย่างชัดเจน

---

## **3) Execution Flow**

ลำดับกระบวนการทำงานของระบบมีดังนี้:

1. รับหัวข้อจากผู้ใช้  
2. บันทึกหัวข้อเข้าสู่ session state  
3. เริ่มกระบวนการค้นคว้าทั้งสองมุมมองแบบขนาน  
4. Judge ตรวจสอบจำนวนประเด็นของแต่ละฝ่าย  
5. หากข้อมูลไม่ครบ → ปรับ keyword และวนรอบใหม่  
6. เมื่อครบเงื่อนไข → สร้างรายงาน  
7. บันทึกผลลัพธ์ลงไฟล์  

โครงสร้างนี้ช่วยให้ระบบ:

- ไม่เอนเอียงไปด้านใดด้านหนึ่ง  
- ไม่สิ้นสุดก่อนข้อมูลครบ  
- ป้องกัน infinite loop  
- ควบคุม execution อย่างมีโครงสร้าง  

---

## **4) System Architecture**

```text
SequentialAgent (historical_court)
│
├── initializer
├── inquiry_agent
├── review_loop (LoopAgent)
│   ├── parallel_investigation (ParallelAgent)
│   │   ├── admirer_agent
│   │   └── critic_agent
│   └── judge_agent
├── verdict_writer
└── verdict_saver
