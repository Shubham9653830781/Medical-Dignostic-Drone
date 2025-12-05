import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
import subprocess

pulse = 0
temp = 0

def tkoff_check():
    if (pulse == 1 and temp == 1):
        tkoff()

def rec_pulse():
    global pulse
    pulse = 1
    with open("pulse_val.txt", "w") as file:
        file.write("Pulse Recorded")
    tkoff_check()
    return pulse


def rec_temp():
    global temp
    temp = 1
    with open("temp_val.txt", "w") as file:
        file.write("Temperature Recorded")
    tkoff_check()
    return temp


def open_pulse():
    pulse_window = tk.Toplevel(root)
    pulse_window.title("MedResQ")
    pulse_window.geometry("2560x1600")
    pulse_window.configure(bg="#22333B")

    home_btn = tk.Button(pulse_window, text="Back", font=("Times New Roman", 40),fg='#22333b', width=7,height=1, command= pulse_window.destroy)
    home_btn.pack(side='top', padx=50,pady=10)
    tk.Label(pulse_window, text="Pulse Oximeter", font=("Canvas Sans MS", 100, "bold"), bg="#22333B", fg='red').pack(side='top')
    tk.Label(pulse_window, text="Place your Index Finger on the \n RED Light", font=("Canvas Sans MS", 50, "bold"), bg="#22333B", fg="#f2f4f3").pack(anchor='center',padx=100, pady=50)
    tk.Label(pulse_window, text="⇦", font=("Canvas Sans MS", 400, "bold"), bg="#22333B", fg="#f2f4f3").pack(side='left')
    tk.Button(pulse_window, text="Pulse Rate:", font=("Canvas Sans MS", 50, "bold"), bg="#f2f4f3", fg="#22333B").pack(side='left',padx=100,pady=50)
    tk.Button(pulse_window, text="Record Value", font=("Canvas Sans MS", 50, "bold"), bg="#22333B", fg="#f2f4f3", command=rec_pulse).pack(side='left',padx=100,pady=50)

def open_temp():
    temp_window = tk.Toplevel(root)
    temp_window.title("MedResQ")
    temp_window.geometry("2560x1600")
    temp_window.configure(bg="#22333B")

    home_btn = tk.Button(temp_window, text="Back", font=("Times New Roman", 40),fg='#22333b', width=7,height=1, command= temp_window.destroy)
    home_btn.pack(side='top', padx=50,pady=10)
    tk.Label(temp_window, text="Temperature", font=("Canvas Sans MS", 100, "bold"), bg="#22333B", fg='red').pack(side='top')
    tk.Label(temp_window, text="Hold your Palm at \n RED Point", font=("Canvas Sans MS", 50, "bold"), bg="#22333B", fg="#f2f4f3").pack(anchor='center',padx=100, pady=50)
    tk.Label(temp_window, text="⇨", font=("Canvas Sans MS", 400, "bold"), bg="#22333B", fg="#f2f4f3").pack(side='right')
    tk.Button(temp_window, text="Record Value", font=("Canvas Sans MS", 50, "bold"), bg="#22333B", fg="#f2f4f3", command=rec_temp).pack(side='right',padx=80,pady=50)
    tk.Button(temp_window, text="Temperature:", font=("Canvas Sans MS", 50, "bold"), bg="#f2f4f3", fg="#22333B").pack(side='right',padx=80,pady=50)


def tkoff():
    countdown_window = tk.Toplevel(root)
    countdown_window.title("MedResQ")
    countdown_window.geometry("2560x1600")
    countdown_window.configure(bg="#22333B")

    tk.Label(countdown_window, text="Take-Off", font=("Canvas Sans MS", 100, "bold"),
             bg="#22333B", fg='red').pack(side='top', pady=20)
    tk.Label(countdown_window, text="Get Away from the drone Immediately!!!",
             font=("Canvas Sans MS", 50, "bold"), bg="#22333B", fg="#f2f4f3").pack(pady=30)
    tk.Label(countdown_window, text="Take-Off In:",
             font=("Canvas Sans MS", 200, "bold"), bg="#22333B", fg="#f2f4f3").pack()

    # Countdown label
    countdown_label = tk.Label(countdown_window, text="10",
                               font=("Canvas Sans MS", 300, "bold"), bg="#22333B", fg="#f2f4f3")
    countdown_label.pack()

    def update_count(n):
        if n >= 0:
            countdown_label.config(text=str(n))
            countdown_window.after(1000, update_count, n - 1)
        else:
            print("Takeoff Initiated")
            countdown_window.destroy()
            root.destroy()
            subprocess.run(["python3", "rtl.py"])

    update_count(10)
    



    
    

# Main window
root = tk.Tk()
root.title("Home")
root.geometry("2560x1600")
root.configure(bg="#22333B")  # Light gray background

exit_btn = tk.Button(root, text="Exit", font=("Arial", 14), width=15, command=root.destroy, bg="red", fg="white")
exit_btn.pack(anchor='c', padx=20, pady=20)

# Title
title_label = tk.Label(root, text="MedResQ", font=("Canvas Sans MS", 100, "bold"), bg="#22333B", fg="#f2f4f3")
title_label.pack(anchor='c',padx=20)

pulse_btn = tk.Button(root, text="Pulse & SpO2", font=("Times New Roman", 60),fg='#22333b', width=17,height=5, command=open_pulse)
pulse_btn.pack(side='left', padx=100)

temp_btn = tk.Button(root, text="Temperature", font=("Times New Roman", 60),fg='#22333b', width=17,height=5, command=open_temp)
temp_btn.pack(side='right', padx=100)


# Run the application
root.mainloop()
