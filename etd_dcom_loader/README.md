# etd_dcom_loader
ETD Digital Commmons Loader Script

Script for unpacking ETD's from ProQuest
Input is a folder containing one or more ETD Zips
Output is an Excel spreadsheet for batch upload to Digital Commons

*To Run*
This script runs from the command line.
After you have downloaded the script:
1) Open cmd.exe and navigate to the etd_dcom_loader folder
  Type 'cd ' and then drag the folder from File Explorer
  Or Type 'cd ' and then type the path to the folder

2) The GUI asks for two paths. Use the "Browse" buttons to navigate to the
folders and enter their paths in the text entry boxes.

  "Folder of Zips" - This is the folder that contains the Zipped ETDs
  OR This is the folder that contains the UnZipped ETD folders

  "Folder for Excel Files" - This is the folder where the Excel files
  will be created.

  Suggestion: Create an ETD working folder in Documents. Within that folder
  create 2 folders, named "etd_zips" and "etd_loaders"

3) There (currently) 3 Checkbox Choices

"Extract Zips" - This unzips all files with the ".zip" extension in the
given "Folder of Zips". It extracts the contents to a folder labeled
"ETDs_unzippedYYYYmonthDD_HHMMSS"

"Generate CSV Log" - This looks for files with the ".pdf" extension in all
sub-folders of the UnZipped ETDs folder. Output is a CSV spreadsheet that
contains the filename of the PDF and the filename of the Zip file that
contained it.

"Generate Excel Loader" - This extracts predetermined fields from the XML
metadata files provided by ProQuest, which accompany each thesis or
dissertation, and feeds those fields into a pre-defined Excel spreadsheet.
