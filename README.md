# miyoo-mini
Random collection for the Miyoo Mini/Plus

## Firmware scripts
Multiple scripts to manipulate miyoo***_fw.img files.
Run from folder with .img or pass a folder containing .img files as argument.

### extract-lcd_init.py
Carves out the well hidden lcd_init from a given firmware image.

### edit-image.py
It carves out and unpacks the 3 squashfs partitions, and then waits and lets you edit the files.
Then it repacks the partitions and surgically places them back into the miyoo***_fw.img file

It creates a backup of the firmware file.
