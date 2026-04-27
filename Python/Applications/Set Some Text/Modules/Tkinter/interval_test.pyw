from tkinter import Tk, Label

#TO CHANGE A WIDGET'S "text" OPTION VALUE, IN INTERVALS,
#USE A FUNCTION THAT UPDATES THE "text" OPTION VALUE,
#USING THE ".configure()" METHOD, WITH THE "text" OPTION VALUE SET, 
#TO THE NEW "text" OPTION VALUE, THEN REPEATEDLY CALL THE FUNCTION,
#IN INTERVALS.
#NOTE: A PYTHON LOOP, WILL INTERFERE WITH THE "tkinter.Tk().mainloop()"
#LOOP, IF THE "threading" MODULE, IS NOT USED.
def change_text():
   CURRENT_TEXT = LABEL['text']
   if CURRENT_TEXT.endswith('...'):
       CURRENT_TEXT = 'Loading '
   else:
       CURRENT_TEXT += '.'
   LABEL.configure(text=CURRENT_TEXT)
   ROOT.after(1000, change_text)

ROOT = Tk()
ROOT.geometry('800x600')
LABEL = Label(ROOT, text='Loading ', font=('Times New Roman', 28, 'bold'), padx=10)
LABEL.pack()
LABEL.after(1000, change_text)
ROOT.mainloop()
