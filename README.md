# General
![kohighlights128w](https://cloud.githubusercontent.com/assets/14363074/9978678/22e01940-5f49-11e5-8112-bc58b8f0f56f.png)

**KoHighlights** is a utility for viewing and converting the [Koreader](https://github.com/koreader/koreader)'s history files to simple text.  
This is a totally re-written application using the Qt framework (PySide).  
The original KoHighlights (using the wxPython) can be found [here](https://github.com/noonkey/KoHighlights), but is considered deprecated..


![HighLights ScreenShot 02](screen2.png)

# Usage
* Load items by:
    * Selecting the reader's drive or any folder that contains books that where opened with Koreader. This will automatically load all the metadata files from all subdirectories.
    * Drag and drop files or folders. This will load the files and/or all the files inside the folders.
* View the highlights and various info for a book by selecting it in the list.
* Show/hide the page, date or even the highlight text while viewing or saving the highlights of the books. 
* Double click or press the Open Book button to view the book in your system's reader.
* Save all the selected books' highlights:
    * A text file for every selected book or
    * A single text file with all highlights combined
* Delete some or all the highlights of any book.
* Clear the .sdr folders with the metadata or the books in the eReader.

# Downloads
Check the latest release on the [Downloads Page](https://github.com/noembryo/KoHighlights/releases).  
Read the version history at [App's Page](http://www.noembryo.com/apps.php?kohighlights).

# Extra
KoHighlights includes SLPPU (a converter between python and lua objects).  
If you want it globally available, get it from its [GitHub's page](https://github.com/noembryo/slppu) or install it with:  
`pip install git+https://github.com/noembryo/slppu`  
