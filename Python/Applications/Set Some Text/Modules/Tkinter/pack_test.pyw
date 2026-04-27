from tkinter import Tk, Label

ROOT = Tk()
ROOT.geometry('800x600')
ROOT.title('Test Application')

#TO ADD TEXT TO AN APPLICATION WINDOW, WITH THE ".pack()" GEOMETRY MANAGER,
#USE "tkinter.Label(tkinter.Tk(), text='[TEXT HERE]')" AND ADD ANY FONT OPTIONS WITH 
#"font=('[FONT NAME HERE]', [FONT SIZE HERE], '[FONT STYLE HERE]')",
#THEN USE THE ".pack()" METHOD, TO SET THE TEXT IN THE WINDOW. 
#NOTE: THE ".pack()" METHOD'S "anchor" OPTION, CAN BE USED TO POSITION THE TEXT,
#IN THE WINDOW, IN CASCADING ORDERED RELEVANCE, TO THE LAST WIDGET SET, IN THE WINDOW.
LABEL = Label(ROOT, text='Header', font=('Arial', 24, 'bold'))
LABEL.pack(anchor='n', padx=10, pady=10)
LABEL = Label(ROOT, text='Sub-title', font=('Arial', 18, 'bold'))
LABEL.pack(anchor='nw', padx=10, pady=10)
LABEL = Label(ROOT, text='Line 1', font=('Arial', 16))
LABEL.pack(anchor='nw', padx=10)
LABEL = Label(ROOT, text='Line 2', font=('Arial', 16))
LABEL.pack(anchor='nw', padx=10)
LABEL = Label(ROOT, text='Line 3', font=('Arial', 16))
LABEL.pack(anchor='nw', padx=10)
LABEL = Label(ROOT, text='Etc...', font=('Arial', 16))
LABEL.pack(anchor='nw', padx=10)
LABEL = Label(ROOT, text='Footer', font=('Arial', 24, 'bold'))
LABEL.pack(anchor='n', padx=10, pady=10)
ROOT.mainloop()
