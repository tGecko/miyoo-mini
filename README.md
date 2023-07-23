# miyoo-mini
Random collection for the Miyoo Mini/Plus

## Firmware extraction scripts
Two scripts, in Python and Powershell, to be used to extract miyoo283/354_fw.img files

The python script can take a directory as an argument, it will extract all the .img files found there, or in the current working directory, if no argument was passed

The PowerShells script looks at the current working directory, if it doesn't find any .img files, it shows a folder browser.

Both scripts will extract the files into the subdirectory "extracted"
