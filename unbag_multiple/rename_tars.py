#!/usr/bin/env python3
# Script to rename old tar.gz files

from os import listdir, path, rename

stop = False
count = 0
while not stop:
    print(f'Please enter the path to the folder of TARs to be renamed.')
    tars_dir = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(tars_sdir):
        stop = True
        print(f'Renaming the items in:\n    {tars_dir}')
    else:
        print(f'Incorrect path.\n')
        stop = False
for t in listdir(tars_dir):
    oldpath = path.join(tars_dir, t)
    if path.isfile(oldpath):
        newpath = path.join(tars_dir, f'{t.split(".")[0]}_old.tar.gz')
        rename(oldpath, newpath)
        count += 1
print(f'renamed {count} files')
