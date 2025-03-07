from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Éc mozi")


musor = Label(root, font=("Helvetica", 26), text="Mai műsoron: ")
musor.grid(column=0, row=0, padx=20, pady=20)  
frame = Frame(root, relief="solid", bd=2)
frame.grid(column=0, row=1, padx=20, pady=20)  

movie1 = Label(frame, font=("Helvetica", 26), text="Shrek 1. ")
movie1.grid(column=0, row=2, padx=10, pady=10) 
movie2 = Label(frame, font=("Helvetica", 26), text="Csuti baki válogatás ")
movie2.grid(column=0, row=3, padx=10, pady=10) 


root.mainloop()
