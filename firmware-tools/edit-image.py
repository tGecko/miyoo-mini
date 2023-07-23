#!/usr/bin/env python3

import os
import re
import shutil
import sys

class Partition:
    def __init__(self, name=""):
        self.name = name


def main():
    if len(sys.argv) == 2:
        img_file = sys.argv[1]
        if not os.path.isfile(img_file):
            print(f"{img_file} is not a file")
            return
    else:	
        return

    print("Processing ", img_file)
    print(f"Copying {img_file} to {img_file}.bak\n")
    shutil.copyfile(img_file, f"{img_file}.bak")
    dest_folder = os.path.join(os.path.dirname(os.path.abspath(img_file)), "extracted")
    os.makedirs(dest_folder, exist_ok=True)
    script = b''

    #fetch whole file
    with open(img_file, 'rb') as f:
        rawfile = f.read()

    #extract u-boot script from file
    with open(img_file, 'rb') as f:
        for line in f:
            script += line
            if b'\x25' in line: # x25 = %
                break
    script = script.decode('utf-8')

    partitions = []

    # fetch partition information from script
    for part in script.split("#"):
        partition = None
        for line in part.split("\n"):
            if "set_config" in line:    # not a partition
                break
            if "File Partition:" in line:
                partition = Partition(line.split()[-1])
            elif "fatload mmc" in line:
                partition.size = int(line.split()[-2][2:], 16)      # second to last item, cut off 0x, convert to dec
                partition.offset = int(line.split()[-1][2:], 16)    # same but last item in line
        if partition is not None:
            partitions.append(partition)
    squashfs_partitions = "miservice|rootfs|customer"
    for partition in partitions:
        if not re.search(squashfs_partitions, partition.name):   # only squashfs partitions for now
            continue

        print(f"Processing partition {partition.name} offset {partition.offset} size {partition.size}")
        output_bytes = rawfile[partition.offset: partition.offset + partition.size]
        output_path = os.path.join(dest_folder, partition.name)
        with open(output_path, 'wb') as f:
            f.write(output_bytes)
        print(f"unsquashing {partition.name}")
        os.system(f"unsquashfs  -d {os.path.join(dest_folder,partition.name)}-part {os.path.join(dest_folder,partition.name)} > /dev/null")
        os.remove(output_path)

    input(f"\nYou can now modify the partitions in {dest_folder}\nPress ENTER when you're done, and the firmware file will be stitched together.\n")
    success = True
    for partition in partitions:
        if not re.search(squashfs_partitions, partition.name):   # only squashfs partitions for now
            continue
        print(f"Squashing {partition.name}")
        dest_path = os.path.join(dest_folder,partition.name)
        os.system(f"mksquashfs {os.path.join(dest_folder,partition.name)}-part {dest_path} -comp xz > /dev/null")
        shutil.rmtree(f"{os.path.join(dest_folder,partition.name)}-part")

        # check if not too big
        if os.path.getsize(dest_path) > partition.size:
            success = False
            print(f"{dest_path} too big - aborting. ")
            break
        
        print(f"output size {os.path.getsize(dest_path)} should be smaller than {partition.size}")

        # read in squashed partition
        with open(dest_path, 'rb') as f:
            partfile = f.read()
            f.close()

        print(f"Writing {partition.name} to {img_file}\n")
        with open(img_file, "r+b") as f:
            f.seek(partition.offset)
            f.write(partfile)
            f.close()

    print("Cleanup")
    shutil.rmtree(dest_folder)
    if success:
        print("\nAll done!")
    else:
        print("\nFailed! Please start over. Applying backup")
        shutil.copyfile(f"{img_file}.bak", img_file)

if __name__ == "__main__":
    main()