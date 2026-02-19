#  Historical Court – ระบบศาลจำลองด้วย Multi-Agent (Google ADK)

##  1) บทนำ (Introduction)

โครงงานนี้พัฒนาระบบ *Multi-Agent System* ด้วย *Google ADK* เพื่อจำลองกระบวนการวิเคราะห์บุคคลหรือเหตุการณ์ทางประวัติศาสตร์ในรูปแบบ *“ศาลจำลอง” (Historical Court)*

แนวคิดหลักของระบบ คือ  ให้ Agent หลายตัวทำงานร่วมกันในบทบาทที่แตกต่างกัน เพื่อสร้างรายงานที่มีความสมดุล (Balanced Perspective) โดยไม่เลือกข้าง

ระบบแบ่งบทบาทออกเป็น 3 ฝ่ายหลัก:

-  *Agent A – The Admirer* → รวบรวมข้อดี / ผลงาน  
-  *Agent B – The Critic* → รวบรวมข้อวิจารณ์ / ข้อโต้แย้ง  
-  *Agent C – The Judge* → ตรวจสอบความสมดุลและควบคุม Loop  

ผลลัพธ์สุดท้ายคือรายงานเชิงเปรียบเทียบที่เป็นกลาง และบันทึกลงไฟล์ verdict.txt

---

##  2) แนวคิดการออกแบบระบบ (System Design Concept)

ระบบนี้ออกแบบตามหลัก *Separation of Responsibility*  
แต่ละ Agent มีหน้าที่ชัดเจน ไม่ทับซ้อนกัน

###  Execution Flow (ภาพรวมลำดับการทำงาน)

ลำดับการทำงาน:

1. รับหัวข้อจากผู้ใช้
2. แยกการค้นคว้าเป็น 2 มุมมองพร้อมกัน
3. Judge ตรวจสอบความสมดุล
4. หากข้อมูลไม่ครบ → ปรับ keyword และวนใหม่
5. เมื่อครบถ้วน → สร้างรายงาน
6. บันทึกผลลงไฟล์

โครงสร้างนี้ช่วยให้ระบบ:

-  ไม่ลำเอียง
-  ไม่จบงานเร็วเกินไป
-  ไม่เกิด infinite loop
-  ควบคุม execution flow อย่างมีระบบ

---

##  3. โครงสร้าง Agent (Architecture Overview)

Root (SequentialAgent)
├─ Initializer
├─ Inquiry Agent
├─ Review Loop (LoopAgent)
│ ├─ Parallel Investigation (ParallelAgent)
│ │ ├─ Admirer Agent
│ │ └─ Critic Agent
│ └─ Judge Agent
└─ Verdict Writer
└─ Verdict Saver



---

##  4. รายละเอียด Agent แต่ละตัว

---

## 4.1 Initializer (State Setup)

*หน้าที่:*  
กำหนดค่าเริ่มต้นของ session state เพื่อป้องกัน KeyError

State ที่กำหนด เช่น:

- topic
- pos_data
- neg_data
- loop_count
- max_loops

Agent นี้ทำงานก่อน Agent อื่นเสมอ

---

## 4.2 Inquiry Agent (Sequential Step)

*หน้าที่:*

- ขอหัวข้อจากผู้ใช้
- ตรวจสอบความถูกต้อง
- บันทึกหัวข้อใน topic

ต้องเรียก: 


หากไม่เรียก tool นี้  
Agent ถัดไปจะไม่สามารถใช้ {topic?} ได้

---

## 4.3 Admirer Agent (Parallel Step)

*บทบาท:* ฝ่ายสนับสนุน (Positive Side)

*หน้าที่:*

- ค้นคว้าข้อมูลด้านบวกจาก Wikipedia
- คีย์เวิร์ดเช่น:
  - achievements
  - legacy
  - contributions
- สรุปอย่างน้อย 3 ประเด็น
- บันทึกลง pos_data

---

## 4.4 Critic Agent (Parallel Step)

*บทบาท:* ฝ่ายวิพากษ์ (Critical Side)

*หน้าที่:*

- ค้นคว้าข้อมูลด้านลบ / ข้อโต้แย้ง
- คีย์เวิร์ดเช่น:
  - controversy
  - criticism
  - ethical issues
- สรุปอย่างน้อย 3 ประเด็น
- บันทึกลง neg_data

---

## 4.5 Judge Agent (Loop Controller)

*บทบาท:* ผู้ควบคุมความสมดุล

หน้าที่:

- ตรวจนับ bullet ของทั้งสองฝ่าย
- หาก ≥ 3 ทั้งคู่ → เรียก exit_loop()
- หากไม่ครบ → ปรับ keyword และวนใหม่
- จำกัดรอบด้วย max_loops

เหตุผลที่ใช้ LoopAgent:

เพื่อสร้าง Self-Correcting Mechanism  
ให้ระบบสามารถตรวจสอบและแก้ไขตนเองได้


---

## 4.6 Verdict Writer

หน้าที่:

- สร้างรายงานแบบเป็นกลาง
- เปรียบเทียบข้อดีและข้อวิจารณ์
- ห้ามเลือกข้าง
- ห้ามประกาศผู้ชนะ

โครงสร้างรายงาน:

- Introduction
- Key Achievements
- Criticisms / Controversies
- Balanced Assessment
- Conclusion

---

## 4.7 Verdict Saver

หน้าที่:

- เรียก save_verdict()
- บันทึกไฟล์ verdict.txt

การแยก Writer และ Saver ช่วยให้โครงสร้างชัดเจนและ modular มากขึ้น

---

##  5. การจัดการ State (Session State Management)

ระบบใช้ ToolContext สำหรับเก็บข้อมูลระหว่าง Agent

## State Keys

| Key | ความหมาย |
|------|-----------|
| topic | หัวข้อ |
| pos_data | ข้อมูลด้านบวก |
| neg_data | ข้อมูลด้านลบ |
| pos_count | จำนวน bullet ฝั่งบวก |
| neg_count | จำนวน bullet ฝั่งลบ |
| loop_count | จำนวนรอบ |
| max_loops | จำนวนรอบสูงสุด |
| verdict_text | รายงานฉบับเต็ม |

ใช้ syntax:


เพื่อ inject ค่าเข้า instruction

---

## 6. หลักการควบคุม Loop

ระบบต้องจบ Loop ด้วย:


ห้ามใช้ข้อความธรรมดาเพื่อจบ loop

เหตุผล:

- ป้องกัน premature termination
- ควบคุม execution flow
- เป็นไปตามข้อกำหนดของ Google ADK


 
 ## จุดเด่นของระบบ

- ใช้ Multi-Agent จริง
- มี Parallel execution
- มี Loop ตรวจสอบความสมดุล
- ใช้ Wikipedia tool
- มี State Management ชัดเจน
- ควบคุมการจบ Loop อย่างถูกต้อง
- แยก Writer และ Saver อย่างเป็นระบบ


## สรุป ##

ระบบ Historical Court แสดงให้เห็นว่า
Multi-Agent System สามารถจำลองกระบวนการวิเคราะห์เชิงเหตุผลได้อย่างเป็นระบบ ผ่านการ:
- แยกมุมมอง
- ตรวจสอบความสมดุล
- ควบคุมการทำงานด้วย Loop
- สร้างรายงานที่เป็นกลาง

เป้าหมายของระบบไม่ใช่เพื่อ “ตัดสินว่าใครถูกหรือผิด”  แต่เพื่อสะท้อนความซับซ้อนของประวัติศาสตร์ผ่านหลายมุมมองอย่างมีเหตุผล
