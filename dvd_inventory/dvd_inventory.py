#!/usr/bin/env python3

"""
This is a script to inventory a folder of photos captured from DVD or CD-ROM.
Created: 2024-08-21
Last modified: 2024-10-15 by L. I. Menzies
"""

import hashlib
import io
import math
import mimetypes
import operator
from os import getenv, mkdir, remove, stat, walk
from os.path import abspath, exists, join, basename, dirname, relpath, isdir
from pandas import DataFrame, ExcelWriter, ExcelFile
from platform import system
from shutil import copy2, copytree
from sys import exit
from time import strftime, localtime
import tkinter as tk
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

""" Global Variables """
CHUNKSIZE = io.DEFAULT_BUFFER_SIZE

class GetValues:
    def __init__(self, root):
        frame001 = Frame(root)
        labl000 = Label(frame001, text='DVD Inventory')
        labl000.configure(fg='black', bg=gray, bd=0, font=('Arial', 10), height=3,
                            width=20, relief=SUNKEN, justify=CENTER)
        labl000.grid(column=1, row=0, pady=5, padx=5, sticky=NSEW)
        # Input Folder
        input_folder = StringVar(frame001)
        labl001 = Label(frame001, text='Input\nFolder:')
        labl001.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl001.grid(column=0, row=2, pady=5, padx=5, sticky=E)
        self.en001 = Entry(frame001, width=40, textvariable=input_folder)
        self.en001.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en001.grid(column=1, row=2, pady=5, padx=0, sticky=W)
        browse1 = Button(frame001, text='Browse', command=lambda: self.ask_folder(input_folder))
        browse1.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse1.grid(column=2, row=2, pady=5, padx=5, sticky=W)
        # Output Folder
        output_folder = StringVar(frame001)
        labl002 = Label(frame001, text='Output\nFolder:')
        labl002.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4,font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl002.grid(column=0, row=3, pady=5, padx=5, sticky=E)
        self.en002 = Entry(frame001, width=40, textvariable=output_folder)
        self.en002.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en002.grid(column=1, row=3, pady=5, padx=0, sticky=W)
        browse2 = Button(frame001, text='Browse', command=lambda: self.ask_folder(output_folder))
        browse2.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse2.grid(column=2, row=3, pady=5, padx=5, sticky=W)
        # Accession Number/ Donation Number
        # Default accession number is the current donation: "A2020-04"
        # This default should be changed here when moving to
        # a new collection/ donation/ accession number.
        accession = StringVar(frame001)
        accession.set('A2020-04')
        labl003 = Label(frame001, text='Accession\nNumber:')
        labl003.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4,font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl003.grid(column=0, row=4, pady=5, padx=5, sticky=E)
        self.en003 = Entry(frame001, width=40, textvariable=accession)
        self.en003.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en003.grid(column=1, row=4, pady=5, padx=0, sticky=W)
        # Disk Number
        disk_number = StringVar(frame001)
        labl004 = Label(frame001, text='Disk\nNumber:')
        labl004.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl004.grid(column=0, row=5, pady=5, padx=5, sticky=E)
        self.en004 = Entry(frame001, width=40, textvariable=disk_number)
        self.en004.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en004.grid(column=1, row=5, pady=5, padx=0, sticky=W)
        # Validate button, only allows integers in the Entry field
        # valid1 = Button(frame001, text='Validate', command=lambda: self.onValidate(disk_number))
        # valid1.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        # valid1.grid(column=2, row=5, pady=5, padx=5, sticky=W)
        # Disk Label
        disk_label = StringVar(frame001)
        labl005 = Label(frame001, text='Disk\nLabel:')
        labl005.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl005.grid(column=0, row=6, pady=5, padx=5, sticky=E)
        self.en005 = Entry(frame001, width=40, textvariable=disk_label)
        self.en005.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en005.grid(column=1, row=6, pady=5, padx=0, sticky=W)
        # BlazerID
        blazerid = StringVar(frame001)
        labl006 = Label(frame001, text='Your\nBlazerID:')
        labl006.configure(fg='black', bg=blazegold, highlightbackground='black',
                            bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl006.grid(column=0, row=7, pady=5, padx=5, sticky=E)
        self.en006 = Entry(frame001, width=40, textvariable=blazerid)
        self.en006.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en006.grid(column=1, row=7, pady=5, padx=0, sticky=W)
        # Configure Frame001
        frame001.configure(bg=uabgreen, highlightbackground='black', bd=5, relief=RAISED)
        frame001.grid(column=0, row=0, pady=0, padx=0, sticky=NSEW)
        # Inventory Checkbox
        self.frame002 = Frame(root)
        self.inventoryvar = IntVar(self.frame002)
        collate_chk = Checkbutton(self.frame002, text='Create Inventory', variable=self.inventoryvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        collate_chk.grid(column=2, row=0, pady=5, padx=5)
        self.inventoryvar.set(1)
        # Copy Checkbox
        self.copyvar = IntVar(self.frame002)
        csv_chk = Checkbutton(self.frame002, text='Copy Files', variable=self.copyvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        csv_chk.grid(column=3, row=0, pady=5, padx=5)
        self.copyvar.set(1)
        # Configure Frame002
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        # Quit
        frame003 = Frame(root)
        cancel = Button(frame003, text='Quit', command=root.quit)
        cancel.configure(fg='black', bg=gray, highlightbackground='white', font=('Arial', 11))
        cancel.grid(column=0, row=0, pady=5, padx=5, sticky=W)
        space = Label(frame003, text='')
        space.configure(fg=uabgreen, bg=uabgreen, highlightbackground='black', bd=0, font=('Arial', 8))
        space.grid(column=1, row=0, pady=0, padx=215, sticky=NSEW)
        # Submit
        submit = Button(frame003, text='Submit', command=lambda: self.run_procs(disk_number))
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

    def onValidate(self, string):
        input = self.en004.get()
        if str.isdigit(input) or str(input) == "":
            string.set(input)
            return True
        else:
            string.set("")
            return False

    def ask_folder(self, foname):
        foname.set(askdirectory(initialdir=self.user_home(), title='Select the Folder'))
        return foname

    def ask_file(self, fname):
        fname.set(abspath(askopenfilename(initialdir=self.user_home(), title='Select the master CSV File')))
        return fname

    def get_entries(self):
        entryvals = ['unknown', 'unknown', 'unknown', 'unknown', 'unknown', 'unknown']
        entryvals[0] = self.en001.get() # Path to the Input Folder
        entryvals[1] = self.en002.get() # Path to the Output Folder
        entryvals[2] = self.en003.get() # Accession Number
        entryvals[3] = f'{int(self.en004.get()):04d}' # Disk Number
        entryvals[4] = self.en005.get() # Disk Label
        entryvals[5] = self.en006.get() # BlazerID
        return entryvals

    def md5hash(file_name):
        """ Generate SHA3-256 hashes. """
        hash_md5 = hashlib.md5()
        try:
            with open(file_name, "rb") as md5file:
                for chunks in iter(lambda: md5file.read(CHUNKSIZE), b""):
                    hash_md5.update(chunks)
        except OSError:
            return "OS Error"
        return hash_md5.hexdigest()

    def sha3hash(filname):
        """ Generate SHA3-256 hashes. """
        hash_sha3 = hashlib.sha3_256()
        try:
            with open(filname, "rb") as sha3file:
                for chunks in iter(lambda: sha3file.read(CHUNKSIZE), b""):
                    hash_sha3.update(chunks)
        except OSError:
            return "OS Error"
        return hash_sha3.hexdigest()

    def convert_size(self, size):
        """ Make file sizes human readable """
        if (size == 0):
            return '0B'
        # size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
        # i = int(math.floor(math.log(size,1024)))
        # p = math.pow(1024,i)
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1000)))
        p = math.pow(1000, i)
        s = round(size / p, 2)
        return '%s%s' % (s, size_name[i])

    def run_inventory(self, entry_values):
        """ Run the inventory and output as Excel """
        filecounter = 0
        dsstore_count = 0
        indir = entry_values[0].strip().replace(" ", "")
        workingdir = entry_values[1].strip().replace(" ", "")
        accno = entry_values[2].strip().replace(" ", "")
        diskno = entry_values[3].strip().replace(" ", "")
        disklabel = entry_values[4].strip()
        runby = entry_values[5].strip().replace(" ", "")
        # Create the AccessionNo_DiskNo folder
        outdir = join(workingdir, f'{accno}_disk{diskno}')
        if exists(outdir):
            contin = messagebox.askyesno(message=f'The folder for this disk\nexists! Continue?')
            if contin == False:
                return False
        elif not exists(outdir):
            mkdir(outdir)
        # Create a data frame from a row of rows
        all_rows = []
        colnames = ['Accession Number', 'Disk Number', 'Disk Label', 'File Name',
                    'Path', 'Size', 'Format', 'Created', 'Modified', 'Date Run', 'Run By']
        for base, dirs, files in walk(indir):
            for name in files:
                filepathname = join(base, name)
                # Ignore or delete .DS_Store Files
                if basename(filepathname) == '.DS_Store':
                    # remove(filepathname)
                    dsstore_count += 1
                elif not basename(filepathname) == '.DS_Store':
                    filecounter += 1
                    statinfo = stat(filepathname)
                    filesize = statinfo[6]
                    csize = self.convert_size(filesize)
                    filemime = str(mimetypes.guess_type(filepathname)[0])
                    filectime = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_ctime))
                    # Note: On Windows, ctime is "date created" but on Unix it is
                    # "change time", i.e. the last time the metadata was changed.
                    modifdate = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_mtime))
                    showpath = relpath(filepathname, dirname(indir))
                    runtime = strftime("%Y.%m.%d %H:%M:%S")
                    newrow = [accno, diskno, disklabel, name, showpath, csize,
                                filemime, filectime, modifdate, runtime, runby]
                    all_rows.append(newrow)
                    # print(f'\rProgress: {filecounter} Files', end='')
        if dsstore_count > 0:
        #    print(f'\nSkipped {dsstore_count} \'.DS_Store\' files.\n')
            messagebox.showinfo(message=f'Skipped {dsstore_count} \'.DS_Store\' files.')
        data_frame = DataFrame(all_rows, columns=colnames)
        outfile = f'Inventory_{accno}_{diskno}_{strftime("%Y%b%d_%H%M%S")}.xlsx'
        output_path = join(outdir, outfile)
        excel_writer = ExcelWriter(output_path)
        data_frame.sort_values(['Path']).to_excel(excel_writer, index=False)
        excel_writer.close()
        messagebox.showinfo(message=f'Total Files: \n{filecounter}')
        return True

    def copy_img_files(self, entry_values):
        iso_dir = entry_values[0].strip().replace(" ", "")
        working_dir = entry_values[1].strip().replace(" ", "")
        acc_num = entry_values[2].strip().replace(" ", "")
        disk_num = entry_values[3].strip().replace(" ", "")
        # Check if AccessionNo_DiskNo folder exists
        out_dir = join(working_dir, f'{acc_num}_disk{disk_num}')
        if not exists(out_dir):
            mkdir(out_dir)
        # Create the Disk Copy Directory
        destination = join(out_dir, f'Disk{disk_num}')
        try:
            copytree(iso_dir, destination, copy_function=copy2)
        except FileExistsError:
            messagebox.showwarning(message=f'{destination}\nalready exists! Fix,\nand run \"copy\" again.')
            return False
        return True

    def run_procs(self, dnumber):
        valid = False
        valid = self.onValidate(dnumber)
        if valid == False:
            messagebox.showwarning(message=f'For \"Disk Number\"\nenter only numbers')
            return
        values = self.get_entries()
        inventory_yesno = self.inventoryvar.get()
        copy_yesno = self.copyvar.get()
        if inventory_yesno == 1:
            successful = False
            successful = self.run_inventory(values)
            if successful == False:
                messagebox.showwarning(message=f'Something went wrong during\ninventory creation. Quitting.')
                exit()
        if copy_yesno == 1:
            success = False
            success = self.copy_img_files(values)
            if success == False:
                messagebox.showwarning(message=f'Something went wrong during\nthe copy process. Quitting.')
                exit()
        messagebox.showinfo(message=f'Done!')
        exit()

root = tk.Tk()
w = 646
h = 504
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' %(w, h, x, y))
root.title('DVD Inventory')
app = GetValues(root)
root.configure(bg=blazegold, bd=4)
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.mainloop()
