import sqlite3
import subprocess
from tkinter import *
from tkinter import messagebox
from datetime import datetime

def init_db():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
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
        ticket_type TEXT NOT NULL,
        reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
        UNIQUE(movie_id, seat_row, seat_col)
    )
''')
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

def get_available_seats(movie_title):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT total_seats FROM movies WHERE title = ?', (movie_title,))
    total_seats = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reservations WHERE movie_id = (SELECT movie_id FROM movies WHERE title = ?)', (movie_title,))
    reserved_seats = cursor.fetchone()[0]
    
    conn.close()
    return total_seats - reserved_seats

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

def make_reservation(movie_title, user_name, user_email, selected_seats):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)', (user_name, user_email))
        cursor.execute('SELECT user_id FROM users WHERE email = ?', (user_email,))
        user_id = cursor.fetchone()[0]
        cursor.execute('SELECT movie_id FROM movies WHERE title = ?', (movie_title,))
        movie_id = cursor.fetchone()[0]
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

def get_user_reservations(email):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.reservation_id, m.title, r.seat_row, r.seat_col, r.reservation_date 
        FROM reservations r
        JOIN movies m ON r.movie_id = m.movie_id
        JOIN users u ON r.user_id = u.user_id
        WHERE u.email = ?
        ORDER BY r.reservation_date DESC
    ''', (email,))
    
    reservations = cursor.fetchall()
    conn.close()
    return reservations

def delete_reservation(reservation_id):
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM reservations WHERE reservation_id = ?', (reservation_id,))
        conn.commit()
        return True
    except:
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

    rows, cols = 5, 11
    seats = {}
    selected_seats = set()

    def toggle_seat(button, seat_id):
        if seats[seat_id] and seat_id not in [f"{r},{c}" for r, c in reserved_seats]:
            button.config(text='🟧', bg="orange")
            seats[seat_id] = False
            selected_seats.add(seat_id)
        elif not seats[seat_id]: 
            button.config(text='🟩', bg="green")
            seats[seat_id] = True
            selected_seats.remove(seat_id)
        if selected_seats:
            booking_button.grid(row=rows+3, column=0, columnspan=11, pady=20)
        else:
            booking_button.grid_forget()

    for r in range(rows):
        for c in range(cols):
            if c == 5:
                label = Label(subwindow, text="", width=2, height=1, bg="#333333")
                label.grid(row=r+2, column=c, padx=2, pady=2)
                continue

            seat_id = f'{r},{c}'
            seats[seat_id] = True
            if (r, c) in reserved_seats:
                btn = Button(subwindow, text='🟥', width=2, height=1, bg="red", state=DISABLED)
                seats[seat_id] = False
            else:
                btn = Button(subwindow, text='🟩', width=2, height=1, bg="green", activebackground="orange", fg="white")
            
            btn.grid(row=r+2, column=c, padx=2, pady=2)
            if (r, c) not in reserved_seats:
                btn.config(command=lambda b=btn, seat=seat_id: toggle_seat(b, seat))
    booking_button = Button(subwindow, text="Foglalás", font=("Helvetica", 16), bg="blue", fg="white", 
                          command=lambda: open_booking_window(movie_title, selected_seats))
    booking_button.grid(row=rows+3, column=0, columnspan=11, pady=20)
    booking_button.grid_forget()

def open_booking_window(movie_title, selected_seats):
    booking_window = Toplevel(root)
    booking_window.title("Foglalás")
    booking_window.geometry("500x400")
    booking_window.config(bg="#333333")
    frame = Frame(booking_window, bg="#333333")
    frame.pack(pady=20)
    Label(frame, text="Foglalás", font=("Helvetica", 20, "bold"), fg="white", bg="#333333").grid(row=0, column=0, columnspan=2, pady=10)
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
    seats_label = Label(frame, text=f"Kiválasztott helyek: {', '.join(selected_seats)}", 
                       font=("Helvetica", 12), fg="white", bg="#333333")
    seats_label.grid(row=3, column=0, columnspan=2, pady=10)
    Label(frame, text="Jegytípus:", font=("Helvetica", 14), fg="white", bg="#333333").grid(row=4, column=0, pady=10, sticky="e")
    ticket_type_var = StringVar(value="teljes árú jegy")
    ticket_options = ["diák jegy", "teljes árú jegy", "gyerek jegy"]
    OptionMenu(frame, ticket_type_var, *ticket_options).grid(row=4, column=1, pady=10, sticky="w")
    confirm_button = Button(frame, text="Foglalás megerősítése", font=("Helvetica", 16), bg="green", fg="white", 
                           command=lambda: confirm_booking(movie_title, name_entry.get(), email_entry.get(), selected_seats, ticket_type_var.get(), booking_window))
    confirm_button.grid(row=5, column=0, columnspan=2, pady=20)
    confirm_button.grid_forget()
    def check_fields():
        if (name_entry.get() and email_entry.get() and 
            name_entry.get() != 'Add meg a neved' and 
            email_entry.get() != 'Add meg az email címed'):
            confirm_button.grid()
        else:
            confirm_button.grid_forget()

    name_entry.bind("<KeyRelease>", lambda event: check_fields())
    email_entry.bind("<KeyRelease>", lambda event: check_fields())

def confirm_booking(movie_title, name, email, selected_seats, ticket_type_var, window):
    if not name or not email or name == 'Add meg a neved' or email == 'Add meg az email címed':
        messagebox.showerror("Hiba", "Kérjük, töltsd ki mindkét mezőt!")
        return
    
    if make_reservation(movie_title, name, email, selected_seats):
        messagebox.showinfo("Siker", f"Foglalás sikeresen leadva!\nNév: {name}\nEmail: {email}\nFilm: {movie_title}\nHelyek: {', '.join(selected_seats)}")
        window.destroy()
        refresh_movie_list()
    else:
        messagebox.showerror("Hiba", "Valami hiba történt a foglalás során. Lehet, hogy valaki már lefoglalta a kiválasztott helyeket.")

def show_my_reservations():
    reservations_window = Toplevel(root)
    reservations_window.title("Foglalásaim")
    reservations_window.geometry("800x600")
    reservations_window.config(bg="#333333")
    
    header_frame = Frame(reservations_window, bg="#333333")
    header_frame.pack(fill=X, padx=20, pady=10)
    
    Label(header_frame, text="Foglalásaim", font=("Helvetica", 20, "bold"), fg="white", bg="#333333").pack(side=LEFT)
    
    email_frame = Frame(reservations_window, bg="#333333")
    email_frame.pack(fill=X, padx=20, pady=10)
    
    email_label = Label(email_frame, text="Email cím:", font=("Helvetica", 14), fg="white", bg="#333333")
    email_label.pack(side=LEFT)
    
    email_entry = Entry(email_frame, font=("Helvetica", 14), width=30, fg='white', bg="#555555")
    email_entry.insert(0, 'Add meg az email címed')
    email_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, email_entry, 'Add meg az email címed'))
    email_entry.pack(side=LEFT, padx=10)
    
    search_button = Button(email_frame, text="Keresés", font=("Helvetica", 12), bg="blue", fg="white",
                          command=lambda: display_reservations(email_entry.get(), reservations_window))
    search_button.pack(side=LEFT)

def display_reservations(email, window):
    if not email or email == 'Add meg az email címed':
        messagebox.showerror("Hiba", "Kérjük, add meg az email címed!")
        return
    
    reservations = get_user_reservations(email)
    
    # Clear previous results if any
    for widget in window.winfo_children():
        if isinstance(widget, Frame) and widget.winfo_name() != "!frame" and widget.winfo_name() != "!frame2":
            widget.destroy()
    
    if not reservations:
        no_res_label = Label(window, text="Nincsenek foglalásaid ezzel az email címmel.", 
                           font=("Helvetica", 14), fg="white", bg="#333333")
        no_res_label.pack(pady=20)
        return
    
    container = Frame(window, bg="#333333")
    container.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    canvas = Canvas(container, bg="#333333", highlightthickness=0)
    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="#333333")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    for i, (res_id, title, row, col, date) in enumerate(reservations):
        res_frame = Frame(scrollable_frame, bg="#555555", padx=10, pady=10)
        res_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
        
        Label(res_frame, text=f"Film: {title}", font=("Helvetica", 14), fg="white", bg="#555555").grid(row=0, column=0, sticky="w")
        Label(res_frame, text=f"Hely: {row}. sor, {col}. szék", font=("Helvetica", 12), fg="white", bg="#555555").grid(row=1, column=0, sticky="w")
        Label(res_frame, text=f"Dátum: {date}", font=("Helvetica", 12), fg="white", bg="#555555").grid(row=2, column=0, sticky="w")
        
        delete_btn = Button(res_frame, text="Törlés", font=("Helvetica", 12), bg="red", fg="white",
                          command=lambda rid=res_id: delete_and_refresh(rid, email, window))
        delete_btn.grid(row=0, column=1, rowspan=3, padx=10, sticky="ns")

def delete_and_refresh(reservation_id, email, window):
    if delete_reservation(reservation_id):
        messagebox.showinfo("Siker", "Foglalás sikeresen törölve!")
        display_reservations(email, window)
        refresh_movie_list()
    else:
        messagebox.showerror("Hiba", "A foglalás törlése sikertelen!")

def refresh_movie_list():
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

# Adatbázis inicializálása
init_db()

# Főablak létrehozása
root = Tk()
root.title("ÉC MOZI")
root.config(bg="#333333")

# Fejléc
header_frame = Frame(root, bg="#333333")
header_frame.grid(column=0, row=0, columnspan=3, sticky="ew", padx=20, pady=10)

musor = Label(header_frame, font=("Helvetica", 20, "bold"), text="Mai műsoron:", fg="white", bg="#333333")
musor.pack(side=LEFT)

my_reservations_btn = Button(header_frame, text="Foglalásaim", font=("Helvetica", 14), bg="blue", fg="white",
                           command=show_my_reservations)
my_reservations_btn.pack(side=RIGHT, padx=10)

# Filmek listája
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