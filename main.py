from tkinter import *

root = Tk()
root.title("ÉC MOZI")

# Main title
musor = Label(root, font=("Helvetica", 20, "bold"), text="Mai műsoron:")
musor.grid(column=0, row=0, padx=20, pady=10, columnspan=2, sticky="w")

# Configure grid layout
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)

# Movie list
movies = [
    ("SHREK 1.", 15),
    ("KEIL OLCSA a mozifilm", 0),
    ("Csuti baki válogatás", 5),
    ("READY PLAYER ONE", 12)
]

# Create movie display
for i, (title, seats) in enumerate(movies):
    frame = Frame(root, relief="solid", bd=2)
    frame.grid(column=0, row=i+1, padx=20, pady=5, sticky="ew")
    
    # Movie title
    movie_label = Label(frame, font=("Helvetica", 20, "bold"), text=title, anchor="w", justify=LEFT)
    movie_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
    
    # Seats available
    seat_label = Label(frame, font=("Helvetica", 18), text=f"{seats} szabad hely", anchor="e", justify=RIGHT)
    seat_label.grid(column=1, row=0, padx=10, pady=10, sticky="e")
    
    frame.grid_columnconfigure(0, weight=1)  # Expand title
    frame.grid_columnconfigure(1, weight=0)  # Keep seat count aligned

root.mainloop()
