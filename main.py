import sqlite3
import subprocess
from tkinter import *
from tkinter import messagebox
from datetime import datetime

# Adatbázis inicializálása
def init_db():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    # Táblák létrehozása, ha nem léteznek
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            total_seats INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            seat_row INTEGER NOT NULL,
            seat_col INTEGER NOT NULL,
            reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
            UNIQUE(movie_id, seat_row, seat_col)
        )
    ''')
    
    # Alap filmek hozzáadása, ha még nincsenek
    movies = [
        ("SHREK 1.", 50),
        ("KEIL OLCSA a mozifilm", 50),
        ("Csuti baki válogatás", 50),
        ("READY PLAYER ONE", 50)
    ]
    
    for title, seats in movies:
        cursor.execute('INSERT OR IGNORE INTO movies (title, total_seats) VALUES (?, ?)', (title, seats))
    
    conn.commit()
    conn.close()

# Szabad helyek számának lekérdezése egy filmhez
def get_available_seats(movie_title):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT total_seats FROM movies WHERE title = ?', (movie_title,))
    total_seats = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reservations WHERE movie_id = (SELECT movie_id FROM movies WHERE title = ?)', (movie_title,))
    reserved_seats = cursor.fetchone()[0]
    
    conn.close()
    return total_seats - reserved_seats

# Foglalt helyek lekérdezése egy filmhez
def get_reserved_seats(movie_title):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT seat_row, seat_col FROM reservations 
        WHERE movie_id = (SELECT movie_id FROM movies WHERE title = ?)
    ''', (movie_title,))
    
    reserved_seats = cursor.fetchall()
    conn.close()
    return reserved_seats

# Új foglalás rögzítése
def make_reservation(movie_title, user_name, user_email, selected_seats):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    try:
        # Felhasználó hozzáadása vagy lekérdezése
        cursor.execute('INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)', (user_name, user_email))
        cursor.execute('SELECT user_id FROM users WHERE email = ?', (user_email,))
        user_id = cursor.fetchone()[0]
        
        # Film ID lekérdezése
        cursor.execute('SELECT movie_id FROM movies WHERE title = ?', (movie_title,))
        movie_id = cursor.fetchone()[0]
        
        # Foglalások rögzítése
        for seat in selected_seats:
            row, col = map(int, seat.split(','))
            cursor.execute('INSERT INTO reservations (user_id, movie_id, seat_row, seat_col) VALUES (?, ?, ?, ?)',
                          (user_id, movie_id, row, col))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

def open_subwindow(movie_title):
    available_seats = get_available_seats(movie_title)
    reserved_seats = get_reserved_seats(movie_title)
    
    subwindow = Toplevel(root)
    subwindow.title(f'{movie_title} - Ülésfoglalás')
    subwindow.config(bg="#333333")

    header = Label(subwindow, text=f'{movie_title}', font=("Helvetica", 20, "bold"), fg="white", bg="#333333")
    header.grid(row=0, column=0, columnspan=11, pady=10)

    info_label = Label(subwindow, text=f'Szabad helyek: {available_seats}', font=("Helvetica", 14), fg="white", bg="#333333")
    info_label.grid(row=1, column=0, columnspan=11, pady=(0, 10))

    rows, cols = 5, 11  # 5 sor, 11 oszlop (középen lépcső)
    seats = {}  # Minden ülés státusza (True = szabad, False = foglalt)
    selected_seats = set()  # Nyilvántartás arról, hogy mely helyek vannak kiválasztva

    def toggle_seat(button, seat_id):
        if seats[seat_id] and seat_id not in [f"{r},{c}" for r, c in reserved_seats]:  # Ha szabad hely és nem előre foglalt
            button.config(text='🟧', bg="orange")  # Narancssárga a kiválasztott hely
            seats[seat_id] = False
            selected_seats.add(seat_id)  # Hozzáadjuk a kiválasztott székekhez
        elif not seats[seat_id]:  # Ha foglalt hely (általunk), feloldás
            button.config(text='🟩', bg="green")
            seats[seat_id] = True
            selected_seats.remove(seat_id)  # Eltávolítjuk a kiválasztott székekből

        # Gomb megjelenítése/elrejtése
        if selected_seats:
            booking_button.grid(row=rows+3, column=0, columnspan=11, pady=20)
        else:
            booking_button.grid_forget()

    for r in range(rows):
        for c in range(cols):
            if c == 5:  # Középső oszlop lépcsőként hagyása
                label = Label(subwindow, text="", width=2, height=1, bg="#333333")
                label.grid(row=r+2, column=c, padx=2, pady=2)
                continue

            seat_id = f'{r},{c}'
            seats[seat_id] = True  # Kezdetben minden hely szabad

            # Ellenőrizzük, hogy a hely már foglalt-e az adatbázisban
            if (r, c) in reserved_seats:
                btn = Button(subwindow, text='🟥', width=2, height=1, bg="red", state=DISABLED)
                seats[seat_id] = False
            else:
                btn = Button(subwindow, text='🟩', width=2, height=1, bg="green", activebackground="orange", fg="white")
            
            btn.grid(row=r+2, column=c, padx=2, pady=2)
            if (r, c) not in reserved_seats:  # Csak a szabad helyekre engedjük a kattintást
                btn.config(command=lambda b=btn, seat=seat_id: toggle_seat(b, seat))

    # Foglalás gomb
    booking_button = Button(subwindow, text="Foglalás", font=("Helvetica", 16), bg="blue", fg="white", 
                          command=lambda: open_booking_window(movie_title, selected_seats))
    booking_button.grid(row=rows+3, column=0, columnspan=11, pady=20)
    booking_button.grid_forget()  # Elrejtjük alapból

def open_booking_window(movie_title, selected_seats):
    booking_window = Toplevel(root)
    booking_window.title("Foglalás")
    booking_window.geometry("500x400")
    booking_window.config(bg="#333333")

    frame = Frame(booking_window, bg="#333333")
    frame.pack(pady=20)

    Label(frame, text="Foglalás", font=("Helvetica", 20, "bold"), fg="white", bg="#333333").grid(row=0, column=0, columnspan=2, pady=10)

    # Név mező
    name_entry = Entry(frame, font=("Helvetica", 14), width=30, fg='white', bg="#555555")
    name_entry.insert(0, 'Add meg a neved')
    name_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, name_entry, 'Add meg a neved'))
    name_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, name_entry, 'Add meg a neved'))
    name_entry.grid(row=1, column=0, columnspan=2, pady=10)

    # Email mező
    email_entry = Entry(frame, font=("Helvetica", 14), width=30, fg='white', bg="#555555")
    email_entry.insert(0, 'Add meg az email címed')
    email_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.grid(row=2, column=0, columnspan=2, pady=10)

    # Foglalt helyek megjelenítése
    seats_label = Label(frame, text=f"Kiválasztott helyek: {', '.join(selected_seats)}", 
                       font=("Helvetica", 12), fg="white", bg="#333333")
    seats_label.grid(row=3, column=0, columnspan=2, pady=10)

    # Megerősítés gomb
    confirm_button = Button(frame, text="Foglalás megerősítése", font=("Helvetica", 16), bg="green", fg="white", 
                           command=lambda: confirm_booking(movie_title, name_entry.get(), email_entry.get(), selected_seats, booking_window))
    confirm_button.grid(row=4, column=0, columnspan=2, pady=20)
    confirm_button.grid_forget()

    # Mezők ellenőrzése
    def check_fields():
        if (name_entry.get() and email_entry.get() and 
            name_entry.get() != 'Add meg a neved' and 
            email_entry.get() != 'Add meg az email címed'):
            confirm_button.grid()
        else:
            confirm_button.grid_forget()

    name_entry.bind("<KeyRelease>", lambda event: check_fields())
    email_entry.bind("<KeyRelease>", lambda event: check_fields())

def confirm_booking(movie_title, name, email, selected_seats, window):
    if not name or not email or name == 'Add meg a neved' or email == 'Add meg az email címed':
        messagebox.showerror("Hiba", "Kérjük, töltsd ki mindkét mezőt!")
        return
    
    if make_reservation(movie_title, name, email, selected_seats):
        messagebox.showinfo("Siker", f"Foglalás sikeresen leadva!\nNév: {name}\nEmail: {email}\nFilm: {movie_title}\nHelyek: {', '.join(selected_seats)}")
        window.destroy()
        refresh_movie_list()
    else:
        messagebox.showerror("Hiba", "Valami hiba történt a foglalás során. Lehet, hogy valaki már lefoglalta a kiválasztott helyeket.")

def refresh_movie_list():
    # Frissíti a főablakban a filmek listáját a szabad helyekkel
    for i, (title, _) in enumerate(movies):
        available_seats = get_available_seats(title)
        seat_labels[i].config(text=f"{available_seats} szabad hely")

def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.config(fg='white')

def restore_placeholder(event, entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg='grey')

def show_movie_description(movie_title):
    descriptions = {
        "SHREK 1.": "Egy zöld ogre, Shrek, békésen él a mocsárban, amíg gonosz törpe, Farquaad, nem száműzi oda a mesefigurákat. Shrek és egy beszélni képes szamár, a Szamár, elindulnak, hogy megmentsék Fiona hercegnőt, és visszaszerezzék Shrek otthonát.",
        "KEIL OLCSA a mozifilm": "Egy fiatal lány, Keil Olcsa, felfedezi, hogy különleges képességei vannak, amik segítenek neki megmenteni a várost egy titokzatos fenyegetéstől. Vígjáték és kaland együtt.",
        "Csuti baki válogatás": "A legvicsesebb és legkínosabb pillanatok gyűjteménye Csuti életéből. Ezeket a bakikat soha nem láthattad még!",
        "READY PLAYER ONE": "2045-ben a világ nagy része a virtuális valóságban, az OASIS-ban él. Wade Watts egy rejtélyes versenyben vesz részt, amely a világ sorsát döntheti el."
    }
    
    description = descriptions.get(movie_title, "Nincs leírás elérhető ehhez a filmhez.")
    
    desc_window = Toplevel(root)
    desc_window.title(f"{movie_title} - Leírás")
    desc_window.config(bg="#333333")
    
    Label(desc_window, text=movie_title, font=("Helvetica", 18, "bold"), fg="white", bg="#333333").pack(pady=10)
    
    text_frame = Frame(desc_window, bg="#333333")
    text_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    scrollbar = Scrollbar(text_frame)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    text_widget = Text(text_frame, wrap=WORD, yscrollcommand=scrollbar.set, 
                      font=("Helvetica", 12), fg="white", bg="#555555", 
                      padx=10, pady=10, width=50, height=10)
    text_widget.insert(END, description)
    text_widget.config(state=DISABLED)
    text_widget.pack(side=LEFT, fill=BOTH, expand=True)
    
    scrollbar.config(command=text_widget.yview)
    
    Button(desc_window, text="Bezárás", font=("Helvetica", 14), bg="red", fg="white", 
           command=desc_window.destroy).pack(pady=10)

# Főprogram
init_db()

root = Tk()
root.title("ÉC MOZI")
root.config(bg="#333333")

musor = Label(root, font=("Helvetica", 20, "bold"), text="Mai műsoron:", fg="white", bg="#333333")
musor.grid(column=0, row=0, padx=20, pady=10, columnspan=3, sticky="w")

# Filmek listája (csak a címek, a helyek száma az adatbázisból jön)
movie_titles = ["SHREK 1.", "KEIL OLCSA a mozifilm", "Csuti baki válogatás", "READY PLAYER ONE"]
movies = [(title, get_available_seats(title)) for title in movie_titles]
seat_labels = []

for i, (title, seats) in enumerate(movies):
    frame = Frame(root, relief="solid", bd=2, bg="#333333")
    frame.grid(column=0, row=i+1, padx=20, pady=5, sticky="ew", columnspan=3)

    movie_label = Label(frame, font=("Helvetica", 20, "bold"), text=title, fg="blue", cursor="hand2", bg="#333333")
    movie_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
    movie_label.bind("<Button-1>", lambda e, t=title: open_subwindow(t))

    desc_link = Label(frame, font=("Helvetica", 12), text="[Leírás]", fg="cyan", cursor="hand2", bg="#333333")
    desc_link.grid(column=1, row=0, padx=(20, 10), pady=10, sticky="w")
    desc_link.bind("<Button-1>", lambda e, t=title: show_movie_description(t))

    seat_label = Label(frame, font=("Helvetica", 18), text=f"{seats} szabad hely", fg="white", bg="#333333")
    seat_label.grid(column=2, row=0, padx=10, pady=10, sticky="e")
    seat_labels.append(seat_label)

    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    frame.grid_columnconfigure(2, weight=0)

root.mainloop()