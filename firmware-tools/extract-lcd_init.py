#!/usr/bin/env python3

import os
import sys
import time
import lzma
import bz2
import tarfile
from io import BytesIO

def main():
    start = time.time()
    if len(sys.argv) == 2:
        folder = sys.argv[1]
        if not os.path.isdir(folder):
            print("please provide a valid folder as argument")
            return
    else:
        folder = os.getcwd()

    print("Looking for .img files in ", folder)
    img_files = [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.endswith(".img")
    ]

    if not img_files:
        print("No .img files in ", folder)
        return

    print("Found .img files:", " ".join(img_files))
    print()
    processedCount = 0
    for file in img_files:
        processedCount += 1
        print("Processing ", file)
        dest_folder = os.path.dirname(file)
        script = b""

        # need to open as binary else it errors out
        with open(file, "rb") as f:
            for line in f:
                script += line
                if b"\x25" in line:  # x25 = %
                    break

        script = script.decode("utf-8")
        partitions = []
        offsets = []
        offsetsdecimal = []
        sizes = []
        sizesdecimal = []
        build = script.split("\n")[0].split(":")[1]
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

        with open(file, "rb") as f:
            rawfile = f.read()

        for i in range(len(partitions)):
            if partitions[i] == "kernel":
                print(
                    f'\tProcessing partition "{partitions[i]}" offset 0x{offsets[i]} size 0x{sizes[i]}'
                )
                output_bytes = rawfile[
                    offsetsdecimal[i] : offsetsdecimal[i] + sizesdecimal[i]
                ]

                xz_magic = b"\xFD\x37\x7A\x58\x5A\x00"
                bz_block_header = b"\x31\x41\x59\x26\x53\x59"
                print("\tsearching for xz magic bytes")
                start_index = output_bytes.find(xz_magic)
                if start_index != -1:
                    print("\txz magic bytes found at offset", start_index)
                    xz_data = output_bytes[start_index:]
                    print("\tdecompressing kernel")
                    decompressed_kernel = lzma.decompress(xz_data)
                    print("\tsearching for mangled BZ header")
                    start_index = decompressed_kernel.find(bz_block_header)
                    if start_index != -1:
                        print("\tmangled BZ header found at offset", start_index)
                        decompressed_kernel = decompressed_kernel[start_index - 4 :]
                        end_index = decompressed_kernel.find(
                            b"\x00\x00\x00\x00\x00\x00\x00\x00"
                        )
                        print("\tcutting off excess data")
                        decompressed_kernel = decompressed_kernel[:end_index]
                        print("\trepairing mangled BZ header")
                        decompressed_kernel = bytearray(decompressed_kernel)
                        decompressed_kernel[0] = 0x42  # B
                        decompressed_kernel[1] = 0x5A  # Z
                        decompressed_kernel = bytes(decompressed_kernel)

                        print(
                            "\tdecompressing lcd_init, size",
                            len(decompressed_kernel),
                            "bytes",
                        )
                        lcd_init = bz2.decompress(decompressed_kernel)

                        tar_bytes_io = BytesIO(lcd_init)
                        print("\tdecompressed lcd_init, size", len(lcd_init), "bytes")
                        output_path = os.path.join(dest_folder, f"lcd_init-{build}")
                        print("\twriting lcd_init to folder", output_path)
                        with tarfile.open(fileobj=tar_bytes_io) as tar:
                            tar.extractall(output_path)

                    else:
                        print("\tmangled BZ header not found")
                else:
                    print("\txz magic bytes not found")
        print()

    elapsedTime = time.time() - start
    print(
        f"All done! Processed {processedCount} {'file' if processedCount == 1 else 'files'} in {str(round(elapsedTime,2))} seconds."
    )


if __name__ == "__main__":
    main()
