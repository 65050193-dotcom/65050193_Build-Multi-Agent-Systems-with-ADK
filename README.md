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
```

---

### **4.1 Agent Types Used**

- **SequentialAgent** – ควบคุม execution flow หลักของระบบ  
- **ParallelAgent** – อนุญาตให้หลาย Agent ทำงานพร้อมกัน  
- **LoopAgent** – จัดการกระบวนการทำงานแบบวนซ้ำ (iterative control)  
- **Tool-based Agents** – จัดการ state และเชื่อมต่อ external tools  

---


## **5) Agent Responsibilities**

### **5.1 Initializer**

หน้าที่หลักคือกำหนดค่าเริ่มต้นให้กับ session state เช่น:

- `topic`  
- `pos_data`  
- `neg_data`  
- `loop_count`  
- `max_loops`  

Agent นี้ต้องทำงานก่อน Agent อื่นเสมอ เพื่อป้องกัน error จาก key ที่ยังไม่ถูกกำหนด

---

### **5.2 Inquiry Agent**

หน้าที่:

- ขอหัวข้อจากผู้ใช้  
- ตรวจสอบว่าเป็น historical topic  
- บันทึกค่าเข้าสู่ state  

ตัวอย่างการเรียก tool:

```python
set_state(key="topic", value="<topic>")
```

---

### **5.3 Admirer Agent**

วิเคราะห์เฉพาะมุมมองเชิงบวก โดย:

- ใช้ Wikipedia search  
- ค้นหาคำเช่น `achievements`, `legacy`, `reforms`  
- สร้าง bullet อย่างน้อย 3 ประเด็น  
- บันทึกลง `pos_data`  

---

### **5.4 Critic Agent**

วิเคราะห์เฉพาะมุมมองเชิงวิพากษ์ โดย:

- ใช้ Wikipedia search  
- ค้นหาคำเช่น `controversy`, `criticism`, `ethical issues`  
- สร้าง bullet อย่างน้อย 3 ประเด็น  
- บันทึกลง `neg_data`  

---

### **5.5 Judge Agent**

ทำหน้าที่ควบคุมความสมดุลของข้อมูล

ขั้นตอน:

1. ตรวจนับจำนวน bullet ทั้งสองฝ่าย  
2. หากครบ ≥ 3 ทั้งคู่ → เรียก `exit_loop()`  
3. หากไม่ครบ → เพิ่มรอบ loop และปรับ keyword  
4. จำกัดจำนวนรอบด้วย `max_loops`  

การใช้ `LoopAgent` ทำให้ระบบสามารถ “ตรวจสอบและแก้ไขตนเอง” ได้ก่อนเข้าสู่ขั้นสรุป

---

### **5.6 Verdict Writer**

สร้างรายงานฉบับสมบูรณ์โดยมีโครงสร้างดังนี้:

- Introduction  
- Positive Contributions  
- Critical Perspectives  
- Balanced Analysis  
- Conclusion  

เงื่อนไขสำคัญ:

- ห้ามเลือกข้าง  
- ห้ามประกาศผู้ชนะ  
- ต้องรักษาน้ำเสียงเป็นกลาง  

เมื่อเขียนเสร็จต้องบันทึกลง:

```python
set_state(key="verdict_text", value="<FULL REPORT>")
```

---

### **5.7 Verdict Saver**

หน้าที่:

- เรียก `save_verdict()`  
- บันทึกข้อมูลจาก `verdict_text` ลงไฟล์ `verdict.txt`  

การแยก Writer และ Saver ช่วยให้ระบบมี modular structure ที่ชัดเจน


---

## **6) Session State Management**

ระบบใช้ `ToolContext.state` เป็น shared memory ระหว่าง Agent

### **6.1 State Variables**

| Variable | Description |
|----------|------------|
| `topic` | หัวข้อประวัติศาสตร์ |
| `pos_data` | ประเด็นด้านบวก |
| `neg_data` | ประเด็นด้านลบ |
| `pos_count` | จำนวน bullet ฝั่งบวก |
| `neg_count` | จำนวน bullet ฝั่งลบ |
| `loop_count` | จำนวนรอบปัจจุบัน |
| `max_loops` | จำนวนรอบสูงสุด |
| `verdict_text` | รายงานฉบับเต็ม |

---

### **6.2 State Injection Syntax**

การอ้างอิงค่าภายใน instruction ใช้รูปแบบ:

```text
{topic?}
{pos_data?}
{neg_data?}
```

---

## **7) Loop Termination Policy**

การจบ loop ต้องทำผ่าน tool เท่านั้น:

```python
exit_loop()
```

ห้ามใช้ข้อความธรรมดาแทนคำสั่งจบ loop

เหตุผล:

- ควบคุม execution อย่างถูกต้องตาม ADK  
- ป้องกัน premature termination  
- ป้องกัน infinite execution  

---

## **8) System Strengths**

- ใช้ Multi-Agent Architecture จริง  
- มี Parallel Processing  
- มี Quality Control Loop  
- เชื่อมต่อ Wikipedia Tool  
- มี State Management ชัดเจน  
- ควบคุมการจบ Loop ตามมาตรฐาน ADK  
- โครงสร้าง modular และขยายต่อได้  

---

## **9) Conclusion**

ระบบ Historical Court แสดงให้เห็นว่า Multi-Agent System สามารถนำมาจำลองกระบวนการวิเคราะห์เชิงเหตุผลได้อย่างเป็นระบบ ผ่านกลไก:

- การแยกบทบาท  
- การวิเคราะห์หลายมุมมอง  
- การควบคุมรอบการทำงาน  
- การสร้างรายงานแบบเป็นกลาง  

วัตถุประสงค์ของระบบไม่ใช่การตัดสินถูกหรือผิด  
แต่เพื่อสะท้อนความซับซ้อนของประวัติศาสตร์ผ่านกระบวนการวิเคราะห์เชิงโครงสร้างและมีเหตุผล
