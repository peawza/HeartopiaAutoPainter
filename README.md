<div align="center">
  <img height="344" src="https://pic.4th.in/images/2026/03/03/logo837ea97692ea2dcb.png" />
</div>

# 🎨 Heartopia.Help-painter

เครื่องมือช่วยแปลงรูปภาพให้กลายเป็น **Pixel Art** สำหรับไกด์การวาดภาพในเกม **Heartopia** โดยเฉพาะ! ช่วยให้คุณเลือกสีจาก Palette ในเกมได้แม่นยำและวางแผนการวาดได้ง่ายขึ้น
โปรแกรมแปลไทยให้แล้ว ได้ใช้งานได้แบบไม่งงกัน
เปลี่ยนการวาดรูปที่แสนยากใน **Heartopia** ให้กลายเป็นเรื่องง่ายด้วยเครื่องมือตัวช่วยที่คุณเองก็ทำได้! มาดูวิธีติดตั้งแบบ step-by-step กัน สอนใช้ Heartopia Help Painter ให้วาดรูปในเกมได้เทพๆ!

---

<div align="center">
  <img height="400" src="https://pic.4th.in/images/2026/03/04/1.png" />
</div>

---

## Requirements
- Python 3.10 ขึ้นไป
- Pillow (PIL)
- CustomTkinter (สำหรับหน้าจอ UI)
- Windows 10 (ทุก build ตั้งแต่ 1809 ขึ้นไป โดยเฉพาะ 21H2, 22H2) → ใช้ได้แน่นอน
- Windows 11 (ทุก build เช่น 21H2, 22H2, 23H2, 24H2, สูงกว่า+) → ใช้ได้ดีที่สุด
- macOS Intel
- macOS Apple Silicon (M1 / M2 / M3)

---

## ดูวิดีโอสอนใช้งาน [YOUTUBE](https://youtu.be/nr_-wqowNoM?si=U9XXHyDxfqi201iv)
[https://youtu.be/nr_-wqowNoM?si=U9XXHyDxfqi201iv](https://youtu.be/nr_-wqowNoM?si=U9XXHyDxfqi201iv)

---

## 🛠️ การติดตั้งบน Windows Windows (Installation)

โปรแกรมที่ต้องใช้:
* Python 3.10 หรือใหม่กว่า 👉 [https://www.python.org/downloads/](https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe)
* Git 👉 [https://git-scm.com/download/win](https://github.com/git-for-windows/git/releases/download/v2.53.0.windows.1/Git-2.53.0-64-bit.exe)

### ติดตั้งโปรแกรม
- ติดตั้ง **Python** ✅ Add Python to PATH -> กด **Install Now**
- ติดตั้ง **Git** ติดตั้งโดยกด Next ตามค่า Default ได้เลย

### เปิด PowerShell
Start Menu → พิมพ์ PowerShell → Run as Administrator

### ดาวน์โหลดโปรเจกต์จาก GitHub
```bash
git clone https://github.com/Nozeed/Heartopia.Help-painter.git
cd Heartopia.Help-painter
```

### อนุญาตให้รัน Script (สำคัญสำหรับ PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
พิมพ์ `Y` แล้วกด Enter

### สร้าง Virtual Environment
สร้าง environment สำหรับโปรเจกต์:
```bash id="rtyxkk"
python -m venv venv
```

เปิดใช้งาน:
```bash
.\venv\Scripts\Activate.ps1
```
หากสำเร็จจะเห็น `(venv)` ด้านหน้าบรรทัดคำสั่ง

### ติดตั้ง Library ที่จำเป็น
```bash
pip install -r requirements.txt --upgrade
```
รอจนติดตั้งเสร็จ

### เปิดใช้งานโปรแกรม
```bash
python main.py
```

---

## 🍎 การติดตั้งบน macOS Installation Guide
โปรแกรมที่ต้องใช้:
* Python 3.10 หรือใหม่กว่า
* Git
* Homebrew (แนะนำ)

### ติดตั้ง Homebrew (หากยังไม่มี)
เปิด **Terminal** แล้วรัน:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### ติดตั้ง Python
ติดตั้ง Python ผ่าน Homebrew:
```bash
brew install python
```
### ติดตั้ง Git
```bash
brew install git
```
### ดาวน์โหลดโปรเจกต์จาก GitHub
```bash
git clone https://github.com/Nozeed/Heartopia.Help-painter.git
cd Heartopia.Help-painter
```
### สร้าง Virtual Environment
```bash
python3 -m venv venv
#เปิดใช้งาน:
source venv/bin/activate
```
### ติดตั้ง Library ที่จำเป็น
```bash
pip install -r requirements.txt
```
### เปิดใช้งานโปรแกรม
```bash
python main.py
```

---

## ⚠️ วิธีแก้ปัญหาที่พบบ่อย (Troubleshooting)

### ❌ Activate ไม่ได้ (script ถูก block) สำหรับ Windows
รันอีกครั้ง:
```powershell id="v0czr1"
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
แล้วเปิด PowerShell ใหม่


### ❌ pip install ไม่ผ่าน
อัปเดต pip:
```powershell
python -m pip install --upgrade pip
```

### ❌ python ไม่ถูกพบ
ตรวจสอบ PATH:
```powershell
where python
```
หากไม่พบ ให้ติดตั้ง Python ใหม่และติ๊ก **Add Python to PATH**

## ✅ ปิด Virtual Environment เมื่อไม่ได้ใช้งานแล้ว
```powershell
deactivate
```

## 💡 หมายเหตุ
* ควร activate `(venv)` ก่อนรันทุกครั้ง
* แนะนำ PowerShell เวอร์ชันล่าสุด
* สามารถนำไป build เป็น `.exe` ได้ในอนาคต

---

## ตัวอย่างรูปที่วาด (รูปใช้ [ChatGPT](https://chatgpt.com/) สร้าง)

รูปวาดขนาด 1:1 (ใหญ่) ใช้ค่าวาด **ตั้งค่า/ค่าที่เหมาะสมที่สุดตอนนี้**
<div align="center">
<img height="500" src="https://pic.4th.in/images/2026/03/04/ChatGPT-Image-Mar-4-2026-11_30_58-AM2e4e2275f6ccbcf0.jpg"  /><br />
<img src="https://pic.4th.in/images/2026/03/04/nozeed-1.png"  />  <img height="400" src="https://pic.4th.in/images/2026/03/04/nozeed-2.png"  />
</div>

---

## 🎨 ขนาดรูปที่แนะนำ
<div align="center">
  <img src="https://pic.4th.in/images/2026/03/04/Untitled-1.png" />
</div>

---

## ข้อมูลอัพเดทแก้ไข
วิธีอัพเดตโหลดไฟล์ใหม่ไปทับไฟล์เดิมได้เลย
### Update 04/03/26
- เพิ่ม 9:16 (ทดสอบแล้วใช้ได้) [ดูตัวอย่างที่นี้](https://pic.4th.in/images/2026/03/05/image.png)
- สี UI ใหม่ ขาว-ชมพู-ม่วง โทนสว่างได้ดูง่ายๆ
- แปลไทยเพิ่มเติม แก้ไขคำผิด
- แก้ Overlay ขณะวาดให้ดูง่ายขึ้น
- เพิ่มการ ตั้งค่า-จังหวะ เน้นความแม่นยำสูง (วาดนาน) ดูที่แฟ้ม ตั้งค่า
- ตั้งค่าจังหวะ default ใหม่ให้เหมาะสม (ตอนเปิดโปรแกรมครั้งแรกก่อนตั้งค่าใหม่)
### Update 28/02/26
- แก้การซูมตอนกด scroll mouse ขึ้นตอนเลือก พื้นที่ Canvas.. ให้ซูมได้ สูงสุด x12
- แก้ Overlay ให้มองง่าย ได้ลากรูปง่ายและตรงกับเกมมากขึ้น

---

ที่มา : [https://github.com/PckyDev/Heartopia-Image-Painter](https://github.com/PckyDev/Heartopia-Image-Painter)
### โปรแกรมตัวนี้ผมนำมาแก้ไขและแปลให้ใช้งานได้ง่ายขึ้น

---

## ใครโลกสวยให้ไปแจ้งผู้พัฒนาเกมครับไม่ต้องมาร้องงอแงดิ้นแถวนี้
- ส่วนใครกลัวโดนแบนแนะนำอย่าใช้ครับ :)
- สุดท้าย งดมาม่านะครับ แค่โปรแกรมช่วยวาด ไม่ใช่ Hack สะหน่อยงอแงไปได้

---

<div align="center">
  <img height="125" src="https://pic.4th.in/images/2026/02/11/NOZEED_LOGO2.png"  />  <img height="125" src="https://pic.4th.in/images/2026/03/02/donate-logo.png"  />
</div>
"# HeartopiaAutoPainter" 
