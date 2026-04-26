from tkinter import Tk, Label, Button

#TO DYNAMICALLY CHANGE THE "text" OPTION VALUE, OF A WIDGET, 
#USE A FUNCTION THAT UPDATES THE "text" OPTION VALUE,
#USING THE ".configure()" METHOD, WITH THE "text" OPTION VALUE SET, 
#TO THE NEW "text" OPTION VALUE.
def dynamically_change_text():
    if LABEL['text'] == 'Click, the button':
        return LABEL.configure(text='The button, was clicked')
    elif LABEL['text'] == 'The button, was clicked':
        return LABEL.configure(text='The button, was clicked again')
    else:
        return LABEL.configure(text='Click, the button')
    
ROOT = Tk()
ROOT.geometry('800x600')
LABEL = Label(ROOT, text='Click, the button', font=('Canada 150', 28, 'bold'), padx=10)
LABEL.pack()
BUTTON = Button(ROOT, text="Click, here", font=('Canada 150', 16, 'bold'), padx=10, command=dynamically_change_text)
BUTTON.pack()
ROOT.mainloop()