#!/usr/bin/env python
# Script to un-bag a folder of Bags
# Simply deletes all Bag-specific files and moves the payload up one folder


from os import listdir, mkdir, path, remove, rename
from shutil import move, rmtree

def unbag_dnd_bags(bagdir, bagslist):
    itemcount = 0
    bagcount = 0
    del_files = ['bag-info.txt', 'bagit.txt', 'manifest-md5.txt', 'manifest-sha256.txt',
                'manifest-sha512.txt', 'tagmanifest-md5.txt', 'tagmanifest-sha256.txt',
                'tagmanifest-sha512.txt', 'metadata.csv', 'manifest.csv', 'metadata.xml',
                'metadata.json']
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
    print(f'Please enter the path to the folder of Bags to be un-Bagged.')
    bagsdir = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(bagsdir):
        stop = True
        print(f'Un-Bagging the items in:\n    {bagsdir}')
    else:
        print(f'Incorrect path.\n')
        stop = False
baglist = [i for i in listdir(bagsdir) if len(i.split('.')) == 1]
dnd_bags = False
yesno = input('Are these bags in the DnD format? ').strip()
if yesno in ['Y', 'y', 'Yes', 'yes', '']:
    dnd_bags = True
else:
    dnd_bags = False
if dnd_bags == True:
    numbers = unbag_dnd_bags(bagsdir, baglist)
else:
    numbers = unbag_normal_bags(bagsdir, baglist)
print(f'\nFound {numbers[0]} folders.\nUnbagged {numbers[1]} bags.\n')
