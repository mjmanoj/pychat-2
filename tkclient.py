from Tkinter import *
import client, thread, time, ScrolledText

class App:
    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.box = ScrolledText.ScrolledText(frame, wrap=WORD, width = 80)
        self.box.insert(END, 'Welcome to PyChat 2!')
        self.box.config(state=DISABLED)
        self.box.pack(side=TOP)

        entryframe = Frame(master = frame)
        entryframe.pack()

        self.texvar = StringVar()
        self.texvar.set("")
        self.label = Label(entryframe, textvariable=self.texvar)
        self.label.pack(side=LEFT)

        self.entry = Entry(entryframe, width = 60)
        self.entry.bind("<Return>", self.gettext)
        self.entry.pack(side=LEFT)

        entryframe.pack(side=LEFT)

        self.buffer = ''
        self.bufferfull = False

        thread.start_new_thread(client.callbacks, (self.printtex, self.blockinput, self.close))

    def printtex(self, text):
        self.box.config(state=NORMAL)
        self.box.insert(END,"\n"+text)
        self.box.config(state=DISABLED)
        self.box.yview_scroll(1,"units")
        
    def gettext(self, e):
        text = self.entry.get()
        self.entry.delete(0, END)
        self.buffer = text
        self.bufferfull = True

    def blockinput(self, prompt=''):
        #TODO: set prompt to prompt variable
        if prompt != '':
            self.texvar.set(prompt)
        else:
            self.texvar.set("Say:")
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
