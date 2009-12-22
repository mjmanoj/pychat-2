from Tkinter import *
import client, thread, time, ScrolledText

class App:
    def __init__(self, master):

        self.newmessages = 0
        self.counting = 0

        frame = Frame(master)
        frame.pack()

        frame.bind('<FocusIn>', self.clearcounter)
        frame.bind('<FocusOut>', self.startcounter)
        #change to regular

        self.entry = Entry(frame, width=70)
        self.entry.bind("<Return>", self.gettext)
        self.entry.pack(side=BOTTOM)

        self.texvar = StringVar()
        self.texvar.set("")
        self.label = Label(frame, textvariable=self.texvar)
        self.label.pack(side=BOTTOM)

        self.box = ScrolledText.ScrolledText(frame, wrap=WORD)
        self.box.insert(END, 'Welcome to PyChat 2!')
        self.box.config(state=DISABLED)
        self.box.pack(side=TOP)
        
        self.buffer = ''
        self.bufferfull = False

        thread.start_new_thread(client.callbacks, (self.printtex, self.blockinput, self.close))

    def startcounter(self, e):
        self.counting = 1
        self.counter = 0
        print 'new(0)'
        #change to 'new(0)'

    def clearcounter(self, e):
        self.counting = 0
        self.counter = 0
        print 'regular'
        #change back to regular

    def incrementcounter(self):
        if self.counting:
            self.counter += 1
            print 'increment'
            #set to new(self.counter)

    def printtex(self, text):
        self.box.config(state=NORMAL)
        self.box.insert(END,"\n"+text)
        self.box.config(state=DISABLED)
        self.box.yview_scroll(1,"units")
        self.incrementcounter()
        
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
