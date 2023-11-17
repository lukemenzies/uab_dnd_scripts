#!/usr/bin/env python
"""
Script for unpacking ETD's from ProQuest
Input is a folder containing one or more ETD Zips
Output is an Excel spreadsheet for batch upload to Digital Commons

Last modified by L. I. Menzies 2023-11-15
"""

import csv, lxml, openpyxl, zipfile
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
from tkinter.filedialog import askdirectory

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
        # Checkbutton to UnZip all
        self.frame002 = Frame(root)
        self.extractvar = IntVar(self.frame002)
        extract_chk = Checkbutton(self.frame002, text='Extract\nZips', variable=self.extractvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        extract_chk.grid(column=2, row=0, pady=5, padx=5)
        self.extractvar.set(1)
        # Checkbutton to Generate CSV
        self.csvvar = IntVar(self.frame002)
        excel_chk = Checkbutton(self.frame002, text='Generate\nCSV Log', variable=self.csvvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        excel_chk.grid(column=3, row=0, pady=5, padx=5)
        self.csvvar.set(1)
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        # Checkbutton to Copy PDF and XML files to separate batch folders
        self.copyvar = IntVar(self.frame002)
        copy_chk = Checkbutton(self.frame002, text='Copy PDF\n+ XML Files', variable=self.copyvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        copy_chk.grid(column=4, row=0, pady=5, padx=5)
        self.copyvar.set(1)
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        # Checkbutton to Generate Excel Loader
        self.excelvar = IntVar(self.frame002)
        excel_chk = Checkbutton(self.frame002, text='Generate\nExcel Loader', variable=self.excelvar, fg='black',
                                bg=smoke, relief='flat', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        excel_chk.grid(column=5, row=0, pady=5, padx=5)
        self.excelvar.set(1)
        self.frame002.configure(bg=dragongreen, highlightbackground='black', bd=5, relief=SUNKEN)
        self.frame002.grid(column=0, row=1, pady=0, padx=0, sticky=NSEW)
        # Checkbutton to Suppress "Success" Messages after Each Task
        self.suppressvar = IntVar(self.frame002)
        suppress_chk = Checkbutton(self.frame002, text='Suppress\nMessages', variable=self.suppressvar, fg='black',
                                bg=smoke, relief='sunken', highlightbackground=dragongreen, bd=4, font=('Arial', 10), justify='left')
        suppress_chk.grid(column=6, row=0, pady=5, padx=5)
        self.suppressvar.set(1)
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

    def get_meta_from_xml(self, xml_path):
        # Columns with blank values are included here, albeit commented out
        # These can be un-commented, if desired, in the future
        # Note: the use of 'or ""' in the variable assignments below is to avoid
        # assigning 'NoneType' to any of the variables, which throws an error.
        # (For example, if there is no "suffix")
        # with open(xml_path, 'r', encoding='ISO-8859-1') as xml_file:
        #     soup = BeautifulSoup(xml_file, features='xml')
        bad_yesno = False
        try:
            xml_file = open(xml_path, 'r', encoding='ISO-8859-1')
            soup = BeautifulSoup(xml_file, features='xml')
        except UnicodeDecodeError:
            messagebox.showwarning(message=f'The file {path.basename(xml_path)}\nhas different encoding than\nwhat was expected. Skipping it.')
            bad_yesno = True
        except:
            messagebox.showwarning(message=f'There was an unknown error processing\n{path.basename(xml_path)}. Skipping it.')
            bad_yesno = True
        else:
            new_row = []
            for n in range(29):
                new_row.append('')
            new_row[0] = soup.DISS_title.string or "" # title
            # new_row[1] = '' # fulltext_url
            new_row[2] = path.basename(xml_path).replace("_DATA.xml", ".pdf") # filename
            new_row[3] = soup.DISS_keyword.string or "" # keywords
            # Convert parts of the abstract from DISS_para tags into a single string
            paragraph = ''
            for ptag in soup.find_all('DISS_abstract'):
                paragraph += f'{ptag.DISS_para.string or ""} '
            new_row[4] = paragraph.strip() or "" # abstract
            new_row[5] = soup.DISS_author.DISS_fname.string or "" # author1_fname
            new_row[6] = soup.DISS_author.DISS_middle.string or "" # author1_mname
            new_row[7] = soup.DISS_author.DISS_surname.string or "" # author1_lname
            try:
                new_row[8] = soup.DISS_author.DISS_suffix.string # author1_suffix
                if new_row[8] == None:
                    new_row[8] = ""
                elif new_row[8] == 'None':
                    new_row[8] = ""
            except:
                new_row[8] = "" # author1_suffix
            # new_row[9] = '' # author1_email
            new_row[10] = soup.DISS_institution.DISS_inst_name.string or "" # author1_institution
            adv1_fname = soup.DISS_advisor.DISS_fname.string or ""
            adv1_mname = soup.DISS_advisor.DISS_middle.string or ""
            adv1_sname = soup.DISS_advisor.DISS_surname.string or ""
            try:
                adv1_sx = soup.DISS_advisor.DISS_suffix.string
            except:
                adv1_sx = ""
            adv1_name = f'{adv1_fname} {adv1_mname} {adv1_sname} {adv1_sx}'
            new_row[11] = adv1_name.strip() # advisor1
            cmte_members = ['', '', '', '', '', '']
            index = 0
            for tag in soup.find_all('DISS_cmte_member'):
                # Break if there are more than 6 committee members
                if index >= 6:
                    break
                cmte_fname = tag.DISS_fname.string or ""
                cmte_mname = tag.DISS_middle.string or ""
                cmte_sname = tag.DISS_surname.string or ""
                try:
                    cmte_sx = tag.DISS_suffix.string
                    if cmte_sx == None:
                        cmte_sx = ""
                    elif cmte_sx == 'None':
                        cmte_sx = ""
                except:
                    cmte_sx = ""
                cmte_name = f'{cmte_fname} {cmte_mname} {cmte_sname} {cmte_sx}'
                cmte_members[index] = cmte_name.strip()
                index += 1
            new_row[12] = cmte_members[0] # advisor2
            new_row[13] = cmte_members[1] # advisor3
            new_row[14] = cmte_members[2] # advisor4
            new_row[15] = cmte_members[3] # advisor5
            new_row[16] = cmte_members[4] # advisor6
            new_row[17] = cmte_members[5] # advisor7
            # new_row[18] = '' # disciplines
            # new_row[19] = '' # comments
            new_row[20] = soup.DISS_processing_code.string or "" # document_type
            # new_row[21] = '' # doi
            try:
                new_row[22] = soup.DISS_sales_restriction.get('remove') # embargo_date
            except AttributeError:
                new_row[22] = '' # embargo_date
            # new_row[23] = '' # isbn
            new_row[24] = soup.DISS_comp_date.string or "" # publication_date
            # new_row[25] = '' # season
            # new_row[26] = '' # pubmedid
            new_row[27] = f'{soup.DISS_degree.string.replace(".", "").strip()} '\
                                    + f'+ {soup.DISS_inst_contact.string}' # degree + dept.
            # new_row[28] = '' # uuid
            xml_file.close()
        return new_row, bad_yesno

    def make_excel(self, etds_dir, suppress):
        entries = self.get_entries()
        excel_folder = entries[1]
        timestamp = strftime("%Y%b%d_%H%M%S")
        excel_file = path.join(excel_folder, f'ETD_loader{timestamp}.xlsx')
        excel_writer = ExcelWriter(excel_file)
        etds_found = 0
        etds_added = 0
        xml_paths = []
        # Add paths of XML files to a list:
        for etd in listdir(etds_dir):
            etd_path = path.join(etds_dir, etd)
            if path.isdir(etd_path):
                for xml_file in listdir(etd_path):
                    if path.splitext(xml_file)[1].lower() == '.xml':
                        etds_found += 1
                        xml_path = path.join(etd_path, xml_file)
                        xml_paths.append(xml_path)
        # Create row of column headers and each subsequent row as a list
        all_rows = []
        header_row = ['title', 'fulltext_url', 'filename', 'keywords', 'abstract',
                'author1_fname', 'author1_mname', 'author1_lname', 'author1_suffix',
                'author1_email', 'author1_institution', 'advisor1', 'advisor2',
                'advisor3', 'advisor4', 'advisor5', 'advisor6', 'advisor7',
                'disciplines', 'comments', 'document_type', 'doi', 'embargo_date',
                'isbn', 'publication_date', 'season', 'pubmedid', 'subject_area', 'uuid']
        all_rows.append(header_row)
        skipped = 0
        for mdata_path in xml_paths:
            next_row, badfile = self.get_meta_from_xml(mdata_path)
            if not badfile:
                all_rows.append(next_row)
                etds_added += 1
            else:
                skipped += 1
        data_frame = DataFrame(all_rows)
        data_frame.to_excel(excel_writer, 'Sheet1', index=False)
        excel_writer.close()
        if skipped == 0:
            if not suppress == 1:
                messagebox.showinfo(message=f'Found {etds_found} XML files.\nCreated {etds_added} Excel rows.')
        else:
            if not suppress == 1:
                messagebox.showinfo(message=f'Found {etds_found} XML files.\nCreated {etds_added} Excel rows.\nSkipped {skipped} XML files.')
        return True

    def copy_files(self, etds_dir, suppress):
        pdf_found = 0
        xml_found = 0
        new = 0
        new_limit = 10
        # Define the destination folders "XMLs" and "PDFs"
        destdir = path.join(path.dirname(etds_dir), f'{path.basename(etds_dir)}-copies')
        while path.exists(destdir):
            new += 1
            if new >= new_limit:
                messagebox.showwarning(message=f'You already have 10 \"copies\" folders!\nDelete some of these before trying\nthis function again.')
                return False
            destdir = path.join(path.dirname(etds_dir), f'{path.basename(etds_dir)}-copies-{str(new)}')
        try:
            mkdir(destdir)
        except Exception as e:
            messagebox.showwarning(message=f'Error: {e}\nQuitting copy function.')
            return False
        dest_pdfs = path.join(destdir, 'PDFs')
        try:
            mkdir(dest_pdfs)
        except FileExistsError:
            rmtree(dest_pdfs)
            mkdir(dest_pdfs)
        except Exception as e:
            messagebox.showwarning(message=f'Error: {e}\nQuitting copy function.')
            return False
        dest_xmls = path.join(destdir, 'XMLs')
        try:
            mkdir(dest_xmls)
        except FileExistsError:
            rmtree(dest_xmls)
            mkdir(dest_xmls)
        except Exception as e:
            messagebox.showwarning(message=f'Error: {e}\nQuitting copy function.')
            return False
        for fols in listdir(etds_dir):
            fols_path = path.join(etds_dir, fols)
            if path.isdir(fols_path):
                for i in listdir(fols_path):
                    ipath = path.join(fols_path, i)
                    if not path.isdir(ipath):
                        if path.splitext(i)[1].lower() == '.pdf':
                            pdf_found += 1
                            src_path = ipath
                            dst_path = path.join(dest_pdfs, i)
                            copyfile(src_path, dst_path)
                        elif path.splitext(i)[1].lower() == '.xml':
                            xml_found += 1
                            src_path = ipath
                            dst_path = path.join(dest_xmls, i)
                            copyfile(src_path, dst_path)
        if not suppress == 1:
            messagebox.showinfo(message=f'Found and copied:\n{pdf_found} PDFs\n{xml_found} XMLs')
        return True

    def make_csv_log(self, unzipped_dir, suppress):
        op_sys = system()
        pdfs_found = 0
        number_rows = 0
        dtime = strftime("%Y%b%d_%H%M%S")
        csv_path = path.join(unzipped_dir, f'etds_log{dtime}.csv')
        if op_sys == 'Windows':
            with open(csv_path, 'w', newline='', encoding='UTF-8') as cfile:
                cwriter = csv.writer(cfile)
                for fol in listdir(unzipped_dir):
                    folpath = path.join(unzipped_dir, fol)
                    if path.isdir(folpath):
                        diss_filename = 'unknown'
                        extra = 0
                        for f in listdir(folpath):
                            fpath = path.join(folpath, f)
                            if path.splitext(f)[1].lower() == '.pdf':
                                diss_filename = f
                                pdfs_found += 1
                            elif path.isdir(fpath):
                                extra += 1
                        if not extra == 0:
                            additional = 'yes'
                        else:
                            additional = ''
                        row = [fol, diss_filename, additional]
                        cwriter.writerow(row)
                        number_rows += 1
        else:
            with open(csv_path, 'w', encoding='UTF-8') as cfile:
                cwriter = csv.writer(cfile)
                for fol in listdir(unzipped_dir):
                    folpath = path.join(unzipped_dir, fol)
                    if path.isdir(folpath):
                        diss_filename = 'unknown'
                        for f in listdir(folpath):
                            if path.splitext(f)[1].lower() == '.pdf':
                                diss_filename = f
                                pdfs_found += 1
                        row = [fol, diss_filename]
                        cwriter.writerow(row)
                        number_rows += 1
        if not suppress == 1:
            messagebox.showinfo(message=f'Found {pdfs_found} PDF files\nand created {number_rows} rows.')
        return True

    def unzip_ETDs(self, suppress):
        info = self.get_entries()
        zips_folder = info[0]
        datetime = strftime("%Y%b%d_%H%M%S")
        unzip_folder = path.join(path.dirname(zips_folder), f'{path.basename(zips_folder)}_unzipped{datetime}')
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
                    extract_dir = path.join(unzip_folder, path.splitext(z)[0])
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as ex_zip:
                            ex_zip.extractall(extract_dir)
                    except Exception as e:
                        messagebox.showwarning(message=f'There was an error extracting:\n{z}\nError = {e.message}\n\nSkipping...')
                    else:
                        unzips += 1
        if not suppress == 1:
            messagebox.showinfo(message=f'Found {zips} zipfiles and\nunzipped {unzips} files.')
        return True, unzip_fold

    def run_procs(self):
        successful = False
        unsuccessful = 0
        unzip_yesno = self.extractvar.get()
        csv_yesno = self.csvvar.get()
        copy_yesno = self.copyvar.get()
        excel_yesno = self.excelvar.get()
        suppress_yesno = self.suppressvar.get()
        dirs = self.get_entries()
        unzip_dir = dirs[0]
        if unzip_yesno == 1:
            successful, unzip_dir = self.unzip_ETDs(suppress_yesno)
            if successful == False:
                messagebox.showwarning(mesage=f'Something went wrong during\nunzipping. Quitting.')
                root.quit()
        if csv_yesno == 1:
            successful = self.make_csv_log(unzip_dir, suppress_yesno)
            if successful == False:
                messagebox.showwarning(mesage=f'Something went wrong during\nCSV logging. Moving on...')
                unsuccessful += 1
        if copy_yesno == 1:
            successful = self.copy_files(unzip_dir, suppress_yesno)
            if successful == False:
                messagebox.showwarning(mesage=f'Something went wrong during\ncopying. Moving on...')
                unsuccessful += 1
        if excel_yesno == 1:
            successful = self.make_excel(unzip_dir, suppress_yesno)
            if successful == False:
                messagebox.showwarning(message=f'Something went wrong during\nExcel generation. Quitting')
                root.quit()
        if not unsuccessful == 0:
            messagebox.showwarning(message=f'One or more processes were not successful.\nQuitting')
            root.quit()
        else:
            messagebox.showinfo(message=f'Done!')
            root.quit()


root = tk.Tk()
w = 676
h = 306
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
