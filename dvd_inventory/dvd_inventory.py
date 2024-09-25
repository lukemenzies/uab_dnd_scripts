#!/usr/bin/env python3

"""
This is a script to inventory a folder of photos captured from DVD or CD-ROM.
Created: 2024-08-21
Last modified: 2024-08-21 by L. I. Menzies
"""

import csv
import hashlib
import io
import math
import mimetypes
import operator
from os import remove, stat, walk
from os.path import join, basename, dirname, relpath, isdir
from platform import system
from time import strftime, localtime
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
        labl000.configure(fg='black', bg=gray, bd=0, font=('Arial', 10), height=3, width=20, relief=SUNKEN, justify=CENTER)
        labl000.grid(column=1, row=0, pady=5, padx=5, sticky=NSEW)
        #
        fol = StringVar(frame001)
        labl001 = Label(frame001, text='Input\nFolder:')
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
        labl002 = Label(frame001, text='Output\nFolder:')
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
        labl003 = Label(frame001, text='Disk\nLabel:')
        labl003.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl003.grid(column=0, row=4, pady=5, padx=5, sticky=E)
        self.en003 = Entry(frame001, width=45, textvariable=owner)
        self.en003.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en003.grid(column=1, row=4, pady=5, padx=0, sticky=W)
        #
        collname = StringVar(frame001)
        labl004 = Label(frame001, text='Archives\nName:')
        labl004.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl004.grid(column=0, row=5, pady=5, padx=5, sticky=E)
        self.en004 = Entry(frame001, width=45, textvariable=collname)
        self.en004.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en004.grid(column=1, row=5, pady=5, padx=0, sticky=W)
        #
        item_type = StringVar(frame001)
        labl005 = Label(frame001, text='Disk\nNumber:')
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
        entries[0] = self.en001.get() # Path to the Input Folder
        entries[1] = self.en002.get() # Path to the Output Folder
        entries[2] = self.en003.get() # Disk Label
        entries[3] = self.en004.get() # Archives Name
        entries[4] = self.en005.get() # Disk Number
        entries[5] = self.en006.get() # BlazerID
        return entries

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

    def convert_size(size):
        """ Make file sizes human readable. """
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

    def run_inventory(indir, outdir):
        """ Run the inventory and output as csv. """
        filecounter = 0
        dsstore_count = 0
        inv_path = join(outdir, f'Inventory{strftime("%Y%b%d_%H%M%S")}temp.csv')
        inventory = open(inv_path, 'w')
        colnames = ['No.', 'Filename', 'RelPath', 'Filesize', 'Filetype', 'C-Time',
                    'Modified', 'Accessed', 'MD5', 'MD5-Time', 'SHA3_256',
                    'SHA3-Time','=>', 'mode', 'inode', 'device',
                    'enlink', 'user', 'group']
        writeCSV = csv.writer(inventory)
        writeCSV.writerow(colnames)
        for base, dirs, files in walk(indir):
            for name in files:
                filepathname = join(base, name)
                # Ignore or delete .DS_Store Files
                if basename(filepathname) == '.DS_Store':
                    # remove(filepathname)
                    dsstore_count += 1
                elif not basename(filepathname) == '.DS_Store':
                    filecounter += 1
                    rownum = str(filecounter)
                    statinfo = stat(filepathname)
                    filesize = statinfo[6]
                    csize = convert_size(filesize)
                    filemime = str(mimetypes.guess_type(filepathname)[0])
                    filectime = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_ctime))
                    # Note: On Windows, ctime is "date created" but on Unix it is
                    # "change time", i.e. the last time the metadata was changed.
                    modifdate = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_mtime))
                    accessdate = strftime("%Y.%m.%d %H:%M:%S",
                                          localtime(statinfo.st_atime))
                    md5sum = md5hash(filepathname)
                    md5time = strftime("%Y.%m.%d %H:%M:%S")
                    sha3sum = sha3hash(filepathname)
                    sha3time = strftime("%Y.%m.%d %H:%M:%S")
                    filemode = str(statinfo.st_mode)
                    fileino = str(statinfo.st_ino)
                    filedevice = str(statinfo.st_dev)
                    filenlink = str(statinfo.st_nlink)
                    fileuser = str(statinfo.st_uid)
                    filegroup = str(statinfo.st_gid)
                    showpath = relpath(filepathname, dirname(indir))
                    newrow = [rownum, name, showpath, csize, filemime, filectime,
                                modifdate, accessdate, md5sum, md5time, sha3sum,
                                sha3time, ' ', filemode, fileino, filedevice,
                                filenlink, fileuser, filegroup]
                    writeCSV.writerow(newrow)
                    print(f'\rProgress: {filecounter} Files', end='')
        inventory.close()
        if dsstore_count > 0:
            print(f'\nSkipped {dsstore_count} \'.DS_Store\' files.\n')
        return inv_path

    def sort_inventory(self, unsorted_file, in_dir):
        # print(f'Sorting Data... ')
        output_path = join(dirname(unsorted_file), f'Inventory_{basename(in_dir)}_{strftime("%Y%b%d_%H%M%S")}.csv')
        with open(unsorted_file, 'r') as un_csv:
            reading = csv.DictReader(un_csv)
            headers = reading.fieldnames
            sorted_data = sorted(reading, key=lambda row: row['RelPath'], reverse=False)
        with open(output_path, 'w') as out_csv:
            writing = csv.DictWriter(out_csv, fieldnames=headers)
            writing.writeheader()
            n = 1
            for rrows in sorted_data:
                rrows['No.'] = str(n)
                n += 1
                writing.writerow(rrows)
        remove(unsorted_file)
        return output_path

    def run_procs(self):
        successful = False
        successful = self.run_inventory()
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
