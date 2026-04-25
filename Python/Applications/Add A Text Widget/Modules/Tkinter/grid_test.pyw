from tkinter import Tk, Label
from time import sleep

ROOT = Tk()
ROOT.geometry('800x600')
ROOT.title('Test Application')

#TO ADD TEXT TO AN APPLICATION WINDOW, WITH THE ".grid()" GEOMETRY MANAGER,
#USE "tkinter.Tk().rowconfigure([INDEX NUMBER HERE], weight=[WEIGHT NUMBER HERE])"
#AND "tkinter.Tk().columnconfigure([INDEX NUMBER HERE], weight=[WEIGHT NUMBER HERE])",
#TO SET GRID CELLS, IN THE APPLICATION WINDOW, THEN USE
#"tkinter.Label(Tk(), text='[TEXT HERE]')" AND ADD ANY FONT OPTIONS, WITH 
#"font=('[FONT NAME HERE]', [FONT SIZE HERE], '[FONT STYLE HERE]')",
#THEN USE THE ".grid()" METHOD, TO SET THE TEXT IN THE WINDOW, WITH THE "row" AND "column"
#OPTIONS SET, TO DETERMINE WHICH GRID CELL THE TEXT IS SET IN.
#NOTE: THE "Tk().rowconfigure()" AND "Tk().columnconfigure()" METHODS'
#"weight" OPTIONS, DEFINE HOW EACH CELL FILLS THE WINDOW, WHEN EXPANDED.
#NOTE: THE ".grid()" METHOD'S, "sticky" OPTION, CAN BE USED TO POSITION THE TEXT,
#IN THE GRID CELL.
ROOT.columnconfigure(0, weight=1)
ROOT.columnconfigure(1, weight=1)
ROOT.columnconfigure(2, weight=1)
ROOT.rowconfigure(0, weight=1)
ROOT.rowconfigure(1, weight=1)
ROOT.rowconfigure(2, weight=1)

LABEL = Label(ROOT, text='Center', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0)

LABEL = Label(ROOT, text='n', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='n')

LABEL = Label(ROOT, text='ne', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='ne')

LABEL = Label(ROOT, text='e', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='e')

LABEL = Label(ROOT, text='se', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='se')

LABEL = Label(ROOT, text='s', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='s')

LABEL = Label(ROOT, text='sw', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='sw')

LABEL = Label(ROOT, text='w', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='w')

LABEL = Label(ROOT, text='nw', font=('Helvetica', 24, 'bold'))
LABEL.grid(row=0, column=0, sticky='nw')

ROOT.mainloop()