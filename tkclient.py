from Tkinter import *
import client, thread, time, ScrolledText

class CloseNote:
    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        Label(top, text='You have been disconnected from the server.').pack()
        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):
        self.top.destroy()

class App:
    def __init__(self, master):

        root.resizable(width=FALSE, height=FALSE)

        self.primary =      "#1C5FBA" #logo yellow
        self.secondary =    "#F1E300" #logo blue

        frame = Frame(master, bg= self.primary)
        frame.pack()

        self.box = ScrolledText.ScrolledText(frame, wrap=WORD, width = 80, relief = GROOVE, bg= self.primary, fg = self.secondary)
        self.box.insert(END, 'Welcome to PyChat 2!')
        self.box.config(state=DISABLED)
        self.box.pack(side=TOP)

        entryframe = Frame(master = frame)
        entryframe.pack()

        self.texvar = StringVar()
        self.texvar.set("")
        self.label = Label(entryframe, textvariable=self.texvar, bg = self.primary, fg = self.secondary)
        self.label.pack(side=LEFT)

        self.entry = Entry(entryframe, width = 50, bg= self.primary, fg = self.secondary)
        self.entry.bind("<Return>", self.gettext)
        self.entry.pack(side=LEFT)

        self.quitter = Button(frame, relief = RIDGE, text = "Quit", fg = self.secondary, bg = self.primary, command = self.quitbutton, state = DISABLED)
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
        root.quit()

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
        dialog = CloseNote(root)
        root.wait_window(dialog.top)
        root.quit()

root = Tk()

app = App(root)

root.mainloop()
