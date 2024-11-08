# Overview
This directory aims to pre-process raw data of CPL to a text-table pair, in which "text" is a file of word string for each raw docx's content in a line and "table" is a json file to store the refined raw excel's content that can be processed by DL methods.

# Methods
Here are pre-process method for raw data to fit our projection.
Data can be download from xxx, which contains original judge documents download from Chinese Law Website and structured excel manually collected in pairs:
- Transform the old type of .doc to accessible .docx. Operation is recommended on Windows OS using win32com api to communicate with kwps.application or other application-level api, using doc2docx.py directly.
- Unify the format of all files' name to make it easy to enable them to be sorted and matched just by its name.
- Save .docx files to lines in "text" and .xlsx files to dict list in "table".