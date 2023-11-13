#!/usr/bin/env python
"""
Script for unpacking ETD's from ProQuest
Input is a folder containing one or more ETD Zips
Output is an Excel spreadsheet for batch upload to Digital Commons

Last modified by L. I. Menzies 2023-11-08
"""

import lxml, openpyxl, zipfile
import tkinter as tk
from bs4 import BeautifulSoup
from os import getcwd, getenv, listdir, mkdir, path, remove
from pandas import DataFrame, ExcelWriter, ExcelFile
from re import compile
from platform import system
from shutil import copyfile, rmtree
from time import strftime
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
        labl000 = Label(frame001, text='ETD_dcom_loader')
        labl000.configure(fg='black', bg=gray, bd=0, font=('Arial', 10), height=3, width=20, relief=SUNKEN, justify=CENTER)
        labl000.grid(column=1, row=0, pady=5, padx=5, sticky=NSEW)
        #
        in_folder = StringVar(frame001)
        labl001 = Label(frame001, text='Folder\nof Zips:')
        labl001.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl001.grid(column=0, row=2, pady=5, padx=5, sticky=E)
        self.en001 = Entry(frame001, width=45, textvariable=in_folder)
        self.en001.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en001.grid(column=1, row=2, pady=5, padx=0, sticky=W)
        browse1 = Button(frame001, text='Browse', command=lambda: self.ask_folder(in_folder))
        browse1.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse1.grid(column=2, row=2, pady=5, padx=5, sticky=W)
        #
        procfol = StringVar(frame001)
        labl002 = Label(frame001, text='Folder for\nExcel Files:')
        labl002.configure(fg='black', bg=blazegold, highlightbackground='black', bd=4, font=('Arial', 10), height=2, width=9, justify=CENTER)
        labl002.grid(column=0, row=3, pady=5, padx=5, sticky=E)
        self.en002 = Entry(frame001, width=45, textvariable=procfol)
        self.en002.configure(bg=gray, fg='black', relief=SUNKEN, bd=2, font=('Arial', 14), justify=LEFT)
        self.en002.grid(column=1, row=3, pady=5, padx=0, sticky=W)
        browse2 = Button(frame001, text='Browse', command=lambda: self.ask_folder(procfol))
        browse2.configure(bd=4, bg=smoke, highlightbackground='black', font=('Arial', 10))
        browse2.grid(column=2, row=3, pady=5, padx=5, sticky=W)
        #
        self.frame002 = Frame(root)
        self.extractvar = IntVar(self.frame002)
        collate_chk = Checkbutton(self.frame002, text='Extract Zips', variable=self.extractvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        collate_chk.grid(column=2, row=0, pady=5, padx=5)
        self.extractvar.set(1)
        #
        self.excelvar = IntVar(self.frame002)
        csv_chk = Checkbutton(self.frame002, text='Generate\nExcel Loader', variable=self.excelvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        csv_chk.grid(column=3, row=0, pady=5, padx=5)
        self.excelvar.set(1)
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        #
        frame001.configure(bg=uabgreen, highlightbackground='black', bd=5, relief=RAISED)
        frame001.grid(column=0, row=0, pady=0, padx=0, sticky=NSEW)
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
        docsdir = path.join(self.user_home(), 'Documents')
        foname.set(askdirectory(initialdir=docsdir, title='Select the Folder'))
        return foname

    def get_entries(self):
        entries = ['unknown', 'unknown']
        entries[0] = self.en001.get() # Path to the folder of ProQuest Zips
        entries[1] = self.en002.get() # Path to the output folder for Excel files
        return entries

    def get_meta_from_xml(self, xml_path, new_row):
        # Columns with blank values are included here, albeit commented out
        # These can be un-commented, if desired, in the future
        # Note: the use of 'or ""' in the variable assignments below is to avoid
        # assigning 'NoneType' to any of the variables, which throws an error.
        # (For example, if there is no "suffix")
        print(xml_path)
        with open(xml_path, 'r', encoding='utf-8') as xml_file:
            soup = BeautifulSoup(xml_file, features='xml')
            new_row['title'] = soup.DISS_title.string or ""
            # new_row['fulltext_url'] = ''
            new_row['filename'] = path.basename(xml_path).replace("_DATA.xml", ".pdf")
            new_row['keywords'] = soup.DISS_keyword.string or ""
            new_row['abstract'] = soup.DISS_abstract.string or ""
            new_row['author1_fname'] = soup.DISS_author.DISS_fname.string or ""
            new_row['author1_mname'] = soup.DISS_author.DISS_middle.string or ""
            new_row['author1_lname'] = soup.DISS_author.DISS_surname.string or ""
            try:
                new_row['author1_suffix'] = soup.DISS_author.DISS_suffix.string
            except:
                new_row['author1_suffix'] = ""
            # new_row['author1_email'] = ''
            new_row['author1_institution'] = soup.DISS_institution.DISS_inst_name.string or ""
            adv1_fname = soup.DISS_advisor.DISS_fname.string or ""
            adv1_mname = soup.DISS_advisor.DISS_middle.string or ""
            adv1_sname = soup.DISS_advisor.DISS_surname.string or ""
            try:
                adv1_sx = soup.DISS_advisor.DISS_suffix.string
            except:
                adv1_sx = ""
            adv1_name = f'{adv1_fname} {adv1_mname} {adv1_sname} {adv1_sx}'
            new_row['advisor1'] = adv1_name.strip()
            cmte_members = ['', '', '', '', '']
            index = 0
            for tag in soup.find_all('DISS_cmte_member'):
                cmte_fname = tag.DISS_fname.string or ""
                cmte_mname = tag.DISS_middle.string or ""
                cmte_sname = tag.DISS_surname.string or ""
                try:
                    cmte_sx = tag.DISS_suffix.string
                except:
                    cmte_sx = ""
                cmte_name = f'{cmte_fname} {cmte_mname} {cmte_sname} {cmte_sx}'
                cmte_members[index] = cmte_name.strip()
                index += 1
            new_row['advisor2'] = cmte_members[0]
            new_row['advisor3'] = cmte_members[1]
            new_row['advisor4'] = cmte_members[2]
            new_row['advisor5'] = cmte_members[3]
            new_row['advisor6'] = cmte_members[4]
            # new_row['disciplines'] = ''
            # new_row['comments'] = ''
            new_row['document_type'] = soup.DISS_processing_code.string or ""
            # new_row['doi'] = ''
            try:
                new_row['embargo_date'] = soup.DISS_sales_restriction.get('remove')
            except AttributeError:
                new_row['embargo_date'] = ''
            # new_row['isbn'] = ''
            new_row['publication_date'] = soup.DISS_comp_date.string or ""
            # new_row['season'] = ''
            # new_row['pubmedid'] = ''
            new_row['subject_area'] = f'{soup.DISS_degree.string.replace(".", "").strip()} '\
                                    + f'\+ {soup.DISS_inst_contact.string}'
            # new_row['uuid'] = ''
        return new_row

    def make_excel(self, etds_dir):
        entries = self.get_entries()
        excel_folder = entries[1]
        timestamp = strftime("%Y%b%d_%H%M%S")
        excel_file = path.join(excel_folder, f'ETD_loader{timestamp}.xlsx')
        excel_writer = ExcelWriter(excel_file)
        etds_found = 0
        etds_added = 0
        xml_paths = []
        all_rows = []
        # Create a dictionary for each row
        header_row = ['title', 'fulltext_url', 'filename', 'keywords', 'abstract',
                'author1_fname', 'author1_mname', 'author1_lname', 'author1_suffix',
                'author1_email', 'author1_institution', 'advisor1', 'advisor2',
                'advisor3', 'advisor4', 'advisor5', 'advisor6', 'disciplines',
                'comments', 'document_type', 'doi', 'embargo_date', 'isbn',
                'publication_date', 'season', 'pubmedid', 'subject_area', 'uuid']
        row_dict = dict()
        for element in header_row:
            row_dict[element] = ''
        # Add paths of XML files to a list:
        for etd in listdir(etds_dir):
            etd_path = path.join(etds_dir, etd)
            if path.isdir(etd_path):
                for xml_file in listdir(etd_path):
                    if path.splitext(xml_file)[1].lower() == '.xml':
                        etds_found += 1
                        xml_path = path.join(etd_path, xml_file)
                        xml_paths.append(xml_path)
        for mdata_path in xml_paths:
            next_row = self.get_meta_from_xml(mdata_path, row_dict)
            all_rows.append(next_row)
        data_frame = DataFrame(all_rows)
        data_frame.to_excel(excel_writer, 'Sheet1', index=False)
        excel_writer.close()
        return True

    def unzip_ETDs(self):
        info = self.get_entries()
        zips_folder = info[0]
        datetime = strftime("%Y%b%d_%H%M%S")
        unzip_folder = path.join(path.dirname(zips_folder), f'ETDs_unzipped{datetime}')
        try:
            mkdir(unzip_folder)
        except FileExistsError:
            messagebox.showwarning(message='The output folder already exists!\n\nQuitting.')
            root.quit()
        else:
            unzip_fold = unzip_folder
        zips = 0
        unzips = 0
        for z in listdir(zips_folder):
            zip_path = path.join(zips_folder, z)
            if not path.isdir(zip_path):
                if path.splitext(z)[1].lower() == '.zip':
                    zips += 1
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as ex_zip:
                            ex_zip.extractall(unzip_folder)
                    except Exception as e:
                        messagebox.showwarning(message=f'There was an error extracting:\n{z}\nError = {e.message}\n\nSkipping...')
                    else:
                        unzips += 1
        messagebox.showinfo(message=f'Found {zips} zipfiles and\nunzipped {unzips} files.')
        return True, unzip_fold

    def run_procs(self):
        successful = False
        unzip_yesno = self.extractvar.get()
        excel_yesno = self.excelvar.get()
        dirs = self.get_entries()
        unzip_dir = dirs[0]
        if unzip_yesno == 1:
            successful, unzip_dir = self.unzip_ETDs()
            if successful == False:
                messagebox.showwarning(mesage=f'Something went wrong during\nunzipping. Quitting.')
                root.quit()
        if excel_yesno == 1:
            successful = self.make_excel(unzip_dir)
            if successful == False:
                messagebox.showwarning(message=f'Something went wrong during\nExcel generation. Quitting')
                root.quit()
        if successful == False:
            messagebox.showwarning(message=f'One or more processes were not successful.\nQuitting')
            root.quit()
        else:
            messagebox.showinfo(message=f'Done!')
            root.quit()


root = tk.Tk()
w = 646
h = 298
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' %(w, h, x, y))
root.title('ETD_dcom_loader')
app = GetValues(root)
root.configure(bg=blazegold, bd=4)
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.mainloop()
