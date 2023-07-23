# miyoo-mini
Random collection for the Miyoo Mini/Plus

## Firmware scripts
Two scripts, in Python and Powershell, to be used to extract miyoo283/354_fw.img files

One script to edit a miyoo***_fw.img firmware file.

It carves out and unpacks the 3 squashfs partitions, and then waits and lets you edit the files.
Then it repacks the partitions and surgically places them back into the miyoo***_fw.img file

It creates a backup of the firmware file.
