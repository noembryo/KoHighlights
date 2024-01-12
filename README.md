## General
![kohighlights128w](https://user-images.githubusercontent.com/24675403/234561476-97283ff8-5437-49cd-b4c5-3929886cf182.png)

[![made-with-python][Python]](https://www.python.org/)
[![Generic badge][OS]][ReleaseLink]
[![License: MIT][MIT]](LICENSE)
[![GitHub release][Release]][ReleaseLink]
<!-- [![Github all releases][TotalDown]][ReleaseLink] -->
<!-- [![Github Releases (by Release)][VersionDown]][ReleaseLink] -->


**KOHighlights** is a utility for viewing and exporting the
[Koreader](https://github.com/koreader/koreader)'s highlights to simple text, html, csv or markdown files.  
This is a totally re-written application using the Qt framework (PySide).  
The original KOHighlights (using the wxPython) can be found
[here](https://github.com/noonkey/KoHighlights), but is considered deprecated..


### Screenshots
<!-- ![HighLights ScreenShot](screen1.png) -->
<!-- ![HighLights ScreenShot](screen2.png) -->
<!-- ![HighLights ScreenShot](screen3.png) -->

<p align="center">
  <a href="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen1.png">
    <img src="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen1.png" height="180"></a>
  <a href="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen2.png">
    <img src="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen2.png" height="180"></a>
  <a href="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen3.png">
    <img src="https://raw.githubusercontent.com/noembryo/KoHighlights/master/screen3.png" height="180"></a>
</p>

## Usage
* Load items by:
    * Selecting the reader's drive or any folder that contains books that where opened with Koreader. This will automatically load all the metadata files from all subdirectories.
    * Drag and drop files or folders. This will load the files and/or all the files inside the folders.  
* Export the highlights of the selected books to individual files or to one merged file.
* Supported formats for exporting:
    * Plain text files (.txt)
    * Hypertext document files (.html)
    * Comma-separated values files (.csv)
    * Markdown files (.md)
* View the highlights and various info for a book by selecting it in the list.
* Save the highlights to the "Archive" and view them, even if your reader is not connected.
* Merge highlights/Sync position from the same book that is read in two different devices and/or sync its reading position. To do it you have to:
    * Load both metadata (e.g. by scanning your reader's _and_ your tablet's books).
    * Select the relevant rows of the (same) book.
    * If the book has the same cre_dom_version (version of the CREngine), then the "Merge/Sync" button gets activated and you get the options to sync the highlights or the position or both.
* Merge highlights/Sync position of a book with its archived version
  (book's right click menu) 
* Show/hide the page, date, chapter or even the highlight text while viewing or saving the highlights of the books. 
* Double click or press the Open Book button to view the book in your system's reader.
* Delete some or all the highlights of any book.
* Clear/reset the .sdr folders with the metadata or the books in the eReader.

### Prerequisites  
These plugins must be enabled in KOReader
* Progress sync plugin
* Reading statistics plugin

### Portable
In Windows, KOHighlights can run in Portable mode using a `portable_settings` directory to store its settings, that is located inside the installation directory of the app.  
Because of this, it is advised to not install the app inside the `Program Files` folder if you indent to use it as portable.  
There are two ways to start the app in Portable mode:
* Run the `KoHighlights Portable.exe` that is located next to the `KoHighlights.exe`.  
* Run `KoHighlights.exe` with a `-p` argument.  
E.g. create a shortcut for the `KoHighlights.exe` and add a space and a `-p` argument at the end of the target filename.

## Downloads
Check the latest release on the [Downloads Page][ReleaseLink].  
Read the version history at [App's Page](http://www.noembryo.com/apps.php?kohighlights).

## Dependencies
Should run in any system with Python 2.7.x or 3.x (more testing required)  
It needs the [PySide](https://pypi.org/project/PySide/),
[BeautifulSoup4](https://pypi.org/project/beautifulsoup4/),
[future](https://pypi.org/project/future/) and
[requests](https://pypi.org/project/requests/) libraries.  
In Linux the `libqt4-sql-sqlite` package must be installed.  

## Extra
KOHighlights includes SLPPU (a converter between python and lua objects).  
If you want it to be globally available, get it from its
[GitHub's page](https://github.com/noembryo/slppu) or install it with:  
`pip install git+https://github.com/noembryo/slppu`  


<!-- ##### Stargazers over time

[![Stargazers over time](https://starchart.cc/noembryo/KoHighlights.svg)](https://starchart.cc/noembryo/KoHighlights) -->

[Release]:https://img.shields.io/github/release/noembryo/KoHighlights.svg
[ReleaseLink]:https://GitHub.com/noembryo/KoHighlights/releases/
[TotalDown]:https://img.shields.io/github/downloads/noembryo/KoHighlights/total.svg
[VersionDown]:https://img.shields.io/github/downloads/noembryo/KoHighlights/v1.2.2.0/total.svg
[Python]:https://img.shields.io/badge/Made%20with-Python-1f425f.svg
[OS]:https://img.shields.io/badge/OS-Windows&nbsp;/&nbsp;Linux-darkgreen.svg
[MIT]:https://img.shields.io/badge/License-MIT-green.svg
