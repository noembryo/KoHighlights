## General
![kohighlights128w](https://cloud.githubusercontent.com/assets/14363074/9978678/22e01940-5f49-11e5-8112-bc58b8f0f56f.png)


[![made-with-python][Python]](https://www.python.org/)
[![License: MIT][MIT]](https://opensource.org/licenses/MIT)
[![Github all releases][TotalDown]]([ReleaseLink])
[![GitHub release][Release]]([ReleaseLink])
<!-- [![Github Releases (by Release)][VersionDown]]([ReleaseLink]) -->


**KoHighlights** is a utility for viewing and converting the
[Koreader](https://github.com/koreader/koreader)'s history files to simple text or html files.  
This is a totally re-written application using the Qt framework (PySide).  
The original KoHighlights (using the wxPython) can be found
[here](https://github.com/noonkey/KoHighlights), but is considered deprecated..


![HighLights ScreenShot](screen1.png)
![HighLights ScreenShot](screen2.png)
![HighLights ScreenShot](screen3.png)

## Usage
* Load items by:
    * Selecting the reader's drive or any folder that contains books that where opened
      with Koreader. This will automatically load all the metadata files from all
      subdirectories.
    * Drag and drop files or folders. This will load the files and/or all the files
      inside the folders.
* View the highlights and various info for a book by selecting it in the list.
* Save the highlights to the "Archive" and view them, even if your reader is not connected.
* Merge highlights from the same book that is read in two different devices and/or sync
  its reading position. 
* Show/hide the page, date or even the highlight text while viewing or saving the
  highlights of the books. 
* Double click or press the Open Book button to view the book in your system's reader.
* Save all the selected books' highlights:
    * A text/html file for every selected book or
    * A single text/html file with all highlights combined
* Delete some or all the highlights of any book.
* Clear the .sdr folders with the metadata or the books in the eReader.

## Downloads
Check the latest release on the [Downloads Page](https://github.com/noembryo/KoHighlights/releases).  
Read the version history at [App's Page](http://www.noembryo.com/apps.php?kohighlights).

## Dependencies
Should run in any system with Python 2.7.x or 3.x (more testing required)  
It needs the [Pyside](https://pypi.org/project/PySide/),
[BeautifulSoup4](https://pypi.org/project/beautifulsoup4/),
[future](https://pypi.org/project/future/) and
[mechanize](https://pypi.org/project/mechanize/) libraries.  
In Linux the `libqt4-sql-sqlite` package must be installed.  

## Extra
KoHighlights includes SLPPU (a converter between python and lua objects).  
If you want it globally available, get it from its
[GitHub's page](https://github.com/noembryo/slppu) or install it with:  
`pip install git+https://github.com/noembryo/slppu`  


[Release]:https://img.shields.io/github/release/noembryo/KoHighlights.svg
[ReleseLink]:https://GitHub.com/noembryo/KoHighlights/releases/
[TotalDown]:https://img.shields.io/github/downloads/noembryo/KoHighlights/total.svg
[VersionDown]:https://img.shields.io/github/downloads/noembryo/KoHighlights/v1.0.0.0/total.svg
[Python]:https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[MIT]:https://img.shields.io/badge/License-MIT-blue.svg