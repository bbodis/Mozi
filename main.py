import subprocess
from tkinter import *
from tkinter import messagebox


def open_subwindow(movie_title, available_seats):
    subwindow = Toplevel(root)
    subwindow.title(f'{movie_title} - Ülésfoglalás')

    # Beállítjuk a szürke hátteret
    subwindow.config(bg="#333333")

    header = Label(subwindow, text=f'{movie_title}', font=("Helvetica", 20, "bold"), fg="white", bg="#333333")
    header.grid(row=0, column=0, columnspan=11, pady=10)

    info_label = Label(subwindow, text=f'Szabad helyek: {available_seats}', font=("Helvetica", 14), fg="white", bg="#333333")
    info_label.grid(row=1, column=0, columnspan=11, pady=(0, 10))

    rows, cols = 5, 11  # 5 sor, 11 oszlop (középen lépcső)
    seats = {}  # Minden ülés státusza (True = szabad, False = foglalt)
    selected_seats = set()  # Nyilvántartás arról, hogy mely helyek vannak kiválasztva

    def toggle_seat(button, seat_id):
        if seats[seat_id]:  # Ha szabad hely, foglalás
            button.config(text='🟧', bg="orange")  # Narancssárga a kiválasztott hely
            seats[seat_id] = False
            selected_seats.add(seat_id)  # Hozzáadjuk a kiválasztott székekhez
        else:  # Ha foglalt hely, feloldás
            button.config(text='🟩', bg="green")
            seats[seat_id] = True
            selected_seats.remove(seat_id)  # Eltávolítjuk a kiválasztott székekből

        # Ha van legalább egy kiválasztott szék, megjelenítjük a foglalás gombot
        if selected_seats:
            booking_button.grid(row=rows+3, column=0, columnspan=11, pady=20)
        else:
            booking_button.grid_forget()  # Ha nincs kiválasztott szék, elrejtjük a gombot

    rows, cols = 5, 11  # 5 sor, 11 oszlop (középen lépcső)
    for r in range(rows):
        for c in range(cols):
            if c == 5:  # Középső oszlop lépcsőként hagyása
                label = Label(subwindow, text="", width=2, height=1, bg="#333333")  # Üres hely
                label.grid(row=r+2, column=c, padx=2, pady=2)
                continue

            seat_id = f'{r},{c}'
            seats[seat_id] = True  # Kezdetben minden hely szabad

            btn = Button(subwindow, text='🟩', width=2, height=1, bg="green", activebackground="orange", fg="white")
            btn.grid(row=r+2, column=c, padx=2, pady=2)
            btn.config(command=lambda b=btn, seat=seat_id: toggle_seat(b, seat))

    # Alapból nem jelenik meg, amíg nem választottak helyet
    booking_button = Button(subwindow, text="Foglalás", font=("Helvetica", 16), bg="blue", fg="white", command=open_booking_window)
    booking_button.grid_forget()  # Elrejtjük alapból


def open_booking_window():
    booking_window = Toplevel(root)
    booking_window.title("Foglalás")
    booking_window.geometry("500x400")  # Szélesebb ablakméret

    # Beállítjuk a szürke hátteret
    booking_window.config(bg="#333333")

    frame = Frame(booking_window, bg="#333333")
    frame.pack(pady=20)

    Label(frame, text="Foglalás", font=("Helvetica", 20, "bold"), fg="white", bg="#333333").grid(row=0, column=0, columnspan=2, pady=10)

    # A szöveg színe fehér a beviteli mezőkben
    name_entry = Entry(frame, font=("Helvetica", 14), width=30, fg='white', bg="#555555")
    name_entry.insert(0, 'Add meg a neved')
    name_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, name_entry, 'Add meg a neved'))
    name_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, name_entry, 'Add meg a neved'))
    name_entry.grid(row=1, column=0, columnspan=2, pady=10)

    email_entry = Entry(frame, font=("Helvetica", 14), width=30, fg='white', bg="#555555")
    email_entry.insert(0, 'Add meg az email címed')
    email_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.grid(row=2, column=0, columnspan=2, pady=10)

    # Alapból a gomb el van rejtve
    confirm_button = Button(frame, text="Foglalás megerősítése", font=("Helvetica", 16), bg="green", fg="white", command=lambda: messagebox.showinfo("Siker", f"Foglalás sikeresen leadva!\nNév: {name_entry.get()}\nEmail: {email_entry.get()}"))
    confirm_button.grid(row=3, column=0, columnspan=2, pady=20)
    confirm_button.grid_forget()  # Elrejtjük alapból

    # A gomb akkor jelenjen meg, ha mindkét mező ki van töltve
    def check_fields():
        if name_entry.get() and email_entry.get() and name_entry.get() != 'Add meg a neved' and email_entry.get() != 'Add meg az email címed':
            confirm_button.grid()  # Ha ki van töltve, megjelenítjük
        else:
            confirm_button.grid_forget()  # Ha nincs kitöltve, elrejtjük

    # Az események, amik aktiválják a mezők figyelését
    name_entry.bind("<KeyRelease>", lambda event: check_fields())
    email_entry.bind("<KeyRelease>", lambda event: check_fields())


def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.config(fg='white')  # Szöveg színe fehérre állítása


def restore_placeholder(event, entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg='grey')  # Visszaállítjuk a helykitöltő szöveget szürkére


root = Tk()
root.title("ÉC MOZI")

# Beállítjuk a szürke hátteret
root.config(bg="#333333")

musor = Label(root, font=("Helvetica", 20, "bold"), text="Mai műsoron:", fg="white", bg="#333333")
musor.grid(column=0, row=0, padx=20, pady=10, columnspan=2, sticky="w")

movies = [
    ("SHREK 1.", 15),
    ("KEIL OLCSA a mozifilm", 0),
    ("Csuti baki válogatás", 5),
    ("READY PLAYER ONE", 12)
]

for i, (title, seats) in enumerate(movies):
    frame = Frame(root, relief="solid", bd=2, bg="#333333")
    frame.grid(column=0, row=i+1, padx=20, pady=5, sticky="ew")

    movie_label = Label(frame, font=("Helvetica", 20, "bold"), text=title, fg="blue", cursor="hand2", bg="#333333")
    movie_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
    movie_label.bind("<Button-1>", lambda e, t=title, s=seats: open_subwindow(t, s))

    seat_label = Label(frame, font=("Helvetica", 18), text=f"{seats} szabad hely", fg="white", bg="#333333")
    seat_label.grid(column=1, row=0, padx=10, pady=10, sticky="e")

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)

root.mainloop()
