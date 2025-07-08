import cv2
from pyzbar.pyzbar import decode
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import mysql.connector
from mysql.connector import Error
import pandas as pd
import smtplib
from email.message import EmailMessage
import schedule
import time
from email.mime.text import MIMEText



# Dictionary to prevent duplicate scans within 1 minute
last_scan_times = {}

# Function to Save Data in MySQL Database
def save_data_to_sql(student_id, name, mobile, category, status):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='student_record',
            user='root',
            password='abhi@121511'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            # Ensure table exists
            cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(255),
                name VARCHAR(255),
                mobile VARCHAR(255),
                category VARCHAR(255),
                status VARCHAR(255),
                time VARCHAR(255),
                date VARCHAR(255)
            )''')
            current_time = datetime.now().strftime("%H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO students (student_id, name, mobile, category, status, time, date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (student_id, name, mobile, category, status, current_time, current_date)
            )
            conn.commit()
            print("✓ Data saved successfully:", student_id, name, mobile, category, status)
            # After saving data, automatically export it to Excel
            save_to_excel()
            # Return status for display function
            return status
    except Error as e:
        print(f"✘ MySQL error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def send_hostel_count_email():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='student_record',
            user='root',
            password='abhi@121511'
        )
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        # Total hostel students today
        cursor.execute("SELECT COUNT(*) FROM students WHERE category = 'Hostel' AND date = %s", (today,))
        total_hostel = cursor.fetchone()[0]

        # Hostel students IN
        cursor.execute("SELECT COUNT(*) FROM students WHERE category = 'Hostel' AND status = 'In' AND date = %s", (today,))
        hostel_in = cursor.fetchone()[0]

        # Hostel students OUT
        cursor.execute("SELECT COUNT(*) FROM students WHERE category = 'Hostel' AND status = 'Out' AND date = %s", (today,))
        hostel_out = cursor.fetchone()[0]

        # Email details
        sender_email = "XYZgmail.com"
        sender_password = "sdkv cbtd zfxp woud"
        receiver_email = "ABC@gmail.com"

        subject = "Hostel Student Status Report"
        body = (
            f"Hostel Student Report for {today}:\n\n"
            f"Total Hostel Entries: {total_hostel}\n"
            f"Currently In Hostel: {hostel_in}\n"
            f"Went Out Today: {hostel_out}"
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("✓ Hostel status email sent successfully.")
        messagebox.showinfo("Success", "Hostel status email sent successfully!")

    except mysql.connector.Error as e:
        print(f"✘ MySQL error: {e}")
    except Exception as ex:
        print(f"✘ Failed to send email: {ex}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Function to Determine "In" or "Out" Status
def determine_status(student_id):
    conn = mysql.connector.connect(
        host='localhost',
        database='student_record',
        user='root',
        password='abhi@121511'
    )
    cursor = conn.cursor()
    # Get the last recorded status
    cursor.execute("SELECT status FROM students WHERE student_id = %s ORDER BY id DESC LIMIT 1", (student_id,))
    last_entry = cursor.fetchone()
    conn.close()
    if last_entry:
        return "Out" if last_entry[0] == "In" else "In"
    return "In"  # First scan defaults to "In"

# Function to Scan QR Code with the Camera
def scan_qr_with_camera():
    global scanning
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open webcam.")
        return
    try:
        while scanning:
            ret, frame = cap.read()
            if not ret:
                break
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                data = obj.data.decode("utf-8").strip()
                try:
                    student_id, name, mobile, category = [x.strip() for x in data.split(",")]
                    # Prevent scanning the same QR within 1 minute
                    current_time = datetime.now()
                    if student_id in last_scan_times and current_time - last_scan_times[student_id] < timedelta(minutes=1):
                        continue
                    last_scan_times[student_id] = current_time
                    status = determine_status(student_id)
                    save_data_to_sql(student_id, name, mobile, category, status)
                    display_student_records()  # Display updated records after saving
                except ValueError:
                    print(f"Invalid QR Code format: {data}")
            cv2.imshow("QR Code Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# Function to Automatically Start the Camera
def start_camera_automatically():
    global scanning
    scanning = True
    scan_thread = threading.Thread(target=scan_qr_with_camera)
    scan_thread.daemon = True
    scan_thread.start()

# Function to Display Student Records
def display_student_records(search_query="", status_filter=None, category_filter=None):
    conn = mysql.connector.connect(
        host='localhost',
        database='student_record',
        user='root',
        password='abhi@121511'
    )
    cursor = conn.cursor()
    
    # Basic query
    query = "SELECT student_id, name, mobile, category, status, time, date FROM students WHERE date = %s"
    params = [datetime.now().strftime("%Y-%m-%d")]
    
    # If a search query is provided
    if search_query:
        query += " AND (student_id LIKE %s OR name LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # If status filter is applied
    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    # If category filter is applied (for bus or hostel)
    if category_filter:
        query += " AND category = %s"
        params.append(category_filter)
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()

    # Update the Treeview
    for item in records_tree.get_children():
        records_tree.delete(item)
    
    count = 0
    for row in records:
        records_tree.insert("", tk.END, values=row)
        count += 1
    
    # Update the total count label
    total_label.config(text=f"Total {status_filter if status_filter else 'Students'}: {count}")

def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to Save Data to Excel
def save_to_excel():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='student_record',
            user='root',
            password='abhi@121511'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            query = "SELECT student_id, name, mobile, category, status, time, date FROM students WHERE date = %s"
            params = [datetime.now().strftime("%Y-%m-%d")]
            cursor.execute(query, params)
            records = cursor.fetchall()
            # Create a DataFrame with the fetched records
            df = pd.DataFrame(records, columns=["Student ID", "Name", "Mobile", "Category", "Status", "Time", "Date"])
            # Create the filename with the current date
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f"student_records_{current_date}.xlsx"
            # Save to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"✓ Excel file created successfully: {filename}")
    except mysql.connector.Error as err:
        print(f"✘ MySQL error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Function to Search Records
def search_records():
    search_query = search_entry.get()
    status_filter = None
    category_filter = None
    
    # Status filter
    if in_var.get():
        status_filter = "In"
    elif out_var.get():
        status_filter = "Out"

    # Category filter (Bus and Hostel students)
    if bus_var.get():
        category_filter = "Bus"
    elif hostel_var.get():
        category_filter = "Hostel"

    display_student_records(search_query, status_filter, category_filter)
# Schedule the send_hostel_count_email function at 10:00 AM daily
# schedule.every().day.at("10:00").do(send_hostel_count_email)

# Start the scheduling in a background thread
email_thread = threading.Thread(target=schedule_thread)#target=schedule_thread
email_thread.daemon = True
email_thread.start()

root = tk.Tk()
root.title("Gate pass entry")
root.geometry("900x600")

search_frame = tk.Frame(root)
search_frame.pack(pady=5)

search_label = tk.Label(search_frame, text="Search:")
search_label.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="Search", command=search_records)
search_button.pack(side=tk.LEFT, padx=5)

filter_frame_1 = tk.Frame(root)
filter_frame_1.pack(pady=5)
filter_frame_2 = tk.Frame(root)
filter_frame_2.pack(pady=5)

in_var = tk.BooleanVar()
out_var = tk.BooleanVar()
bus_var = tk.BooleanVar()
hostel_var = tk.BooleanVar()

in_checkbox = tk.Checkbutton(filter_frame_1, text="In Students", variable=in_var, command=search_records)
in_checkbox.pack(side=tk.LEFT, padx=5)
out_checkbox = tk.Checkbutton(filter_frame_1, text="Out Students", variable=out_var, command=search_records)
out_checkbox.pack(side=tk.LEFT, padx=5)

bus_checkbox = tk.Checkbutton(filter_frame_2, text="Bus Student", variable=bus_var, command=search_records)
bus_checkbox.pack(side=tk.LEFT, padx=5)
hostel_checkbox = tk.Checkbutton(filter_frame_2, text="Hostel Student", variable=hostel_var, command=search_records)
hostel_checkbox.pack(side=tk.LEFT, padx=5)

total_label = tk.Label(root, text="Total Students: 0")
total_label.pack(pady=5)

# Display Records Button
records_button = tk.Button(root, text="Display Student Records", command=display_student_records)
records_button.pack(pady=10)
# email_button = tk.Button(root, text="Send Hostel Count via Email", command=send_hostel_count_email)
# email_button.pack(pady=5)
# email_button.config(bg="gray", fg="white")
columns = ("ID", "Name", "Mobile", "Category", "Status", "Time", "Date")
records_tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    records_tree.heading(col, text=col)
    records_tree.column(col, width=100)
records_tree.pack(fill=tk.BOTH, expand=True)

# Start the webcam scanning as soon as the program starts
start_camera_automatically()

# search_label.config(bg="lightgray", fg="black")

search_button.config(bg="gray", fg="white")

# total_label.config(bg="lightgray", fg="black")
records_button.config(bg="gray", fg="white")
root.mainloop()
