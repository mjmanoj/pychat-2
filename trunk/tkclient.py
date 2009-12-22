from Tkinter import *
import client, thread, time, ScrolledText

class App:
    def __init__(self, master):

        root.resizable(width=FALSE, height=FALSE)

        frame = Frame(master, bg= "#1C5FBA")
        frame.pack()

        self.box = ScrolledText.ScrolledText(frame, wrap=WORD, width = 80, relief = GROOVE)
        self.box.insert(END, 'Welcome to PyChat 2!')
        self.box.config(state=DISABLED)
        self.box.pack(side=TOP)

        entryframe = Frame(master = frame)
        entryframe.pack()

        self.texvar = StringVar()
        self.texvar.set("")
        self.label = Label(entryframe, textvariable=self.texvar, bg= "#1C5FBA", fg = "#F1E300")
        self.label.pack(side=LEFT)

        self.entry = Entry(entryframe, width = 60)
        self.entry.bind("<Return>", self.gettext)
        self.entry.pack(side=LEFT)

        self.quitter = Button(frame, relief = RIDGE, text = "Quit", fg = "#F1E300", bg = "#1C5FBA", command = self.quitbutton, state = DISABLED)
        self.quitter.pack(side=RIGHT)

        entryframe.pack(side=LEFT)

        self.buffer = ''
        self.bufferfull = False

        thread.start_new_thread(client.callbacks, (self.printtex, self.blockinput, self.close))

    def printtex(self, text):
        self.box.config(state=NORMAL)
        self.box.insert(END,"\n"+text)
        self.box.config(state=DISABLED)
        self.box.yview_scroll(1,"units")

    def quitbutton(self):
        self.buffer = "/exit"
        self.bufferfull = True
        
        
    def gettext(self, e):
        text = self.entry.get()
        self.entry.delete(0, END)
        self.buffer = text
        self.bufferfull = True

    def blockinput(self, prompt=''):
        if prompt != '':
            self.texvar.set(prompt)
        else:
            self.texvar.set("Say:")
            self.quitter.config(state = NORMAL, relief = RAISED)
        while 1:
            if self.bufferfull:
                self.bufferfull = False
                text = self.buffer
                self.buffer = ''
                return text
            else:
                time.sleep(0.01)
    
    def close(self):
        root.quit()
root = Tk()

app = App(root)

root.mainloop()
