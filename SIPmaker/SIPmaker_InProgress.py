#!/usr/bin/env python3
"""
====================================================================
SIP Maker - version 1.0.0
Submission Information Package (SIP) builder
Designed and written by L. I. Menzies
Head of Digitization and Digital Preservation (DnD)
UAB Libraries
University of Alabama at Birmingham
1700 University Boulevard
Birmingham, AL 35294

Initial script created 2022-03-30 by L. I. Menzies
This Version Last Updated 2023-03-30 by L. I. Menzies
====================================================================
For more information, see the UABL DnD collaboration wiki:
https://uab-libraries.atlassian.net/wiki/spaces/DIGITIZATI/pages/349634561/SIP+Maker
or contact L. I. Menzies = menziesluke (at) gmail (dot) com
====================================================================
"""

import bagit, csv, hashlib, io, math, mimetypes, sys, tarfile, time, uuid
import tkinter as tk
from os import getcwd, getenv, listdir, mkdir, path, remove, rename, stat, walk
from platform import system
from tkinter import messagebox, Button, Entry, Label, Checkbutton, Frame, Toplevel, OptionMenu, Text, Scrollbar, StringVar, IntVar
from tkinter.filedialog import askdirectory, askopenfilename
from PIL import Image, ImageTk
from rdflib import URIRef, Graph, BNode, Literal
from rdflib.namespace import *
from shutil import copytree, move, rmtree

""" Global color definitions, w/ official UAB RGB values """
uabgreen = '#%02x%02x%02x' % (30, 107, 82)
dragongreen = '#%02x%02x%02x' % (20, 75, 57)
campusgreen = '#%02x%02x%02x' % (128, 188, 0)
loyalyellow = '#%02x%02x%02x' % (255, 212, 0)
blazegold = '#%02x%02x%02x' % (170, 151, 103)
smoke = '#%02x%02x%02x' % (128, 130, 133)
gray = '#%02x%02x%02x' % (215, 210, 203)

def resource_path(relative_path):
    """ Fixes the problem with PyInstaller not hooking associated files """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, 'data', relative_path)


class ToggleFrame(Frame):
    """ Creates a toggle frame for optional functions """
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.show = IntVar()
        self.show.set(0)
        xpad = 6
        ypad = 5
        basefont = 10
        spacepad = 175
        # Frame with the "Show Options" and "Prompt after Each Action?" buttons
        self.show_frame = Frame(self)
        self.space = Label(self.show_frame, text='')
        self.space.configure(fg=dragongreen, bg=dragongreen, relief='flat')
        self.space.grid(column=0, row=0, pady=0, padx=spacepad, sticky='e')
        self.togButton = Checkbutton(self.show_frame, text='Show Options', command=self.tog_options, variable=self.show,
                                     fg='black', bg=gray, bd=4, font=('Arial', basefont), justify='left')
        self.togButton.grid(column=1, row=0, pady=0, padx=xpad, sticky='w')
        self.prompt = IntVar()
        self.prompt.set(0)
        self.promptButton = Checkbutton(self.show_frame, text='Prompt after Each Action?', variable=self.prompt,
                                        fg='black', bg=gray, bd=4, font=('Arial', basefont), justify='left')
        self.promptButton.grid(column=2, row=0, pady=0, padx=xpad, sticky='w')
        # Frame with all of the Options
        self.sub_frame = Frame(self)
        labl4 = Label(self.sub_frame, text='Options:')
        labl4.configure(fg='black', bg=blazegold, bd=4, font=('Arial', basefont), height=2, width=9, justify='center')
        labl4.grid(column=0, row=0, pady=5, padx=5, sticky='w')
        # Options checkbuttons
        # Pre-Bag puts objects into a subfolder of the same name, to preserve folder names during Bagging
        self.prebagvar = IntVar(self)
        prebag_chk = Checkbutton(self.sub_frame, text='Pre-Bag\nObjects', variable=self.prebagvar, fg='black',
                                  bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4,
                                  font=('Arial', basefont), justify='left')
        prebag_chk.grid(column=1, row=0, pady=5, padx=xpad)
        # Metadata
        self.metavar = IntVar(self)
        meta_chk = Checkbutton(self.sub_frame, text='Create min\nmetadata files', variable=self.metavar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4,
                                font=('Arial', basefont), justify='left')
        meta_chk.grid(column=2, row=0, pady=5, padx=xpad)
        # Inventory
        self.invenvar = IntVar(self)
        inv_chk = Checkbutton(self.sub_frame, text='Generate\n\'manifest.csv\'', variable=self.invenvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', basefont), justify='left')
        inv_chk.grid(column=3, row=0, pady=5, padx=xpad)
        # BagIt
        self.bagitvar = IntVar(self)
        bagit_chk = Checkbutton(self.sub_frame, text='Run\nBagIt', variable=self.bagitvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', basefont), justify='left')
        bagit_chk.grid(column=4, row=0, pady=5, padx=xpad)
        # Tar
        self.tarvar = IntVar(self)
        tar_chk = Checkbutton(self.sub_frame, text='TAR\nObjects', variable=self.tarvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', basefont), justify='left')
        tar_chk.grid(column=5, row=0, pady=5, padx=xpad)
        # Transfer manifest
        self.transvar = IntVar(self)
        trans_chk = Checkbutton(self.sub_frame, text='Transfer\nManifest', variable=self.transvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', basefont), justify='left')
        trans_chk.grid(column=6, row=0, pady=5, padx=xpad)
        # Set defaults to "checked"
        self.prebagvar.set(1)
        self.metavar.set(1)
        self.invenvar.set(1)
        self.bagitvar.set(1)
        self.tarvar.set(1)
        self.transvar.set(1)
        #
        self.sub_frame.configure(bd=2, bg=dragongreen, relief='raised')
        self.show_frame.configure(bd=2, bg=dragongreen, relief='flat')
        self.show_frame.grid(column=0, row=3, pady=0, padx=0, sticky='nsew')

    def tog_options(self):
        if self.show.get() == 1:
            self.sub_frame.grid(column=0, row=0, pady=0, padx=0, sticky='nsew')
            self.togButton.configure(text='Hide Options')
        else:
            self.sub_frame.grid_forget()
            self.togButton.configure(text='Show Options')


class ObjFormatter:
    """ The main widget """
    def __init__(self, root):
        imgpad = 250
        xpadd = 5
        ypadd = 5
        basefont = 10
        entryfont = 11
        buttonpad = 220

        def load_image(imgname):
            imgpath = resource_path(imgname)
            openimg = Image.open(imgpath)
            return ImageTk.PhotoImage(openimg)

        # Main widget background image
        frame0 = Frame(root)
        self.logoimage = load_image("SIPmakerLogo.jpg")
        self.logoimglabel = Label(frame0, image=self.logoimage)
        self.logoimglabel.configure(bg='black', bd=0, relief='flat')
        self.logoimglabel.grid(column=0, row=0, pady=7, padx=imgpad, sticky='nsew')
        frame0.configure(bg='white', bd=5, relief='sunken')
        frame0.grid(column=0, row=0, pady=0, padx=0, sticky='nsew')
        frame1 = Frame(root)
        # Entry for the Folder that contains the items
        itemfolder = StringVar(frame1)
        labl1 = Label(frame1, text='Folder of\nItems:')
        labl1.configure(fg='black', bg=blazegold, bd=0, font=('Arial', basefont), height=2, width=9, justify='center')
        labl1.grid(column=0, row=0, pady=5, padx=5, sticky='e')
        browse1 = Button(frame1, text='Browse', command=lambda: self.ask_folder(itemfolder))
        browse1.configure(bg=smoke, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        browse1.grid(column=2, row=0, pady=5, padx=5, sticky='w')
        self.e1 = Entry(frame1, width=50, textvariable=itemfolder)
        self.e1.configure(bg=gray, fg='black', relief='sunken', bd=2, font=('Arial', entryfont + 2), justify='left')
        self.e1.grid(column=1, row=0, pady=5, padx=0, sticky='w')
        # Entry for the "processing" folder, which includes "ready_to_transfer" etc. subfolders
        processfolder = StringVar(frame1)
        labl2 = Label(frame1, text='Processing\nFolder:')
        labl2.configure(fg='black', bg=blazegold, bd=0, font=('Arial', basefont), height=2, width=9, justify='center')
        labl2.grid(column=0, row=1, pady=5, padx=5, sticky='e')
        browse2 = Button(frame1, text='Browse', command=lambda: self.ask_folder(processfolder))
        browse2.configure(bg=smoke, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        browse2.grid(column=2, row=1, pady=5, padx=5, sticky='w')
        self.e2 = Entry(frame1, width=50, textvariable=processfolder)
        self.e2.configure(bg=gray, fg='black', relief='sunken', bd=2, font=('Arial', entryfont + 2), justify='left')
        self.e2.grid(column=1, row=1, pady=5, padx=0, sticky='w')
        # Entry for the master CSV metadata file
        csvfile = StringVar(frame1)
        labl3 = Label(frame1, text='CSV File:')
        labl3.configure(fg='black', bg=blazegold, bd=0, font=('Arial', basefont), height=2, width=9, justify='center')
        labl3.grid(column=0, row=2, pady=5, padx=5, sticky='e')
        browse3 = Button(frame1, text='Browse', command=lambda: self.ask_file(csvfile))
        browse3.configure(bg=smoke, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont),
                          relief='raised')
        browse3.grid(column=2, row=2, pady=5, padx=5, sticky='w')
        self.e3 = Entry(frame1, width=50, textvariable=csvfile)
        self.e3.configure(bg=gray, fg='black', relief='sunken', bd=2, font=('Arial', entryfont + 2), justify='left')
        self.e3.grid(column=1, row=2, pady=5, padx=0, sticky='w')
        # Drop-Down of the column headings in the master CSV file
        labl4 = Label(frame1, text='CSV ID\nColumn:')
        labl4.configure(fg='black', bg=blazegold, bd=0, font=('Arial', basefont), height=2, width=9, justify='center')
        labl4.grid(column=0, row=3, pady=5, padx=5, sticky='e')
        self.variable = StringVar(frame1)
        self.options = StringVar(frame1)
        self.options.trace('r', self.get_headers)
        firstone = ["Select CSV", "Then \'Refresh\'"]
        self.hdmenu = OptionMenu(frame1, self.variable, *firstone)
        self.hdmenu.configure(width=20, fg='black', bg=uabgreen, font=('Arial', basefont + 2))
        self.hdmenu.grid(column=1, row=3, pady=5, padx=0, sticky='e')
        self.e4 = Entry(frame1, width=24, textvariable=self.variable)
        self.e4.configure(bg=gray, fg='black', relief='sunken', bd=2, font=('Arial', entryfont + 2), justify='left')
        self.e4.grid(column=1, row=3, pady=5, padx=0, sticky='w')
        refresh1 = Button(frame1, text='Refresh', command=lambda: self.get_headers(csvfile))
        refresh1.configure(bg=smoke, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        refresh1.grid(column=2, row=3, pady=5, padx=5, sticky='w')
        frame1.configure(bg=uabgreen, bd=5, relief='raised')
        frame1.grid(column=0, row=1, pady=0, padx=0, sticky='nsew')
        # Checkbuttons
        frame2 = ToggleFrame(root)
        frame2.configure(bg=dragongreen, bd=5, relief='flat')
        frame2.grid(column=0, row=2, pady=0, padx=0, sticky='n')
        # Buttons for Quit, Instructions, and Submit
        frame3 = Frame(root)
        # self.buttonimg = load_image("quit_button.png")
        # cancel1 = Button(frame3, text='Quit', image=self.buttonimg, command=root.quit)
        cancel1 = Button(frame3, text='Quit', command=root.quit)
        cancel1.configure(bg=gray, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        cancel1.grid(column=0, row=0, pady=5, padx=xpadd, sticky='e')
        instruct = Button(frame3, text='Instructions', command=lambda: instructions(basefont))
        instruct.configure(bg=gray, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        instruct.grid(column=1, row=0, pady=5, padx=buttonpad, sticky='e')
        submit1 = Button(frame3, text='Submit', command=lambda: self.run_procs(root, frame2))
        submit1.configure(bg=gray, fg='black', highlightbackground=uabgreen, font=('Arial', entryfont))
        submit1.grid(column=2, row=0, pady=5, padx=xpadd, sticky='e')
        frame3.configure(bg=uabgreen, bd=5, relief='raised')
        frame3.grid(column=0, row=3, pady=0, padx=0, sticky='nsew')

    def user_home(self):
        user_os = system()
        if not user_os == 'Windows':
            userHome = getenv('HOME')
        else:
            userHome = getenv('USERPROFILE')
        return userHome

    def ask_folder(self, foname):
        startfolder1 = self.user_home()
        foname.set(path.abspath(askdirectory(initialdir=startfolder1, title='Select the Folder')))
        return foname

    def ask_file(self, fname):
        startfolder2 = self.user_home()
        fname.set(path.abspath(askopenfilename(initialdir=startfolder2, title='Select the master CSV File')))
        return fname

    def pre_bag(self, root, packdir, moreopts1):
        """
        Preserves departmental folder structure during Bagging by moving
        object contents into a subdirectory named with the local object ID
        """
        numitems = 0
        obj_list = [f for f in listdir(packdir) if len(f.split('.')) == 1]
        for item in obj_list:
            oldpath = path.join(packdir, item)
            newpath = path.join(oldpath, item)
            if not path.exists(newpath):
                numitems += 1
                temppath = path.join(packdir, f'tempdir{numitems}')
                mkdir(temppath)
                move(oldpath, temppath)
                rename(temppath, oldpath)
        if not moreopts1 == 0:
            if self.prompting == 0:
                runnext1 = True
            else:
                runnext1 = messagebox.askyesno(message=f'Pre-Bagged {numitems} Objects.\n\nContinue?')
        else:
            runnext1 = False
            messagebox.showinfo(message=f'Pre-Bagged {numitems} Objects.')
        return runnext1

    def get_headers(self, *args):
        """ Retrieves the options for the drop-down menu of CSV headers """
        csvfi = self.e3.get()
        csvpath = path.join(str(csvfi))
        if path.exists(csvpath) and path.splitext(csvpath)[1] == '.csv':
            with open(csvfi, 'r', encoding='utf-8') as cfile:
                hreader = csv.DictReader(cfile)
                opts = hreader.fieldnames
        else:
            opts = ["Select CSV", "Then \'Refresh\'"]
        self.variable.set(opts[0])
        menu = self.hdmenu['menu']
        menu.delete(0, 'end')
        for headr in opts:
            menu.add_command(label=headr, command=lambda idcolumn=headr: self.variable.set(idcolumn))

    def meta_from_csv(self, csvIn, locids, fpath):
        nfiles = 0
        rfiles = 0
        overwrite_all = False
        firstone = True
        with open(csvIn, 'r', encoding='utf-8') as incsv:
            reader = csv.DictReader(incsv)
            headers = reader.fieldnames
            verifyHeadrs = ['System UUID', 'Local ID', 'Owned By', 'Collection', 'Item Type', 'Packaged By']
            if not headers == verifyHeadrs:
                messagebox.showwarning(message="Your input CSV is not formatted correctly.\n\nQuitting action.")
                return [0, 0]
            for row in reader:
                skip1 = False
                foldname = row['%s' % locids]
                foldpath = path.join(fpath, foldname)
                if not path.exists(foldpath):
                    skip1 = True
                # The function skips objects that are Bags or already have a
                # 'metadata.csv' file. Thus it skips creating a 'metadata.xml'
                # for these objects also.
                if path.exists(path.join(foldpath, 'data')):
                    skip1 = messagebox.askyesno(
                        message="It appears that \'%s\' is a bag.\n\nSkip creating \'metadata.csv\' for this one item?" % foldname)
                if path.exists(path.join(foldpath, 'metadata.csv')) and firstone == True:
                    firstone = False
                    overwrite_all = messagebox.askyesno(
                        message="At least one \'metadata.csv\' already\nexists. Overwrite ALL of them?")
                if path.exists(path.join(foldpath, 'metadata.csv')) and overwrite_all == False:
                    skip1 = True
                if skip1 == False:
                    metafile = path.join(foldpath, 'metadata.csv')
                    with open(metafile, 'w') as newmeta:
                        metawriter = csv.DictWriter(newmeta, fieldnames=headers)
                        metawriter.writeheader()
                        metawriter.writerow(row)
                    nfiles += 1
                    newmeta.close()
                    rdfok = False
                    # rdfok = self.make_rdf(metafile)
                    if rdfok == True:
                        rfiles += 1
        return [nfiles, rfiles]

    def create_meta(self, folderpath, myfile, idcolname, moreopts2):
        """
        Generates minimal metadata files, 'metadata.csv' and 'metadata.xml'
        based on a master CSV or a METS xml file
        """
        sourcetype = 'csv'  # default
        counts = [0, 0]  # default
        if path.splitext(myfile)[1] == '.csv':
            sourcetype = 'csv'
        else:
            messagebox.showwarning(message="The metadata source file must be CSV.\nQuitting action.")
            runnext2 = False
            return runnext2
        if sourcetype == 'csv':
            counts = self.meta_from_csv(myfile, idcolname, folderpath)
        if not moreopts2 == 0:
            if self.prompting == 0:
                runnext2 = True
            else:
                runnext2 = messagebox.askyesno(message=f'Created {counts[0]} \'metadata.csv\' and {counts[1]} \'metadata.xml\' files.\n\nProceed with the next action?')
        else:
            runnext2 = False
            messagebox.showwarning(
                message=f'Created {counts[0]} \'metadata.csv\' and {counts[1]} \'metadata.xml\' files.')
        return runnext2

    def md5hash(self, finame):
        """ Generates MD5 hashes """
        hash_md5 = hashlib.md5()
        with open(finame, "rb") as md5file:
            for chunk in iter(lambda: md5file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def sha256hash(self, filnam):
        """ Generates SHA256 hashes """
        chunksize = io.DEFAULT_BUFFER_SIZE
        hash_sha256 = hashlib.sha256()
        with open(filnam, "rb") as sha256file:
            for chunk in iter(lambda: sha256file.read(chunksize), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def sha3hash(self, filname):
        """ Generates SHA3-256 hashes """
        chunksize = io.DEFAULT_BUFFER_SIZE
        hash_sha3 = hashlib.sha3_256()
        with open(filname, "rb") as sha3file:
            for chunks in iter(lambda: sha3file.read(chunksize), b""):
                hash_sha3.update(chunks)
        return hash_sha3.hexdigest()

    def convert_size(self, size):
        """ Converts bytes to human readable denominations """
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

    def run_inventory(self, objectsdir, moreopts3):
        """
        Runs an inventory and generates 'manifest.csv' files for each object
        """
        manifiles = 0
        for obj in listdir(objectsdir):
            objpath = path.join(objectsdir, obj)
            walkpath = path.join(objpath, obj)
            skipit = False
            counter = 0
            if not path.isdir(objpath):
                skipit = True
            elif path.isdir(objpath):
                if path.exists(path.join(objpath, 'data')):
                    isabag = messagebox.askyesno(message="It appears that \'%s\' is a bag.\nSkip this object?" % obj)
                    if isabag == True:
                        skipit = True
                if path.exists(path.join(objpath, 'manifest.csv')):
                    skipit = True
                    messagebox.showwarning(
                        message="The file \'manifest.csv\' already exists.\nSkipping inventory of the object: \n\'%s\'" % obj)
            if skipit == False:
                manifiles += 1
                temp_path = path.join(objpath, 'temp_manifest.csv')
                tempmani = open(temp_path, 'w', encoding='utf-8')
                temp_writer = csv.writer(tempmani)
                headrow = ['Filename', 'Relative Path', 'Filesize', 'Filetype', 'C-Time', 'Modified', 'Accessed',
                            'MD5', 'SHA256', 'ChecksumDateTime', 'mode', 'inode',
                            'device', 'enlink', 'user', 'group']
                temp_writer.writerow(headrow)
                for base, dirs, files in walk(walkpath):
                    for name in files:
                        filepathname = path.join(base, name)
                        # Deletes .DS_Store Files
                        if name == '.DS_Store':
                            remove(filepathname)
                        # elif not path.basename(filepathname) == '.DS_Store':
                        # Ignores files that begin with '.'
                        elif not name == '.DS_Store' and not name.startswith('.'):
                            counter += 1
                            rownum = str(counter)
                            statinfo = stat(filepathname)
                            filesize = statinfo[6]
                            csize = self.convert_size(filesize)
                            filemime = str(mimetypes.guess_type(filepathname)[0])
                            filectime = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(statinfo.st_ctime))
                            # note: on a Windows system, ctime is "date created" but on Unix it is
                            # "change time", i.e. the last time the metadata was changed.
                            modifdate = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(statinfo.st_mtime))
                            accessdate = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(statinfo.st_atime))
                            md5sum = self.md5hash(filepathname)
                            sha256sum = self.sha256hash(filepathname)
                            runtime = time.strftime("%Y.%m.%d %H:%M:%S")
                            filemode = str(statinfo.st_mode)
                            fileino = str(statinfo.st_ino)
                            filedevice = str(statinfo.st_dev)
                            filenlink = str(statinfo.st_nlink)
                            fileuser = str(statinfo.st_uid)
                            filegroup = str(statinfo.st_gid)
                            # Displays a shortened Path for each file, excluding the directories
                            # that precede the working directory that contains the objects.
                            showpath = path.relpath(filepathname, objpath)
                            newrow = [name, showpath, csize, filemime, filectime, modifdate, accessdate,
                                        md5sum, sha256sum, runtime, filemode, fileino, filedevice,
                                        filenlink, fileuser, filegroup]
                            temp_writer.writerow(newrow)
                tempmani.close()
                # Sort the temporary manifest just created by Relative Path
                with open(temp_path, 'r') as unsorted_csv:
                    unsort_reader = csv.DictReader(unsorted_csv)
                    sorted_list = sorted(unsort_reader, key=lambda row:(row['Relative Path']), reverse=False)
                m = path.join(objpath, 'manifest.csv')
                with open(m, 'w') as manifest:
                    mwriter = csv.DictWriter(manifest, fieldnames=headrow)
                    mwriter.writeheader()
                    for sortrow in sorted_list:
                        mwriter.writerow(sortrow)
                if path.exists(m):
                    remove(temp_path)
        if not moreopts3 == 0:
            if self.prompting == 0:
                runnext3 = True
            else:
                runnext3 = messagebox.askyesno(
                    message="Created %d \'manifest.csv\' files.\n\nProceed with the next action?" % manifiles)
        else:
            runnext3 = False
            messagebox.showwarning(message="Created %d \'manifest.csv\' files." % manifiles)
        return runnext3

    def run_bagit(self, bagsdir, moreopts4):
        """ Bags all objects in a single directory, according to APTrust BagIt profile """
        validbags = 0
        totalbags = 0
        # Defining MData tags
        APT_bag_info = {
            'Bag-Count': '',
            'Bag-Group-Identifier': '',
            'BagIt-Profile-Identifier': 'https://raw.githubusercontent.com/APTrust/preservation-services/master/profiles/aptrust-v2.2.json',
            'Internal-Sender-Description': '',
            'Internal-Sender-Identifier': '',
            'Source-Organization': 'University of Alabama at Birmingham'
            }
        for f in listdir(bagsdir):
            inpath = path.join(bagsdir, f)
            cont = True
            if path.isdir(inpath):
                if path.exists(path.join(inpath, 'data')):
                    cont = messagebox.askyesno(message="It appears that \'%s\' is already a bag.\nBag it anyway?" % f)
                if cont == True:
                    # Section to create the necessary APTrust Info file
                    APT_info_path = path.join(inpath, 'aptrust-info.txt')
                    with open(APT_info_path, 'w') as APT_info:
                        APT_info.write(f'Access: Institution\nDescription: University of Alabama at Birmingham\nStorage-Option: Standard\nTitle: {f.split(".")[0]}\n')
                    newbag = bagit.make_bag(inpath, APT_bag_info, checksums=['md5', 'sha256'])
                    totalbags += 1
                    if newbag.is_valid():
                        validbags += 1
                    elif not newbag.is_valid():
                        messagebox.showwarning(message="Bag \'%s\' is not a valid bag." % f)
                # elif cont == False:
                #     messagebox.showwarning(message="Skipped bagging of \'%s\'." %f)
        if not moreopts4 == 0:
            if self.prompting == 0:
                runnext4 = True
            else:
                runnext4 = messagebox.askyesno(
                    message="Created %d total bags,\nof which %d are valid.\n\nProceed with the next action?" % (
                        totalbags, validbags))
        else:
            runnext4 = False
            messagebox.showwarning(message="Created %d total bags,\nof which %d are valid." % (totalbags, validbags))
        return runnext4

    def run_tar(self, tarfolder, procfolder, moreopts5):
        """ Tars all objects in a single directory """
        tarfiles = 0
        alreadytar = 0
        notfolder = 0
        outfolder = path.join(procfolder, 'ready_to_transfer')
        if not path.exists(outfolder):
            mkdir(outfolder)
        for i in listdir(tarfolder):
            infile = path.join(tarfolder, i)
            if path.isdir(infile):
                outfile = path.join(outfolder, f'{path.splitext(i)[0]}.tar.gz')
                if path.exists(outfile):
                    messagebox.showwarning(
                        message=f'The TAR file: {outfile}\nalready exists!\nTar archive not created.')
                    alreadytar += 1
                elif not path.exists(outfile):
                    with tarfile.open(outfile, 'w:gz') as newtar:
                        tarname = path.relpath(infile, tarfolder)
                        newtar.add(infile, arcname='%s' % tarname)
                    tarfiles += 1
            else:
                notfolder += 1
        if not alreadytar == 0:
            messagebox.showwarning(message=f'The folder {outfolder} already contained {alreadytar} tar files which were skipped.')
        # if not notfolder == 0:
        #    messagebox.showinfo(message="The target folder contained %d files, which were ignored." %notfolder)
        if not moreopts5 == 0:
            if self.prompting == 0:
                runnext5 = True
            else:
                runnext5 = messagebox.askyesno(
                    message=f'Created {tarfiles} tar archives.\n\nProceed with the next action?')
        else:
            runnext5 = False
            messagebox.showwarning(message=f'Created {tarfiles} tar archives.')
        return runnext5

    def trans_manifest(self, indirectory, procdirectory):
        """
        Generates a manifest of filenames and checksums for a directory of
        Bagged and Tarred objects
        """
        if path.isdir(procdirectory):
            process_dir = procdirectory
        else:
            process_dir = askdirectory(initialdir=self.user_home())
        askingdir = path.join(process_dir, 'ready_to_transfer')
        indir = ""
        tardest = messagebox.askyesno(message=f'Create manifest of {askingdir}?', default='yes')
        if tardest:
            indir = askingdir
        elif not tardest:
            indir = askdirectory(initialdir=process_dir,
                                 title="In which folder are the objects to be transferred?")
        outdir = path.join(process_dir, 'transfer_manifests')
        if not path.exists(outdir):
            mkdir(outdir)
        tar_list = open(path.join(outdir, f'transfer_{time.strftime("%Y%b%d_%H%M%S")}.csv'),
                        'w', encoding='utf-8')
        sorted_tarlist = sorted([t for t in listdir(indir) if '.tar' in t])
        for tars in sorted_tarlist:
            tar_path = path.join(indir, tars)
            md5sum = self.md5hash(tar_path)
            sha256sum = self.sha256hash(tar_path)
            # sha3sum = self.sha3hash(tar_path)
            tar_list.write(f'{tars},{md5sum},{sha256sum}\n')
        tar_list.close()
        if self.prompting == 1:
            messagebox.showinfo(message=f'Transfer Manifest Created\nfor {len(sorted_tarlist)} Tar Files')
        return

    def run_procs(self, root, frame2):
        runnext = True
        itemsdir = self.e1.get()
        procdir = self.e2.get()
        pre = frame2.prebagvar.get()
        meta = frame2.metavar.get()
        inv = frame2.invenvar.get()
        bagit = frame2.bagitvar.get()
        tar = frame2.tarvar.get()
        trans = frame2.transvar.get()
        self.prompting = frame2.prompt.get()
        nselect = 0
        for d in [pre, meta, inv, bagit, tar, trans]:
            if d == 1:
                nselect += 1
        if trans == 1 and not nselect == 1:
            if itemsdir == "":
                messagebox.showwarning(message="You must first select a folder.")
                return
            if not path.exists(itemsdir):
                messagebox.showwarning(message="Items folder:\n\'%s\'\nnot found." % olditemsdir)
                return
        if nselect == 0:
            messagebox.showwarning(message="You have not selected any \'Options\'.")
            return
        # PreBag items
        if pre == 1:
            nselect -= 1
            runnext = self.pre_bag(root, itemsdir, nselect)
            if runnext == False:
                return
        # Run CSV meta
        if meta == 1:
            nselect -= 1
            metainput = self.e3.get()
            idcolumn = self.e4.get()
            if metainput == "":
                messagebox.showwarning(message="You must choose a CSV master metadata file.")
                return
            if not path.exists(metainput):
                messagebox.showwarning(message="CSV file:\n\'%s\'\nnot found. Stopping action." % metainput)
                return
            if path.splitext(metainput)[1] == '.csv' and idcolumn == "":
                messagebox.showwarning(message="You must choose the column of ID's in the CSV.")
                return
            runnext = self.create_meta(itemsdir, metainput, idcolumn, nselect)
            if runnext == False:
                return
        # Run Inventory
        if inv == 1:
            nselect -= 1
            runnext = self.run_inventory(itemsdir, nselect)
            if runnext == False:
                return
        # Run BagIt
        if bagit == 1:
            nselect -= 1
            self.run_bagit(itemsdir, nselect)
            if runnext == False:
                return
        # Run Tar
        if tar == 1:
            nselect -= 1
            runnext = self.run_tar(itemsdir, procdir, nselect)
            if runnext == False:
                return
        # Make Transfer Manifest
        if trans == 1:
            self.trans_manifest(itemsdir, procdir)
        messagebox.showinfo(message='Done!')
        root.quit()

def instructions(fontsize):
    new = Toplevel()
    nw = 850
    nh = 600
    nws = new.winfo_screenwidth()  # width of the screen
    nhs = new.winfo_screenheight()  # height of the screen
    nx = (nws / 2) - (nw / 2)
    ny = (nhs / 2) - (nh / 2)
    new.geometry('%dx%d+%d+%d' % (nw, nh, nx, ny))
    new.title('SIPmaker Instructions')
    new.configure(bg=uabgreen, pady=5, padx=5)
    new.grid_propagate(False)
    new.grid_rowconfigure(0, weight=1)
    new.grid_columnconfigure(0, weight=1)
    txt = Text(new, relief='sunken', bd=4, fg='black', bg=smoke)
    txt.config(pady=10, padx=40, font=('Times', fontsize), wrap='word')
    txt.grid(column=0, row=0, sticky='nsew')
    scroller = Scrollbar(new, orient='vertical', command=txt.yview)
    scroller.grid(column=1, row=0, sticky='nsew')
    txt['yscrollcommand'] = scroller.set
    OKa = Button(new, command=new.destroy, text='OK')
    OKa.configure(bg=smoke, bd=4, fg='black', font=('Arial', fontsize), highlightbackground=uabgreen,
                  relief='raised')
    OKa.grid(column=0, row=1, sticky='nsew')
    instructtext = resource_path("SIPmakerInstructions.txt")
    if path.exists(instructtext):
        with open(instructtext) as inst:
            quote = inst.read()
            txt.insert('end', quote)
    else:
        pathstring = str(instructtext)
        messagebox.showwarning(message="Cannot find the file:\n\'%s\'." % pathstring)


def main():
    root = tk.Tk()
    w = 705
    h = 515
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.title('SIPmaker Digital Object Formatter')
    root.configure(bg=blazegold, bd=4)
    # Run main app
    app = ObjFormatter(root)
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.mainloop()


if __name__ == '__main__':
    main()
