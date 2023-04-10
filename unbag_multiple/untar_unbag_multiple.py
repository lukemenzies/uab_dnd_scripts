#!/usr/bin/env python
# Script to un-tar, unzip, and un-bag a folder of Bags
# Un-tar runs equivalent of tar -xzvf
# Simply deletes all Bag-specific files and moves the payload up one folder
# Last updated 2023-04-05 by L. I. Menzies

import tarfile
from os import listdir, mkdir, path, remove, rename
from shutil import move, rmtree

def untar_targz(tarsdir, tarslist):
    counting = 0
    errs = 0
    extractok = True
    for tar in tarslist:
        tarpath = path.join(tarsdir, tar)
        ex_dir = path.join(tarsdir, tar.split('.')[0])
        if 'gz' in tar:
            rmode = 'r:gz'
        else:
            rmode = 'r'
        try:
            with tarfile.open(tarpath, rmode) as xtar:
                xtar.extractall(path=ex_dir, numeric_owner=False)
        except Exception as e:
            errs += 1
            extractok = False
            print(f'There was an error extracting {tar}')
            print(f'ERROR MESSAGE:\n{e}')
        else:
            counting += 1
            # move tar contents up a level
            for c in listdir(ex_dir):
                itempath = path.join(ex_dir, c)
                temppath = path.join(tarsdir, c + 't')
                newpath = path.join(tarsdir, c)
                move(itempath, temppath)
                rmtree(ex_dir)
                rename(temppath, newpath)
            print(f'Extracted {tar} to {tarsdir}\n')
            # remove(tarpath)
    print(f'Extracted contents of {counting} tar files with {errs} extraction errors.\n')
    return extractok

def unbag_dnd_bags(bagdir, bagslist):
    itemcount = 0
    bagcount = 0
    del_files = ['bag-info.txt', 'bagit.txt', 'aptrust-info.txt', 'manifest-md5.txt',
                'manifest-sha256.txt', 'manifest-sha512.txt', 'tagmanifest-md5.txt',
                'tagmanifest-sha256.txt', 'tagmanifest-sha512.txt', 'metadata.csv',
                'manifest.csv', 'metadata.xml', 'metadata.json']
    for b in bagslist:
        itemcount += 1
        bagpath = path.join(bagdir, b)
        datapath = path.join(bagpath, 'data')
        itempath = path.join(datapath, b)
        temppath = path.join(bagdir, f'temp{itemcount}')
        if path.exists(datapath):
            bagcount += 1
            # delete bagit files
            for f in listdir(bagpath):
                fpath = path.join(bagpath, f)
                if f in del_files:
                    remove(fpath)
            # delete metadata files
            for m in listdir(datapath):
                mpath = path.join(datapath, m)
                if m in del_files:
                    remove(mpath)
            # move 'payload' up to original file structure
            move(itempath, temppath)
            rmtree(bagpath)
            rename(temppath, bagpath)
        nums = [itemcount, bagcount]
    return nums

def unbag_normal_bags(bagdir, bagslist):
    itemcount = 0
    bagcount = 0
    del_files = ['bag-info.txt', 'bagit.txt', 'manifest-md5.txt', 'manifest-sha256.txt',
                'manifest-sha512.txt', 'tagmanifest-md5.txt', 'tagmanifest-sha256.txt',
                'tagmanifest-sha512.txt']
    for b in bagslist:
        itemcount += 1
        bagpath = path.join(bagdir, b)
        datapath = path.join(bagpath, 'data')
        temppath = path.join(bagdir, f'temp{itemcount}')
        if path.exists(datapath):
            bagcount += 1
            # delete bagit files
            for f in listdir(bagpath):
                fpath = path.join(bagpath, f)
                if f in del_files:
                    remove(fpath)
            # move 'payload' up to original file structure
            move(datapath, temppath)
            rmtree(bagpath)
            rename(temppath, bagpath)
        nums = [itemcount, bagcount]
    return nums

# Main
stop = False
while not stop:
    print(f'Please enter the path to the folder of TARs and Bags.')
    bagsdir = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(bagsdir):
        stop = True
        print(f'Un-tarring and Un-Bagging the items in:\n    {bagsdir}')
    else:
        print(f'Incorrect path.\n')
        stop = False
dnd_bags = False
yesno = input('Are the bagged items in the DnD format? ').strip()
if yesno in ['Y', 'y', 'Yes', 'yes', '']:
    dnd_bags = True
else:
    dnd_bags = False
tarlist = [t for t in listdir(bagsdir) if tarfile.is_tarfile(path.join(bagsdir, t))]
success = False
success = untar_targz(bagsdir, tarlist)
if not success:
    print(f'Tar extraction failed.\nQuitting.')
    exit()
baglist = [i for i in listdir(bagsdir) if len(i.split('.')) == 1]
if dnd_bags == True:
    numbers = unbag_dnd_bags(bagsdir, baglist)
else:
    numbers = unbag_normal_bags(bagsdir, baglist)
print(f'\nFound {numbers[0]} folders.\nUnbagged {numbers[1]} bags.\n')
