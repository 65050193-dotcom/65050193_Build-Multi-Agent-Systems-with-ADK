Historical Court Multi-Agent System

Built with Google ADK + Gemini + Wikipedia Tool

1. System Overview

โปรเจกต์นี้เป็นระบบ Multi-Agent Architecture ที่จำลอง “ศาลประวัติศาสตร์ (Historical Court)” โดยใช้แนวคิดการแยกบทบาทของ Agent เพื่อสร้างรายงานเชิงเปรียบเทียบอย่างสมดุล

ระบบทำงานเป็นลำดับขั้นดังนี้:

Initializer – เตรียม State เริ่มต้น

Inquiry – รับหัวข้อประวัติศาสตร์จากผู้ใช้

Parallel Investigation – เก็บข้อมูลด้านบวกและด้านลบแบบขนาน

Judge Loop – ตรวจสอบความสมดุลของข้อมูล

Verdict Writer – เขียนรายงานเชิงวิเคราะห์แบบเป็นกลาง

Verdict Saver – บันทึกผลลัพธ์ลงไฟล์

สถาปัตยกรรมถูกออกแบบให้:

แยกหน้าที่ชัดเจน (Separation of Concerns)

ใช้ State เป็นศูนย์กลาง (State-driven orchestration)

ป้องกัน infinite loop

บังคับให้ข้อมูลมีความสมดุลก่อนเขียนรายงาน

2. Architecture Overview

โครงสร้างหลักของระบบ:

SequentialAgent (historical_court)
│
├── initializer
├── inquiry_agent
├── review_loop (LoopAgent)
│ ├── parallel_investigation (ParallelAgent)
│ │ ├── admirer_agent
│ │ └── critic_agent
│ └── judge_agent
│
├── verdict_writer
└── verdict_saver

ประเภทของ Agent ที่ใช้:

SequentialAgent – ควบคุมลำดับหลักของระบบ

ParallelAgent – ทำงานสองฝั่งพร้อมกัน

LoopAgent – วนลูปตรวจสอบคุณภาพข้อมูล

Tool-based state control – ใช้ ToolContext เป็น Shared Memory

3. State Management Design

ระบบใช้ ToolContext.state เป็น Shared Memory กลาง

State Keys ที่สำคัญ
Key	ความหมาย
topic	หัวข้อประวัติศาสตร์
pos_data	ข้อมูลด้านบวก (bullets)
neg_data	ข้อมูลด้านลบ (bullets)
pos_keywords	คีย์เวิร์ดขยายการค้นหาฝั่งบวก
neg_keywords	คีย์เวิร์ดขยายการค้นหาฝั่งลบ
loop_count	จำนวนรอบที่วน
max_loops	จำนวนรอบสูงสุด
pos_count	จำนวน bullet ฝั่งบวก
neg_count	จำนวน bullet ฝั่งลบ
verdict_text	รายงานฉบับสมบูรณ์

แนวคิดสำคัญ:
Agent ไม่สื่อสารกันโดยตรง แต่สื่อสารผ่าน State

4. Step-by-Step Agent Explanation
Step 0: initializer

หน้าที่:

เรียก init_defaults

สร้างค่า default ให้ state ทุกตัว

ป้องกัน missing key error

หลักคิด:
State ต้องถูก initialize ก่อนระบบเริ่มทำงาน

Step 1: inquiry_agent

หน้าที่:

ขอหัวข้อประวัติศาสตร์จากผู้ใช้

ตรวจสอบว่าเป็น Historical topic จริง

ถ้าถูกต้อง เรียก set_state(key="topic")

Validation Logic:

ห้ามเป็น celebrity ปัจจุบัน

ต้องเป็น historical figure หรือ historical event

หลักคิด:
ควบคุมคุณภาพ input ก่อนเข้าสู่ pipeline

Step 2: Parallel Investigation

โครงสร้าง:

ParallelAgent
├── admirer_agent
└── critic_agent

admirer_agent

บทบาท: เก็บข้อมูลด้านบวกเท่านั้น

ใช้ tool:

wikipedia_search อย่างน้อย 3 ครั้ง

set_state(key="pos_data")

เงื่อนไข:

อย่างน้อย 3 bullet

แต่ละบรรทัดต้องขึ้นต้นด้วย "- "

critic_agent

บทบาท: เก็บข้อมูลด้านลบหรือ controversy

ใช้ tool:

wikipedia_search อย่างน้อย 3 ครั้ง

set_state(key="neg_data")

เงื่อนไข:

อย่างน้อย 3 bullet

ต้องไม่ซ้ำกัน

หลักคิดของ Parallel Design:

ลดเวลา

ป้องกัน bias

สร้าง dual-perspective reasoning

5. Step 3: Judge Loop (Quality Control Layer)

โครงสร้าง:

LoopAgent
├── parallel_investigation
└── judge_agent

judge_agent

ลำดับการทำงาน:

เรียก check_balance()

แสดงสถานะ JUDGE_STATUS

ถ้า pos_count >= 3 และ neg_count >= 3 → exit_loop()

ถ้ายังไม่ครบ → bump_loop()

ถ้า loop_count < max_loops → refine_keywords()

ถ้าเกิน max_loops → exit_loop()

เครื่องมือที่ใช้:

check_balance

bump_loop

refine_keywords

exit_loop

หลักคิดของ Loop Design:

ทำหน้าที่เป็น Quality Assurance Layer

บังคับให้ข้อมูลครบทั้งสองด้าน

ป้องกัน imbalance

ป้องกัน infinite loop

มี hard stop ผ่าน max_loops

6. Step 4: verdict_writer

หน้าที่:

นำ pos_data และ neg_data มาเขียนรายงาน

ต้องเป็นกลาง

ห้ามเลือกข้าง

โครงสร้างรายงาน:

Introduction

Key Achievements / Positive Contributions (bullets)

Criticisms / Controversies (bullets)

Balanced Assessment (2–4 paragraphs)

Conclusion

หลังจากเขียนเสร็จ:
set_state(key="verdict_text")

7. Step 5: verdict_saver

หน้าที่:

เรียก save_verdict(verdict_text)

บันทึกลงไฟล์ verdict.txt

จบการทำงาน

8. Tool System Explanation

ระบบใช้ Tool 2 ประเภทหลัก

1. External Tool

wikipedia_search
ใช้ LangChain Wikipedia API
ดึงข้อมูลจริงจาก Wikipedia

2. State Control Tools

init_defaults

set_state

bump_loop

refine_keywords

check_balance

save_verdict

exit_loop

9. Design Philosophy

ระบบนี้ออกแบบตามหลัก:

Separation of Responsibility
แต่ละ Agent มีหน้าที่เดียว

Bias Mitigation
ใช้ dual-agent (Admirer vs Critic)

Controlled Iteration
ใช้ Judge + LoopAgent

Deterministic Structure
Sequential flow ชัดเจน

State-driven reasoning
ข้อมูลไหลผ่าน state ไม่ไหลผ่าน prompt ตรง ๆ

10. Safety and Control Mechanisms

จำกัดจำนวนรอบด้วย max_loops

บังคับ exit_loop()

ห้าม verdict_writer เลือกข้าง

ตรวจสอบ input ตั้งแต่ต้น

11. Conceptual Summary

ระบบนี้จำลองโครงสร้างศาล:

บทบาท	Agent
เตรียมระบบ	initializer
รับคำร้อง	inquiry_agent
ฝ่ายสนับสนุน	admirer_agent
ฝ่ายคัดค้าน	critic_agent
ผู้พิพากษา	judge_agent
ผู้เขียนคำตัดสิน	verdict_writer
ผู้บันทึกผล	verdict_saver

นี่คือ Multi-Agent System ที่มี:

Parallel reasoning

Iterative validation

Structured report generation

Tool-driven state orchestration
