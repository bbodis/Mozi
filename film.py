import sys
from tkinter import *

movie_title = sys.argv[1] if len(sys.argv) > 1 else "Ismeretlen film"

root = Tk()
root.title(movie_title)

Label(root, text=f"Jegyfoglalás: {movie_title}", font=("Helvetica", 20, "bold")).pack(pady=20)
Button(root, text="Bezár", command=root.destroy).pack(pady=10)

root.mainloop()
