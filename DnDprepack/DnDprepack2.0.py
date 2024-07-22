#!/usr/bin/env python
"""
Script to take Output folder of individual pages and place them into top-
level Item folders. Generates a CSV that can be edited. Output of this
script can be fed into SIPmaker.

Created by L. I. Menzies 2022-04-13
Last modified by L. I. Menzies 2024-06-17
"""

import csv, time, sys
import tkinter as tk
from os import getcwd, getenv, listdir, mkdir, path, remove
from platform import system
from re import compile, match
from shutil import copy2, rmtree
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

""" Global Variable for User OS"""
USER_OS = system()

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
        self.en001.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en001.grid(column=1, row=2, pady=5, padx=0, sticky=W)
        browse1 = Button(frame001, text='Browse', command=lambda: self.ask_folder(fol))
        browse1.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse1.grid(column=2, row=2, pady=5, padx=5, sticky=W)
        #
        procfol = StringVar(frame001)
        labl002 = Label(frame001, text='\"Processing\"\nFolder:')
        labl002.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl002.grid(column=0, row=3, pady=5, padx=5, sticky=E)
        self.en002 = Entry(frame001, width=45, textvariable=procfol)
        self.en002.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en002.grid(column=1, row=3, pady=5, padx=0, sticky=W)
        browse2 = Button(frame001, text='Browse', command=lambda: self.ask_folder(procfol))
        browse2.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse2.grid(column=2, row=3, pady=5, padx=5, sticky=W)
        #
        owner = StringVar(frame001)
        labl003 = Label(frame001, text='Responsible\nOrg:')
        labl003.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl003.grid(column=0, row=4, pady=5, padx=5, sticky=E)
        self.en003 = Entry(frame001, width=45, textvariable=owner)
        self.en003.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en003.grid(column=1, row=4, pady=5, padx=0, sticky=W)
        #
        collname = StringVar(frame001)
        labl004 = Label(frame001, text='Collection\nName:')
        labl004.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl004.grid(column=0, row=5, pady=5, padx=5, sticky=E)
        self.en004 = Entry(frame001, width=45, textvariable=collname)
        self.en004.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en004.grid(column=1, row=5, pady=5, padx=0, sticky=W)
        #
        item_type = StringVar(frame001)
        labl005 = Label(frame001, text='ItemType:')
        labl005.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl005.grid(column=0, row=6, pady=5, padx=5, sticky=E)
        self.en005 = Entry(frame001, width=45, textvariable=item_type)
        self.en005.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en005.grid(column=1, row=6, pady=5, padx=0, sticky=W)
        #
        blazerid = StringVar(frame001)
        labl006 = Label(frame001, text='Your\nBlazerID:')
        labl006.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl006.grid(column=0, row=7, pady=5, padx=5, sticky=E)
        self.en006 = Entry(frame001, width=45, textvariable=blazerid)
        self.en006.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en006.grid(column=1, row=7, pady=5, padx=0, sticky=W)
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
        foname.set(askdirectory(initialdir=self.user_home(), title='Select the Folder'))
        return foname

    def ask_file(self, fname):
        fname.set(path.abspath(askopenfilename(initialdir=self.user_home(), title='Select the master CSV File')))
        return fname

    def get_entries(self):
        entries = ['unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown']
        entries[0] = self.en001.get() # Path to the 'Output' folder
        entries[1] = self.en002.get() # Path to the 'Processing' folder
        entries[2] = self.en003.get() # Responsible Org. (formerly "Owned by")
        entries[3] = self.en004.get() # Collection Name
        entries[4] = self.en005.get() # Item Type
        entries[5] = self.en006.get() # Packaged By
        return entries

    def check_filenames(self, chk_folder):
        """Checks to see if file names are properly formed. If it finds a
        malformed file name it notifies the User which filename caused the error
        and returns False.
        """
        for filename in listdir(chk_folder):
            # Checks file names, ignores folder names
            if not path.splitext(filename)[1] == '':
                pattern = r"^[A-Z][A-Z][A-Z][A-Z]_[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][a|b]"
                test = path.splitext(filename)[0]
                if not len(test) == 20 or not match(pattern, test):
                    messagebox.showwarning(message=f'The filename {filename} is improperly\nformed. Quitting.')
                    return False
        return True

    def collate_files(self):
        ignored_files = []
        total_files = 0
        included_files = 0
        info = self.get_entries()
        in_dir = info[0]
        good_filenames = False
        good_filenames = self.check_filenames(in_dir)
        if good_filenames == False:
            return False
        p_dir = info[1]
        obj_list = []
        objects = path.join(p_dir, 'ready_to_package')
        if not path.isdir(objects):
            try:
                mkdir(objects)
            except:
                messagebox.showwarning(message=f'There was an error creating the \'ready_to_package\' folder.')
                return False
        for files in listdir(in_dir):
            # ignore directories/ folders
            if not path.splitext(files)[1] == '':
                total_files += 1
            accepted_files = ['.tif', '.pdf', '.xml', '.txt', '.jpg', '.iso', '.jp2', '.wav', '.mp4', '.mkv', '.mp3', '.csv']
            # script only accepts file formats of the proper type that do not begin with '.'
            if path.splitext(files)[1] not in accepted_files or files.startswith('.'):
                if not path.splitext(files)[1] == '' and not files.startswith('.'):
                    ignored_files.append(files)
            if path.splitext(files)[1] in accepted_files and not files.startswith('.'):
                included_files += 1
                oldfilepath = path.join(in_dir, files)
                itemname = files[0:-10]
                itemfolder = path.join(objects, itemname)
                if not itemname in obj_list:
                    obj_list.append(itemname)
                    try:
                        mkdir(itemfolder)
                    except FileExistsError:
                        yesno = messagebox.askyesno(message=f'The folder {itemfolder} already exists!\nOverwrite?')
                        if yesno == True:
                            rmtree(itemfolder)
                            mkdir(itemfolder)
                        else:
                            quitting = messagebox.askyesno(message=f'Do you want to quit?')
                            if quitting == True:
                                return False
                if files[-5] == 'a':
                    newfilepath = path.join(itemfolder, files)
                    try:
                        copy2(oldfilepath, newfilepath)
                    except:
                        messagebox.showwarning(message=f'There was an error copying:\n{files}')
                elif files[-5] == 'b':
                    newfilepath = path.join(itemfolder, files)
                    try:
                        copy2(oldfilepath, newfilepath)
                    except:
                        messagebox.showwarning(message=f'There was an error copying:\n{files}')
                else:
                    messagebox.showwarning(message=f'The filename {files} does not \nend in \'a\' or \'b\'.\nSkipping it...')
        messagebox.showinfo(message=f'Found {total_files} total files.\nCollated {included_files} files.\nIgnored the following:\n{ignored_files}')
        return True

    def check_ids(self, checkdir):
        for folder_id in listdir(checkdir):
            id_path = path.join(checkdir, folder_id)
            if path.isdir(id_path):
                pattern = r"^[A-Z][A-Z][A-Z][A-Z]_[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]"
                if not match(pattern, folder_id):
                    return False
        return True

    def make_csv(self):
        csv_info = self.get_entries()
        proc_dir = csv_info[1]
        ownBy = csv_info[2]
        collection = csv_info[3]
        itemType = csv_info[4]
        username = csv_info[5]
        obj_dir = path.join(proc_dir, 'ready_to_package')
        if not path.isdir(obj_dir):
            messagebox.showwarning(message=f'Could not find the \"ready_to_package\" folder.\nQuitting.')
            return False
        out_dir = path.join(proc_dir, 'csv_loaders')
        if not path.isdir(out_dir):
            try:
                mkdir(out_dir)
            except:
                messagebox.showwarning(message=f'There was an error creating the \'csv_loaders\' folder.')
                return False
        datetime = time.strftime("%Y%b%d_%H%M%S")
        good_ids = False
        good_ids = self.check_ids(obj_dir)
        if good_ids == False:
            messagebox.showwarning(message=f'One or more folders in target directory\nhave incorrect UUIDs. Quitting.')
            return False
        if USER_OS == 'Windows':
            try:
                newCSV = open(path.join(out_dir, f'csv_loader{datetime}.csv'), 'w', newline='', encoding='UTF-8')
            except:
                messagebox.showwarning(message='There was an error creating the CSV loader file.')
                return False
        else:
            try:
                newCSV = open(path.join(out_dir, f'csv_loader{datetime}.csv'), 'w', encoding='UTF-8')
            except:
                messagebox.showwarning(message='There was an error creating the CSV loader file.')
                return False
        colnames = ['System UUID', 'Local ID', 'Responsible Org', 'Collection', 'Item Type', 'Packaged By']
        writer = csv.writer(newCSV)
        writer.writerow(colnames)
        flist = listdir(obj_dir)
        sorted_flist = sorted(flist)
        numfolders = 0
        for dirs in sorted_flist:
            fpath = path.join(obj_dir, dirs)
            if path.isdir(fpath):
                newrow = ['unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown']
                newrow[0] = dirs
                newrow[1] = ''
                newrow[2] = ownBy
                newrow[3] = collection
                newrow[4] = itemType
                newrow[5] = username
                numfolders += 1
                writer.writerow(newrow)
        newCSV.close()
        messagebox.showinfo(message=f'Created CSV loader file\n with rows for {numfolders} items.')
        return True

    def run_procs(self):
        successful = False
        collate_yesno = self.collatevar.get()
        csv_yesno = self.csvvar.get()
        if collate_yesno == 1:
            successful = self.collate_files()
            if successful == False:
                messagebox.showwarning(message=f'Something went wrong during\ncollation. Quitting.')
                sys.exit()
        if csv_yesno == 1:
            successful = self.make_csv()
            if successful == False:
                messagebox.showwarning(message=f'Something went wrong during\nCSV Generation. Quitting.')
                sys.exit()
        else:
            messagebox.showinfo(message=f'Done!')
            sys.exit()

root = tk.Tk()
w = 646
h = 504
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
