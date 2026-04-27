from tkinter import Tk, StringVar, Entry, Checkbutton, Label

#TO TOGGLE PASSWORD VISIBILITY,
#USE THIS FUNCTION:
def toggle_input_visibility():
    if PASSWORD_INPUT.cget("show") == '*':
        PASSWORD_INPUT.config(show='')
    else:
        PASSWORD_INPUT.config(show='*')

ROOT = Tk()
ROOT.title('Test Application')
ROOT.geometry('300x160')

#TO SET AN INPUT, IN THE WINDOW, FIRST SET A VARIABLE TYPE,
#SUCH AS "StringVar()", THEN SET AN "Entry()" WIDGET, 
#WITH THE "textvariable" OPTION SET,
#TO UPDATE THE VARIABLE TYPE.
USERNAME_VARIABLE = StringVar(value='')
USERNAME_INPUT = Entry(ROOT, textvariable=USERNAME_VARIABLE, width=30)
USERNAME_INPUT.pack()
USERNAME_INPUT.focus()
PASSWORD_VARIABLE = StringVar(value='')

#TO HIDE PASSWORD VISIBILITY, USE THE "show" OPTION.
PASSWORD_INPUT = Entry(ROOT, textvariable=PASSWORD_VARIABLE, width=30, show='*')

PASSWORD_INPUT.pack()
Checkbutton(ROOT, text="Show Password", command=toggle_input_visibility).pack(pady=5)
LABEL = Label(ROOT, textvariable=USERNAME_VARIABLE)
LABEL.pack()
LABEL = Label(ROOT, textvariable=PASSWORD_VARIABLE)
LABEL.pack()
ROOT.mainloop()
