#!/usr/bin/env python
# Quick Script to rearrange legacy a's and b's

import zipfile
from os import mkdir, path, listdir
from shutil import move, rmtree, make_archive

def move_as_bs(batchfolder):
    num_items = 0
    success_items = 0
    success = True
    for item_name in listdir(batchfolder):
        item_path = path.join(batchfolder, item_name)
        if path.isdir(item_path):
            num_items += 1
            old_a_folder = path.join(item_path, 'a')
            old_b_folder = path.join(item_path, 'b')
            new_a_folder = path.join(batchfolder, item_name + 'a')
            new_b_folder = path.join(batchfolder, item_name + 'b')
            try:
                mkdir(new_a_folder)
            except:
                print(f'There was an error creating {new_a_folder}.')
                success = False
            else:
                for atifs in listdir(old_a_folder):
                    if not atifs.startswith('.') and atifs.endswith('a.tif'):
                        old_a_tif_path = path.join(old_a_folder, atifs)
                        new_a_tif_path = path.join(new_a_folder, atifs)
                        try:
                            move(old_a_tif_path, new_a_tif_path)
                        except:
                            print(f'There was an error moving {atifs}.')
                            success = False
            try:
                mkdir(new_b_folder)
            except:
                print(f'There was an error creating {new_b_folder}.')
                success = False
            else:
                for btifs in listdir(old_b_folder):
                    if not btifs.startswith('.') and btifs.endswith('b.tif'):
                        old_b_tif_path = path.join(old_b_folder, btifs)
                        new_b_tif_path = path.join(new_b_folder, btifs)
                        try:
                            move(old_b_tif_path, new_b_tif_path)
                        except:
                            print(f'There was an error moving {btifs}.')
                            success = False
            if success:
                success_items += 1
                rmtree(item_path)
    return [num_items, success_items]

def zip_b_folders(batch_dir):
    num_bs = 0
    num_zips = 0
    for b_folder in listdir(batch_dir):
        b_folder_path = path.join(batch_dir, b_folder)
        # b_zip_path = path.join(batch_dir, b_folder + '.zip')
        if path.isdir(b_folder_path) and b_folder.endswith('b'):
            num_bs += 1
            try:
                make_archive(b_folder_path, 'zip', b_folder_path)
            except:
                print(f'There was an error zipping {b_folder}.')
            else:
                num_zips += 1
                rmtree(b_folder_path)
    return [num_bs, num_zips]


# Main
stop = False
while not stop:
    print(f'Please enter the path to batch folder in new_items.')
    batchdir = input(': ').replace('\"', ' ').replace('\'', ' ').strip()
    if path.isdir(batchdir):
        stop = True
    else:
        print(f'Incorrect path.\n')
        stop = False
items_no = move_as_bs(batchdir)
print(f'Found {items_no[0]} items and moved {items_no[1]} items successfully.')
zips_no = zip_b_folders(batchdir)
print(f'Found {zips_no[0]} b folders and zipped {zips_no[1]} b folders successfully.')
