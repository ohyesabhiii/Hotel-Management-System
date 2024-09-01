import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
import mysql.connector as sql
import random
import datetime
import pandas as pd

# connecting to sql
def connect_db(database=None):
    return sql.connect(
        host='localhost',
        user='root',
        password='1234',
        database=database
    )

# creating a database
def create_db():
    try:
        with connect_db() as con:
            with con.cursor() as cursor:
                cursor.execute('CREATE DATABASE IF NOT EXISTS d2')
                messagebox.showinfo("Success", "Database Created")
    except sql.Error as error:
        messagebox.showerror("Error", f"Error creating database: {error}")

# creating a table
def create_table():
    try:
        with connect_db('d2') as con:
            with con.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS customer (
                                  roomno INT(10),
                                  name VARCHAR(20),
                                  gender VARCHAR(30),
                                  room VARCHAR(40),
                                  date DATE,
                                  days INT(10),
                                  cost INT(11),
                                  total BIGINT
                                  )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS customer_checkout (
                                  roomno INT(10),
                                  name VARCHAR(20),
                                  gender VARCHAR(30),
                                  room VARCHAR(40),
                                  date DATE,
                                  days INT(10),
                                  cost INT(11),
                                  total BIGINT,
                                  checkout_date DATE
                                  )''')
                messagebox.showinfo("Success", "Tables Created")
    except sql.Error as error:
        messagebox.showerror("Error", f"Error creating table: {error}")

# inserting data
def insert_data():
    def insert():
        try:
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    choice = room_choice.get()
                    if choice not in {'1', '2', '3'}:
                        messagebox.showerror("Error", "Invalid choice")
                        insert_window.destroy()
                        return

                    room_choices = {
                        '1': ('classic', 2000, 1, 100),
                        '2': ('executive', 4000, 201, 270),
                        '3': ('presidential', 6000, 301, 330)
                    }

                    room, cost, start_range, end_range = room_choices[choice]
                    name = entry_name.get()
                    gender = entry_gender.get()
                    date = datetime.date.today()
                    days = int(entry_days.get())
                    amount = cost * days

                    cursor.execute('SELECT roomno FROM customer WHERE roomno BETWEEN %s AND %s ORDER BY roomno',
                                   (start_range, end_range))
                    occupied_rooms = [row[0] for row in cursor.fetchall()]

                    room_no = start_range
                    for occupied_room in occupied_rooms:
                        if room_no == occupied_room:
                            room_no += 1
                        else:
                            break

                    if room_no > end_range:
                        messagebox.showinfo("No Rooms", "No available rooms in the selected category")
                        insert_window.destroy()
                        return

                    cursor.execute('''INSERT INTO customer (roomno, name, gender, room, date, days, cost, total)
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                                   (room_no, name, gender, room, date, days, cost, amount))
                    con.commit()
                    messagebox.showinfo("Success", f"Data Inserted: Room No: {room_no}")
                    insert_window.destroy()

        except sql.Error as error:
            messagebox.showerror("Error", f"Error inserting data: {error}")
            insert_window.destroy()
    insert_window = tk.Toplevel()
    insert_window.title("Insert Data")

    tk.Label(insert_window, text="Enter Name:").grid(row=0, column=0)
    entry_name = tk.Entry(insert_window)
    entry_name.grid(row=0, column=1)

    tk.Label(insert_window, text="Enter Gender (F/M):").grid(row=1, column=0)
    entry_gender = tk.Entry(insert_window)
    entry_gender.grid(row=1, column=1)

    tk.Label(insert_window, text="Enter Days:").grid(row=2, column=0)
    entry_days = tk.Entry(insert_window)
    entry_days.grid(row=2, column=1)

    tk.Label(insert_window, text="Choose Room:").grid(row=3, column=0)
    room_choice = tk.StringVar(value="")
    tk.Radiobutton(insert_window, text="Classic (Rs. 2000)", variable=room_choice, value='1').grid(row=3, column=1)
    tk.Radiobutton(insert_window, text="Executive (Rs. 4000)", variable=room_choice, value='2').grid(row=4, column=1)
    tk.Radiobutton(insert_window, text="Presidential (Rs. 6000)", variable=room_choice, value='3').grid(row=5, column=1)

    tk.Button(insert_window, text="Insert", command=insert).grid(row=6, column=1)
    
# Reading data
def read_data():
    def fetch_data():
        try:
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('SELECT * FROM customer')
                    records = cursor.fetchall()
                    for record in records:
                        record_display.insert(tk.END, f"Room No.: {record[0]}, Name: {record[1]}, Gender: {record[2]}, "
                                                      f"Room: {record[3]}, Date: {record[4]}, Days: {record[5]}, "
                                                      f"Cost: {record[6]}, Amount: {record[7]}\n")
                        
        except sql.Error as error:
            messagebox.showerror("Error", f"Error reading data: {error}")
            read_window.destroy()
    read_window = tk.Toplevel()
    read_window.title("Read Data")

    record_display = tk.Text(read_window, width=100, height=20)
    record_display.pack()
    fetch_button = tk.Button(read_window, text="Fetch Data", command=fetch_data)
    fetch_button.pack()


# Searching data
def search_room():
    def search():
        try:
            room_no = int(entry_room_no.get())
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('SELECT * FROM customer WHERE roomno = %s', (room_no,))
                    record = cursor.fetchone()
                    if record:
                        search_display.insert(tk.END, f"Room No.: {record[0]}, Name: {record[1]}, Gender: {record[2]}, "
                                                      f"Room: {record[3]}, Date: {record[4]}, Days: {record[5]}, "
                                                      f"Cost: {record[6]}, Amount: {record[7]}\n")
                        
                    else:
                        messagebox.showinfo("Not Found", "Room not found")
                        
        except sql.Error as error:
            messagebox.showerror("Error", f"Error searching for room: {error}")
            search_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid room number.")
            search_window.destroy()
    search_window = tk.Toplevel()
    search_window.title("Search Room")

    tk.Label(search_window, text="Enter Room No:").grid(row=0, column=0)
    entry_room_no = tk.Entry(search_window)
    entry_room_no.grid(row=0, column=1)

    search_display = tk.Text(search_window, width=80, height=10)
    search_display.grid(row=1, column=0, columnspan=2)

    tk.Button(search_window, text="Search", command=search).grid(row=2, column=1)

# update data
def update_entry():
    def update():
        try:
            room_no = int(entry_room_no.get())
            choice = update_choice.get()

            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    if choice == '1':
                        new_days = int(entry_new_value.get())
                        cursor.execute('UPDATE customer SET days = %s WHERE roomno = %s', (new_days, room_no))
                        cursor.execute('SELECT cost FROM customer WHERE roomno = %s', (room_no,))
                        cost = cursor.fetchone()[0]
                        new_total = new_days * cost
                        cursor.execute('UPDATE customer SET total = %s WHERE roomno = %s', (new_total, room_no))
                        update_window.destroy()
                    elif choice == '2':
                        new_name = entry_new_value.get()
                        cursor.execute('UPDATE customer SET name = %s WHERE roomno = %s', (new_name, room_no))
                        update_window.destroy()
                    elif choice == '3':
                        room_choices = {
                            '1': ('classic', 2000),
                            '2': ('executive', 4000),
                            '3': ('presidential', 6000)
                        }
                        room_choice = entry_new_value.get()
                        if room_choice not in room_choices:
                            messagebox.showerror("Error", "Invalid room choice")
                            return
                        room, cost = room_choices[room_choice]
                        cursor.execute('UPDATE customer SET room = %s, cost = %s WHERE roomno = %s', (room, cost, room_no))
                        cursor.execute('SELECT days FROM customer WHERE roomno = %s', (room_no,))
                        days = cursor.fetchone()[0]
                        new_total = days * cost
                        cursor.execute('UPDATE customer SET total = %s WHERE roomno = %s', (new_total, room_no))
                        update_window.destroy()
                    con.commit()
                    messagebox.showinfo("Success", "Data Updated")

        except sql.Error as error:
            messagebox.showerror("Error", f"Error updating entry: {error}")
            update_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid room number.")
            update_window.destroy()
    update_window = tk.Toplevel()
    update_window.title("Update Data")

    tk.Label(update_window, text="Enter Room No:").grid(row=0, column=0)
    entry_room_no = tk.Entry(update_window)
    entry_room_no.grid(row=0, column=1)

    tk.Label(update_window, text="Choose what to update:").grid(row=1, column=0)
    update_choice = tk.StringVar()
    tk.Radiobutton(update_window, text="Days", variable=update_choice, value='1').grid(row=1, column=1)
    tk.Radiobutton(update_window, text="Name", variable=update_choice, value='2').grid(row=2, column=1)
    tk.Radiobutton(update_window, text="Room Type(1: Classic, 2: Executive, 3: Presidential)", variable=update_choice, value='3').grid(row=3, column=1)

    tk.Label(update_window, text="Enter new value:").grid(row=4, column=0)
    entry_new_value = tk.Entry(update_window)
    entry_new_value.grid(row=4, column=1)

    tk.Button(update_window, text="Update", command=update).grid(row=5, column=1)

# deleting an entry
def delete_entry():
    def delete():
        try:
            room_no = int(entry_room_no.get())
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('DELETE FROM customer WHERE roomno = %s', (room_no,))
                    con.commit()
                    if cursor.rowcount == 0:
                        messagebox.showinfo("Not Found", "Room not found")
                        delete_window.destroy()
                        
                    else:
                        messagebox.showinfo("Success", f"Room No. {room_no} deleted")
                        delete_window.destroy()

        except sql.Error as error:
            messagebox.showerror("Error", f"Error deleting entry: {error}")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid room number.")

    delete_window = tk.Toplevel()
    delete_window.title("Delete Record")

    tk.Label(delete_window, text="Enter Room No:").grid(row=0, column=0)
    entry_room_no = tk.Entry(delete_window)
    entry_room_no.grid(row=0, column=1)

    tk.Button(delete_window, text="Delete", command=delete).grid(row=1, column=1)

# Deleteing a table
def delete_table():
    def confirm_delete():
        try:
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('DROP TABLE IF EXISTS customer')
                    cursor.execute('DROP TABLE IF EXISTS customer_checkout')
                    con.commit()
                    messagebox.showinfo("Success", "Tables deleted")

        except sql.Error as error:
            messagebox.showerror("Error", f"Error deleting tables: {error}")

    delete_table_window = tk.Toplevel()
    delete_table_window.title("Delete Table")

    tk.Label(delete_table_window, text="Are you sure you want to delete the table?").pack()
    tk.Button(delete_table_window, text="Yes", command=confirm_delete).pack()
    tk.Button(delete_table_window, text="No", command=delete_table_window.destroy).pack()

# deleteing a database
def delete_database():
    def confirm_delete_db():
        try:
            with connect_db() as con:
                with con.cursor() as cursor:
                    cursor.execute('DROP DATABASE IF EXISTS d2')
                    con.commit()
                    messagebox.showinfo("Success", "Database deleted")

        except sql.Error as error:
            messagebox.showerror("Error", f"Error deleting database: {error}")

    delete_db_window = tk.Toplevel()
    delete_db_window.title("Delete Database")

    tk.Label(delete_db_window, text="Are you sure you want to delete the database?").pack()
    tk.Button(delete_db_window, text="Yes", command=confirm_delete_db).pack()
    tk.Button(delete_db_window, text="No", command=delete_db_window.destroy).pack()

# reading checkout records
def show_checkout_records():
    def fetch_checked_out_data():
        try:
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('SELECT * FROM customer_checkout')
                    records = cursor.fetchall()
                    for record in records:
                        checkout_display.insert(tk.END, f"Room No.: {record[0]}, Name: {record[1]}, Gender: {record[2]}, "
                                                        f"Room: {record[3]}, Date: {record[4]}, Days: {record[5]}, "
                                                        f"Cost: {record[6]}, Amount: {record[7]}, "
                                                        f"Checkout Date: {record[8]}\n")

        except sql.Error as error:
            messagebox.showerror("Error", f"Error fetching checkout records: {error}")

    checkout_window = tk.Toplevel()
    checkout_window.title("Show Checkout Records")

    checkout_display = tk.Text(checkout_window, width=100, height=20)
    checkout_display.pack()

    fetch_button = tk.Button(checkout_window, text="Fetch Data", command=fetch_checked_out_data)
    fetch_button.pack()

# checkout
def checkout():
    def perform_checkout():
        room_no = int(room_no_entry.get())
        try:
            with connect_db('d2') as con:
                with con.cursor() as cursor:
                    cursor.execute('SELECT * FROM customer WHERE roomno = %s', (room_no,))
                    row = cursor.fetchone()
                    checkout_date = datetime.date.today()
                    if row:
                        cursor.execute('''INSERT INTO customer_checkout (roomno, name, gender, room, date, days, cost, total, checkout_date) 
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                       (*row, checkout_date))
                        cursor.execute('DELETE FROM customer WHERE roomno = %s', (room_no,))
                        con.commit()
                        messagebox.showinfo("Success", f"Room {room_no} has been checked out!")
                        checkout_window.destroy()
                    else:
                        messagebox.showerror("Error", "Room not found.")
                        checkout_window.destroy()
        except sql.Error as error:
            messagebox.showerror("Error", f"Error during checkout: {error}")
            checkout_window.destroy()
    checkout_window = tk.Toplevel(root)
    checkout_window.title("Checkout")

    tk.Label(checkout_window, text="Room Number:").grid(row=0, column=0, padx=10, pady=5)
    room_no_entry = tk.Entry(checkout_window)
    room_no_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(checkout_window, text="Checkout", command=perform_checkout).grid(row=1, column=0, columnspan=2, pady=10)

# creating excel sheet of current data
def current_excel():
    try:
        with connect_db('d2') as con:
            with con.cursor() as cursor:
                data = pd.read_sql("SELECT * FROM customer", connect_db('d2'))
                '''directory = os.path.dirname(output_file)
                if not os.path.exists(directory):
                    os.makedirs(directory)'''
                data.to_excel('D:/cs project/cs project/hotel_data(current).xlsx', index=False)
                messagebox.showinfo("Success", "Excel Created")
    
    except sql.Error as error:
        messagebox.showerror("Error", f"Error while creating excel sheet: {error}")

#creating excel sheet of checkout data
def checkout_excel():
    try:
        with connect_db('d2') as con:
            with con.cursor() as cursor:
                data = pd.read_sql("SELECT * FROM customer_checkout", connect_db('d2'))
                data.to_excel('D:/cs project/cs project/hotel_data(checked out).xlsx', index=False)
                messagebox.showinfo("Success", "Excel Created")
    
    except sql.Error as error:
        messagebox.showerror("Error", f"Error while creating excel sheet: {error}")

root = tk.Tk()
root.title("Hotel Management System")

root.state('zoomed')


root.configure(bg='#e6f7ff')  

title_frame = tk.Frame(root, bg='#80ced6')
title_frame.pack(fill='x', pady=10)

tk.Label(
    title_frame, 
    text="Hotel Management System", 
    font=("Arial", 28, "bold"), 
    bg='#80ced6', 
    fg='white'
).pack(pady=20)

button_frame = tk.Frame(root, bg='#e6f7ff')
button_frame.pack(pady=20)

button_style = {
    'font': ("Arial", 16),
    'bg': '#80ced6',
    'fg': 'white',
    'activebackground': '#4682B4',
    'activeforeground': 'white',
    'width': 30,
    'height': 2,
    'bd': 0,
    'highlightthickness': 0,
}

buttons = [
    ("Create Database", create_db),
    ("Create Table", create_table),
    ("Insert Data", insert_data),
    ("Read Data", read_data),
    ("Search Room", search_room),
    ("Update Data", update_entry),
    ("Checkout", checkout),
    ("Show Checkout Records", show_checkout_records),
    ("Delete Data", delete_entry),
    ("Delete Table", delete_table),
    ("Delete Database", delete_database),
    ("Excel Sheet of Current Data", current_excel),
    ("Excel Sheet of Checked Out Data", checkout_excel),
]


for i, (text, command) in enumerate(buttons):
    row = i // 3
    col = i % 3
    btn = tk.Button(button_frame, text=text, command=command, **button_style)
    btn.grid(row=row, column=col, padx=20, pady=10)

root.mainloop()