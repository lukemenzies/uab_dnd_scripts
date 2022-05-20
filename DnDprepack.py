#!/usr/bin/env python3
"""
Script to take Output folder of individual pages and place them into top-
level Item folders. Generates a CSV that can be edited. Output of this
script can be fed into SIPmaker.

Created by L. I. Menzies 2022-04-13
Last modified by L. I. Menzies 2022-04-13
"""

import csv, time
import tkinter as tk
from os import getcwd, getenv, listdir, mkdir, path, remove
from platform import system
from shutil import copyfile
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory

""" Global color definitions, w/ official UAB RGB values """
uabgreen = '#%02x%02x%02x' % (30, 107, 82)
dragongreen = '#%02x%02x%02x' % (20, 75, 57)
campusgreen = '#%02x%02x%02x' % (128, 188, 0)
loyalyellow = '#%02x%02x%02x' % (255, 212, 0)
blazegold = '#%02x%02x%02x' % (170, 151, 103)
smoke = '#%02x%02x%02x' % (128, 130, 133)
gray = '#%02x%02x%02x' % (215, 210, 203)

class GetValues:
    def __init__(self, root):
        frame001 = Frame(root)
        labl000 = Label(frame001, text='DnD\nPre-Packer')
        labl000.configure(fg='black', bg=gray, bd=0, font=('Arial', 10), height=3, width=20, relief=SUNKEN, justify=CENTER)
        labl000.grid(column=1, row=0, pady=5, padx=5, sticky=NSEW)
        #
        fol = StringVar(frame001)
        labl001 = Label(frame001, text='\"Output\"\nFolder:')
        labl001.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl001.grid(column=0, row=2, pady=5, padx=5, sticky=E)
        self.en001 = Entry(frame001, width=45, textvariable=fol)
        self.en001.configure(bg=gray, relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en001.grid(column=1, row=2, pady=5, padx=0, sticky=W)
        browse1 = Button(frame001, text='Browse', command=lambda: self.ask_folder(fol))
        browse1.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse1.grid(column=2, row=2, pady=5, padx=5, sticky=W)
        #
        owner = StringVar(frame001)
        labl002 = Label(frame001, text='Owned By:')
        labl002.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl002.grid(column=0, row=3, pady=5, padx=5, sticky=E)
        self.en002 = Entry(frame001, width=45, textvariable=owner)
        self.en002.configure(bg=gray, relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en002.grid(column=1, row=3, pady=5, padx=0, sticky=W)
        #
        collname = StringVar(frame001)
        labl003 = Label(frame001, text='Collection\nName:')
        labl003.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl003.grid(column=0, row=4, pady=5, padx=5, sticky=E)
        self.en003 = Entry(frame001, width=45, textvariable=collname)
        self.en003.configure(bg=gray, relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en003.grid(column=1, row=4, pady=5, padx=0, sticky=W)
        #
        blazerid = StringVar(frame001)
        labl004 = Label(frame001, text='Your\nBlazerID:')
        labl004.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl004.grid(column=0, row=5, pady=5, padx=5, sticky=E)
        self.en004 = Entry(frame001, width=45, textvariable=blazerid)
        self.en004.configure(bg=gray, relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en004.grid(column=1, row=5, pady=5, padx=0, sticky=W)
        #
        frame001.configure(bg=uabgreen, highlightbackground='black', bd=5, relief=RAISED)
        frame001.grid(column=0, row=0, pady=0, padx=0, sticky=NSEW)
        #
        self.frame002 = Frame(root)
        self.collatevar = IntVar(self.frame002)
        collate_chk = Checkbutton(self.frame002, text='Collate Objects', variable=self.collatevar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        collate_chk.grid(column=2, row=0, pady=5, padx=5)
        self.collatevar.set(1)
        self.csvvar = IntVar(self.frame002)
        csv_chk = Checkbutton(self.frame002, text='Generate\nCSV Loader', variable=self.csvvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        csv_chk.grid(column=3, row=0, pady=5, padx=5)
        self.csvvar.set(1)
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        #
        frame003 = Frame(root)
        cancel = Button(frame003, text='Quit', command=root.quit)
        cancel.configure(fg='black', bg=gray, highlightbackground='white', font=('Arial', 11))
        cancel.grid(column=0, row=0, pady=5, padx=5, sticky=W)
        space = Label(frame003, text='')
        space.configure(fg=uabgreen, bg=uabgreen, highlightbackground='black', bd=0, font=('Arial', 8))
        space.grid(column=1, row=0, pady=0, padx=235, sticky=NSEW)
        submit = Button(frame003, text='Submit', command=self.run_procs)
        submit.configure(fg='black', bg=gray, highlightbackground='white', font=('Arial', 11))
        submit.grid(column=2, row=0, pady=5, padx=5, sticky=E)
        frame003.configure(bg=uabgreen, highlightbackground='black', bd=5, relief=RAISED)
        frame003.grid(column=0, row=2, pady=0, padx=0, sticky=NSEW)

    def user_home(self):
        user_os = system()
        if not user_os == 'Windows':
            userHome = getenv('HOME')
        else:
            userHome = getenv('USERPROFILE')
        return userHome

    def ask_folder(self, foname):
        foname.set(askdirectory(initialdir=path.join(self.user_home(), 'Pictures'), title='Select the Folder'))
        return foname

    def ask_file(self, fname):
        fname.set(path.abspath(askopenfilename(initialdir=path.join(self.user_home(), 'Pictures'), title='Select the master CSV File')))
        return fname

    def get_entries(self):
        entries = ['unknown', 'unknown', 'unknown', 'unknown']
        entries[0] = self.en001.get() # Path to the 'Output' folder
        entries[1] = self.en002.get() # Owned By
        entries[2] = self.en003.get() # Collection name
        entries[3] = self.en004.get() # Packaged By
        return entries

    def collate_files(self):
        info = self.get_entries()
        in_dir = info[0]
        obj_list = []
        objects = path.join(self.user_home(), 'Documents', 'ready_to_package')
        if not path.isdir(objects):
            try:
                mkdir(objects)
            except:
                messagebox.showwarning(message=f'There was an error creating the \'ready_to_package\' folder.')
                root.quit()
        for files in listdir(in_dir):
            accepted_files = ['.tif', '.pdf', '.xml', '.txt', '.jp2']
            if path.splitext(files)[1] in accepted_files:
                oldfilepath = path.join(in_dir, files)
                itemname = files[0:-10]
                itemfolder = path.join(objects, itemname)
                if not itemname in obj_list:
                    obj_list.append(itemname)
                    mkdir(itemfolder)
                    mkdir(path.join(itemfolder, 'a'))
                    mkdir(path.join(itemfolder, 'b'))
                if files[-5] == 'a':
                    newfilepath = path.join(itemfolder, 'a', files)
                    try:
                        copyfile(oldfilepath, newfilepath)
                    except:
                        messagebox.showwarning(message=f'There was an error copying:\n{files}')
                    if path.exists(newfilepath):
                        remove(oldfilepath)
                elif files[-5] == 'b':
                    newfilepath = path.join(itemfolder, 'b', files)
                    try:
                        copyfile(oldfilepath, newfilepath)
                    except:
                        messagebox.showwarning(message=f'There was an error copying:\n{files}')
                    if path.exists(newfilepath):
                        remove(oldfilepath)
                else:
                    messagebox.showwarning(message=f'The filename {files} does not \nend in \'a.tif\' or \'b.tif\'.\nSkipping it...')
        return True

    def make_csv(self):
        csv_info = self.get_entries()
        ownBy = csv_info[1]
        collection = csv_info[2]
        username = csv_info[3]
        obj_dir = path.join(self.user_home(), 'Documents', 'ready_to_package')
        if not path.isdir(obj_dir):
            messagebox.showwarning(message=f'Could not find the folder of items.\nQuitting.')
            root.quit()
        out_dir = path.join(self.user_home(), 'Documents', 'csv_loaders')
        if not path.isdir(out_dir):
            try:
                mkdir(out_dir)
            except:
                messagebox.showwarning(message=f'There was an error creating the \'csv_loaders\' folder.')
                root.quit()
        datetime = time.strftime("%Y%b%d_%H%M%S")
        try:
            newCSV = open(path.join(out_dir, f'csv_loader{datetime}.csv'), 'w')
        except:
            messagebox.showwarning(message='There was an error creating the CSV loader file.')
            root.quit()
        colnames = ['System UUID', 'Local ID', 'Owned By', 'Collection', 'Item Type', 'Packaged By']
        writer = csv.writer(newCSV)
        writer.writerow(colnames)
        flist = listdir(obj_dir)
        sorted_flist = sorted(flist)
        numfiles = len(sorted_flist)
        numrows = 0
        for dirs in sorted_flist:
            fpath = path.join(obj_dir, dirs)
            if path.isdir(fpath):
                newrow = ['unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown']
                newrow[0] = dirs
                newrow[1] = ''
                newrow[2] = ownBy
                newrow[3] = collection
                newrow[4] = ''
                newrow[5] = username
                numrows += 1
                writer.writerow(newrow)
        newCSV.close()
        messagebox.showinfo(message=f'Created CSV loader file\n with {numrows} rows for {numfiles} files.')
        return True

    def run_procs(self):
        finished = False
        collate_yesno = self.collatevar.get()
        csv_yesno = self.csvvar.get()
        if collate_yesno == 1:
            finished = self.collate_files()
        if csv_yesno == 1:
            finished = self.make_csv()
        if finished == True:
            messagebox.showinfo(message=f'Done!')
            root.quit()
        else:
            messagebox.showwarning(message=f'Something went wrong.')
            root.quit()

root = tk.Tk()
w = 646
h = 401
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' %(w, h, x, y))
root.title('DnD Pre-Packer')
app = GetValues(root)
root.configure(bg=blazegold, bd=4)
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.mainloop()