#!/usr/bin/env python3
# Script to rename old tar.gz files

from os import listdir, path, rename

stop = False
count = 0
while not stop:
    print(f'Please enter the path to the \"new_items\" directory.')
    new_items = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(new_items):
        stop = True
        print(f'Renaming the items in:\n    {new_items}')
    else:
        print(f'Incorrect path.\n')
        stop = False
for t in listdir(new_items):
    tars_dir = path.join(new_items, t)
    for i in listdir(tars_dir):
        oldpath = path.join(tars_dir, i)
        if path.isfile(oldpath):
            newpath = path.join(tars_dir, f'{t.split(".")[0]}_old.tar.gz')
            rename(oldpath, newpath)
            count += 1
print(f'renamed {count} files')
