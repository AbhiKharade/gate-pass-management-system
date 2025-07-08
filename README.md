# gate-pass-management-system
A smart gate pass management system using QR Code, MySQL, and Tkinter for secure entry-exit tracking.
# 🚪 Gate Pass Management System

A smart gate pass management system using **QR Code**, **MySQL**, and **Tkinter** for secure entry-exit tracking. Designed to streamline entry and exit logging for students, employees, or visitors using both QR scanning and manual options.

---

## ✅ Features

- 🔐 QR Code scanning for secure gate pass verification
- 🧾 Temporary **In/Out** entry tracking system
- 📊 Auto-export of logs to **Excel**
- 📬 Email alerts with timestamp (optional)
- 🖥️ Simple, user-friendly GUI with **Tkinter**
- 🗃️ MySQL database integration for storing logs
- 🧹 Clean and modular Python code for maintainability

---

## 🛠 Tech Stack

- **Python 3.x**
- **Tkinter** – for GUI
- **OpenCV** (optional for face recognition)
- **MySQL** – for storing gate logs
- **Pandas** – for Excel export
- **qrcode** / **pyzbar** – for QR code generation and scanning
- **smtplib** – for sending email notifications

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/AbhiKharade/gate-pass-management-system.git
cd gate-pass-management-system

---

## 🧾 QR Code Generator

This script allows you to generate QR codes for individuals (students, employees, or visitors) which can be scanned later during entry/exit.

### 📁 File:
`qr_generator.py`

### 🛠️ How it Works:

- Takes **input data** (like name, roll number, or ID)
- Generates a QR code image using the **qrcode** library
- Saves the image locally (can be printed or shown on mobile)

### ▶️ Example Usage:

```bash
python qr_generator.py


