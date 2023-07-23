#!/usr/bin/env python3

import os
import re
import shutil
import sys
import time

def main():
	start = time.time()
	if len(sys.argv) == 2:
		folder = sys.argv[1]
		if not os.path.isdir(folder):
			print(f"{folder} is not a folder")
			return
	else:	
		folder = os.getcwd()
	
	print("Looking for .img files in ", folder)
	img_files = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.img')]

	if not img_files:
		print("No .img files in ", folder)
		return

	print("Found .img files:", ' '.join(img_files))
	print()
	processedCount = 0
	for file in img_files:
		processedCount += 1
		print("Processing ", file)
		dest_folder = os.path.join(os.path.dirname(file), "extracted")
		os.makedirs(dest_folder, exist_ok=True)
		leaf = os.path.basename(file)
		script = b''

		# need to open as binary else it errors out
		with open(file, 'rb') as f:
			for line in f:
				script += line
				if b'\x25' in line: # x25 = %
					break

		script = script.decode('utf-8')
		partitions = []
		offsets = []
		offsetsdecimal = []
		sizes = []
		sizesdecimal = []
		for part in script.split("#"):
			for line in part.split("\n"):
				if "File Partition:" in line and "set_config" not in line:
					partitions.append(line.split()[-1])
				if "fatload mmc" in line:
					size = line.split()[-2]
					sizes.append(size[2:])
					sizesdecimal.append(int(size[2:], 16))
					offset = line.split()[-1]
					offsets.append(offset[2:])
					offsetsdecimal.append(int(offset[2:], 16))

		with open(file, 'rb') as f:
			rawfile = f.read()

		for i in range(len(partitions)):
			print(f"\tProcessing partition {partitions[i]} offset 0x{offsets[i]} size 0x{sizes[i]}")
			output_bytes = rawfile[offsetsdecimal[i]: offsetsdecimal[i] + sizesdecimal[i]]
			output_path = os.path.join(dest_folder, f"{leaf.split('_')[0]}_{partitions[i]}")
			with open(output_path, 'wb') as f:
				f.write(output_bytes)
		print()
	elapsedTime = time.time() - start
	print(f"All done! Processed {processedCount} {'file' if processedCount == 1 else 'files'} in {str(round(elapsedTime,2))} seconds.")
if __name__ == "__main__":
	main()
