import subprocess
from tkinter import *

def open_subwindow(movie_title):
    subprocess.Popen(["python", "film.py", movie_title])

root = Tk()
root.title("ÉC MOZI")

musor = Label(root, font=("Helvetica", 20, "bold"), text="Mai műsoron:")
musor.grid(column=0, row=0, padx=20, pady=10, columnspan=2, sticky="w")

movies = [
    ("SHREK 1.", 15),
    ("KEIL OLCSA a mozifilm", 0),
    ("Csuti baki válogatás", 5),
    ("READY PLAYER ONE", 12)
]

for i, (title, seats) in enumerate(movies):
    frame = Frame(root, relief="solid", bd=2)
    frame.grid(column=0, row=i+1, padx=20, pady=5, sticky="ew")
    
    movie_label = Label(frame, font=("Helvetica", 20, "bold"), text=title, fg="blue", cursor="hand2")
    movie_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
    movie_label.bind("<Button-1>", lambda e, t=title: open_subwindow(t))

    seat_label = Label(frame, font=("Helvetica", 18), text=f"{seats} szabad hely")
    seat_label.grid(column=1, row=0, padx=10, pady=10, sticky="e")

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)

root.mainloop()
