## User Guide

---
### Table of contents

* [Introduction](#introduction)
* [Sources, Views and Actions](#sources-views-and-actions)
  * [Main toolbar](#main-toolbar)
    * [A. Metadata sources](#a-metadata-sources)
    * [B. Views](#b-views)
    * [C. Action buttons](#c-action-buttons)
* [I. Books View](#i-books-view)
    * [Action buttons in a glance](#action-buttons-in-a-glance)
    * [Usage Info - Common Tasks](#usage-info---common-tasks)
      * [Scanning for Books](#scanning-for-books)
      * [Reviewing selected book information](#reviewing-selected-book-information)
      * [Editing the highlight's comment](#editing-the-highlights-comment)
      * [Deleting highlights](#deleting-highlights)
      * [Filtering content](#filtering-content)
      * [Viewing the book's epub](#viewing-the-books-epub)
      * [Deleting metadata or .epub files from connected devices](#deleting-metadata-or-epub-files-from-connected-devices)
      * [Clearing the book list](#clearing-the-book-list)
      * [Exporting highlights](#exporting-highlights)
      * [Using Custom Markdown Template](#using-custom-markdown-template)
* [II. Highlights View](#ii-highlights-view)
* [III. Sync Groups View](#iii-sync-groups-view)
    * [Sync Groups View elements](#sync-groups-view-elements)
    * [Functionality accessible via right-click menu](#functionality-accessible-via-right-click-menu)
    * [Creating a New (blank) Sync Group](#creating-a-new-blank-sync-group)
    * [Adding Books from connected devices to a Sync Group](#adding-books-from-connected-devices-to-a-sync-group)
    * [Specifying sync options for the sync group](#specifying-sync-options-for-the-sync-group)
    * [Syncing All Active Groups](#syncing-all-active-groups)
    * [Deactivating or Activating a Sync Group](#deactivating-or-activating-a-sync-group)
    * [Syncing a Specific Group](#syncing-a-specific-group)
    * [Deleting a Sync Group](#deleting-a-sync-group)
    * [Troubleshooting Path Errors](#troubleshooting-path-errors)
    * [Replacing book metadata with Archived copy](#replacing-book-metadata-with-archived-copy)
* [Advanced Features](#advanced-features)
    * [Database management](#database-management)
    * [MD5 Mismatch Correction](#md5-mismatch-correction)
    * [Exporting to markdown with collapsible TOC levels](#exporting-to-markdown-with-collapsible-toc-levels)
      * [KOReader user patch installation](#koreader-user-patch-installation)
___

### Introduction

[KOHighlights](https://github.com/noembryo/KoHighlights) **(KH)** is a powerful highlight manager, designed to work seamlessly with [KOReader](https://github.com/koreader/koreader), a popular open-source e-book reading software.  

KH provides a robust solution for viewing, editing, synchronizing, and exporting your KOReader highlights across multiple devices.  

It supports highlight synchronization and merging, enabling concurrent highlights of the same book on several KOReader devices such as e-ink readers, android phones, or linux desktops.  

Periodically, all devices would need to be connected to a PC running KH, at which time, the program will merge all highlights across the connected devices irrespective of the time they were created.  

Additionally, one can create an archived copy stored in KH's internal database as a backup or as a way to have it handy, without the need of a reader connection.  

Note, KOReader usually stores the epub book metadata information including the highlights and comments in `metadata.epub.lua` files (a.k.a. "metadata").  
These files are automatically created by KOReader for each epub book and kept in .sdr folders with the same names as the corresponding epub files.  

# Sources, Views and Actions

While using KOHighlights, keep in mind that most of the user interface controls have a Tooltip that briefly explains what they do.  
This Tooltip is shown when you hover your mouse over the corresponding control. 

## Main toolbar

The main toolbar of KH contains three types of buttons:

A. Source buttons -- used to select sources of book's metadata  
B. Views buttons -- used to switch between interface Views  
C. Action buttons -- used to execute specific functionality of the program

![1]


### A. Metadata sources

There are two sources from which KH can load highlights and other metadata:

1. Directly from the metadata files on connected devices or on local drives (located in .sdr folders), or

2. Copies of metadata files stored in the KH's internal database (provided that the user manually archived these copies of metadata, internally)

-   Use **"Loaded"** button to set the connected devices/drives as the source.

-   Use **"Archived"** button to set the KH's database as the source.


### B. Views

KH can present book metadata in either **[Books](#i-books-view)** or **[Highlights](#ii-highlights-view)** layout view.  
These views are explained in more detail later in this guide.  
In addition, there is a special **[Sync Groups](#iii-sync-groups-view)** view, used to synchronize highlights across multiple devices running KOReader.

### C. Action buttons

Depending on the metadata source and the specific View selected, KH will display/hide and/or activate/deactivate the action buttons that are appropriate for the given context.  
The action buttons execute KH functionality as described in their corresponding sections.



# I. Books View

As the name implies, the Books View is a layout used to display the content of the e-book metadata files created in KOReader.  
The Books View is accessible for both the Loaded and Archived sources of metadata.  

This layout has three panels: Book Selector, Book Information and Highlights.  

The Book Selector panel displays all loaded books in a table, with several columns showing the book's Name, Author, Type, Percentage read, last modified date, the number of highlights captured in the metadata file and more.  

The Book Info panel provides additional information for the select book such as Book Series, Tags, Language and Description.  

The Highlights panel shows the selected book's highlights and comments.  


### Action buttons in a glance

![2]

1. **Scan Directory**[ (Usage)](#scanning-for-books) - Used to select some directory that contains `.sdr` metadata folders of books, for scanning. Could be a reader's partition or a folder somewhere on a hard drive.
2. **Export**[ (Usage)](#exporting-highlights) - Used to export the highlights from the selected books. It opens a drop-down menu to select the format of the export.
3. **View** - Used to open the selected book with your system's default viewer.
4. **Filter**[ (Usage)](#filtering-content) - Used to filter the content of the Book Selector panel with keywords that can be found in the book's title, highlights or comments. 
5. **Merge/Sync** - This button is only activated if two entries of the _**same**_ book are selected in the book selector pane. It will try to sync the position and/or merge the highlights of the selected books.
6. **Delete**[ (Usage)](#deleting-highlights) - <ins>_**Warning: Use this with extreme caution!**_</ins> This button will open a drop-down menu to select one of the actions that will execute to the selected books. These are:
    - Delete their metadata
    - Delete the book files and their metadata
    - Delete the metadata of all the book entries with missing book files  
7. **Clear List**[ (Usage)](#clearing-the-book-list) - Removes all the entries from the Book Selector panel. Nothing gets deleted from the devices/drives.


### Usage Info - Common Tasks


#### Scanning for Books

1.  Put the source selector button (8) into the "Loaded" position

2.  Click the "Scan Directory" button (1)

3.  Navigate to the directory containing your KOReader metadata files

4.  Click on the Select Directory button

5.  KH will search for all metadata.lua files that are inside this directory and all subdirectories, and display the book names in the Book Selector panel



#### Reviewing selected book information

1.  Select a book in the book selector panel (KH will highlight your
    selection)

2.  Browse the highlights and comments in the Highlights panel

3.  Customize how highlights are displayed using the Preferences dialog
    (press the "Preferences" button (9) to show)


   ![3]

Note the Highlight Options specified in the Preferences dialog also impact what will be included / excluded when using the Export feature.


#### Editing the highlight's comment

1.  Double-click on the highlight you want to edit its comment

2.  Type something or edit the existing text

3.  Press OK to save the changes, Cancel to discard them 

4.  Your edits will be directly applied to (written into) the book's metadata file

For clarity, the highlights themselves must be created in KOReader and cannot be created/edited with KH.  
However, you can create/edit notes (comments) of the highlights both in KOReader and KH.  


#### Deleting highlights

1.  Click on the highlight you want to delete to select it (use ctrl+ click to select multiple entries)

2.  Right-click on the selection and chose "Delete"

3.  When KH displays a warning, click "Yes" to proceed and "No" to cancel

<ins>_**Warning: Do not use any of the options under the Delete button in the toolbar to delete specific highlights!**_</ins>  
Those options are used only to delete the entire metadata file for the book or even the underlying epub book file too.  

Note, if you are using KH to synchronize highlights across devices, the deleted highlights may be restored during the next synchronization, if other devices in the same [Sync Group](#iii-sync-groups-view) still contain the deleted highlights.  

This is because the synchronization process looks for the current differences inside the metadata files.  
The deleted entries are viewed by the program as missing highlights that must be synced/added to the metadata that misses them.  

If you want to delete certain highlights and comments on one device and then propagate your deletions to other devices (in the given sync group), use the workaround described in the [Replacing book metadata with Archived copy](#replacing-book-metadata-with-archived-copy) under [III. Sync Groups View](#iii-sync-groups-view) section of this guide.  


#### Filtering content

Use the "Filter" button (4) to open a dialog you can use to filter the content of the current View by some specified keywords.  
Only book entries that contain these words will be displayed.

   ![4]

1.  From the "Filter ..." drop down menu select where to search for the words, limiting the filtering to specific text areas like the "Book Titles" only.


#### Viewing the book's epub

1.  Select a book in the selector panel

2.  Click on the View button (3) or double-click anywhere on the book's row, to view the epub in your system's default viewer


#### Deleting metadata or .epub files from connected devices

- <ins>_**Warning: use at your own risk with extreme caution!**_</ins>

1.  Select a book in the selector panel (use ctr+click to select multiple books)

2.  Click on the Delete button (6) to display the drop-down menu

3.  Select the desired option from the list

    -   To delete the book's metadata file use the "Selected book's info" option

    -   To delete the book's .epub file(s) use the "Selected books" option

    -   To delete the metadata files that do not have their corresponding .epub/.pdf/etc. files, use the "All missing books info" option


#### Clearing the book list

-  Press "Clear List" button (7) to clear the Book Selection panel.

    Note, this action doesn't remove or delete any actual epub or metadata files from your system.  
-  Use "Scan Directory" button to repopulate the list (see [Scanning for Books](#scanning-for-books)), or drag and drop any folder that contains book metadata.  
 
Tip: To only remove one or a few entries from the panel, select them and just press the `Delete` button. No physical files will be deleted from the device/drive.


#### Exporting highlights

KH can export highlights to text, html, csv, and markdown formats.

Optional: Use the "Preferences" options to customize the way the highlights should look.  
This will also affect the way the exported files will look like.  

   ![3]

- Specify what part of the highlight data to include / exclude in your export (e.g. the dates, page numbers, comments, etc.), by checking / unchecking the appropriate option.
- Use "Sort Highlights by Date" / "Sort Highlights by Page" selector, to specify how you want the highlights to get sorted in your export.
- To change the date / time formatting use "Custom Date format" button.
- To change the appearance of the Markdown files, [see the next task](#using-custom-markdown-template) 

If the highlights are displayed OK, then the steps to actually export them are:  

1.  Select the book (or books) to export in the Book selector by clicking on them.  
   (While in the Books View, exporting a book's highlights will export all the highlights that are included in the book)  

2.  Click on the "Export" button and select the desired format from the drop-down menu.

3.  Specify the destination folder for the exported file(s) in the dialog.


#### Using Custom Markdown Template

KH includes a custom template creation feature, that you can use to tweak the appearance of the highlights exported into the Markdown format.   

1.  Check the "Custom Markdown" checkbox under "Preferences" dialog, to activate the option.

2.  Customize the template by clicking on the "Edit" button.

3.  Enter the variables into the parameter panels on the left side of the "Edit Markdown template" dialog (1).  
The outcome will be reflected in the preview panels on the right side (2)

   ![7]

> _**[Exporting with collapsible TOC levels](#exporting-to-markdown-with-collapsible-toc-levels)**_  
> This is an experimental feature designed to work with "2-save-full-chapter-path.lua" user patch.  
> With this user patch installed, the highlights created in the KOReader metadata's "chapter" key will contain the full path from the book's Table of Content separated by the "▸" character.


# II. Highlights View


The Highlights View is designed to present highlights from all loaded books in a single grid. This format is useful when one wants to view highlights across several books.  
Alternatively, one can compare the highlights from the same book but located on several devices .

The Highlights View has a single panel with several columns that one can re-arrange in the desired order.

All columns are sortable. Click on the column headers to sort the content either in the ascending or the descending order.


![8]


Most of the action buttons under the Highlights View look and behave the same way as under the Books View.  
However, there some notable differences to be aware of:

-   The "Export" button will export only the selected highlights, rather than including all highlights in a selected book as under the Books view.  
  Also, this button doesn't have the drop-down menu to select the format of the export. Once you press the button, one would specify the exported file destination in the dialog window as well as select the desired format under the "Save as Type" drop down.

-   The "Delete" button doesn't have a drop-down selector as in the Books view, and what it does is to delete all the selected highlights.  
The `Delete` button of the keyboard also performs the same function.


# III. Sync Groups View

This layout is designed to simplify highlight synchronization tasks across several devices running KOReader.

KH can synchronize (merge) highlights / reading positions between:

1.  Connected KOReader devices or local drives (required access to the book metadata folders)  
  These can also be _copies_ of folders that exist in devices that can expose their internal storage as a local drive to a PC (like modern Android phones). 

2.  KH's Internal database copy (archive)


### Sync Groups View elements

![9]


(1) Add a new group (KH will create a new empty group at the bottom of the group list)

(2) Sync all groups (KH will synchronize all active Sync Groups at once)

(3) Delete selected group(s) (also available via right-click menu)

(4) Refresh the source files (KH will re-read the metadata files specified in the Sync Paths of the selected group)

(5) Sync Position (check this box to sync the reading positions)

(6) Merge Highlights (KH will merge the highlights and comments across the members of the group)

(7) Sync with archived (KH will update the archived version in its internal database)

(8) The name of the Sync Group (typically the same as the book's title). The group can be renamed via right-click menu

(9) Sync this group: KH will only sync this group, not any other group. Same is available via right-click menu

(10) Add / Remove a member of the Sync Group

(11) Show/Hide the group members' paths

(12) Select / Change the file path pointing to book metadata files (e.g. after adding a new member to the group)

(13) Path error (red color indicates an issue with the file)

-  File path is inaccurate / metadata file is missing or not accessible (use "Refresh" button after correcting the issue to make KH to re-read the path)
- The metadata file is not compatible with the others, because it was created with a different CREngine version of KOReader.  
  (This version does not change often, but sometimes big changes make it necessary to break compatibility with older versions.) 
-  Book file's MD5 value is not matching to other books in the group (see advanced features for some ways to correct).

(14) Toggle the Sync Group active / inactive. Only active groups are synced when used Sync All (2)).  

Note, that you can re-arrange the Sync Groups order by dragging specific groups to the desired position.


### Functionality accessible via right-click menu

Right-clicking on a sync group will bring up the following menu:


   ![10]


-  **Rename group** - Allows to change the name of the Sync Group

-  **Sync group** - Same as the "Sync this group" button (9)

-  **Load group items** - Will load all metadata files in a group in the Books view

-  **Copy Archived to group**  
  <ins>_**Caution! Using this feature will overwrite all highlights in the group files with the archived version stored in KH database.**_</ins>  
  This feature can also be used when you edited the archived version of the book, and you want to propagate it to all devices.

-  **Delete selected** - Same as the "Delete" button (3).


### Creating a New (blank) Sync Group

- Click the "Add a new group" button (1). A new empty group will appear at the bottom of the list.


### Adding Books from connected devices to a Sync Group

1. Click the "Select" button (11) to locate the book's metadata file on device 1. KH will read the book's metadata file and automatically assign the book's title as the name for this sync group.

2. Rename the group if desired by right-clicking and selecting "Rename group".

3. Click the "Plus" button (10) to add a new path

4. Click the "Select" button (12) to locate the book's metadata file on device 2.

5. Repeat steps "3" and "4" for other connected devices if any.


### Specifying sync options for the sync group

1.  Check or uncheck the following options as needed:

-   "Sync Position" (5) to sync reading positions across devices.

-   "Merge Highlights" (6) to combine highlights and comments from all devices.

-   "Sync with archived" (7) to copy an updated version to  KH's internal database.


### Syncing All Active Groups

1. Ensure all groups you want to sync are set to active using the toggle switch (14).

2. Click the "Sync all groups" button (2).

3. KH will display a message informing if the sync was successful.


### Deactivating or Activating a Sync Group

1.  Locate the toggle switch (14) next to the group you want to activate or deactivate.

2.  Click the switch to toggle between active and inactive states.

Note, that only active groups will be synced when using the "Sync all
groups" function.

### Syncing a Specific Group

1.  Select the desired group from the list.

2.  Click the "Sync this group" button (9) or right-click and select "Sync this group".

3.  KH will display a message informing if the sync was successful.


### Deleting a Sync Group

1.  Select the group(s) you want to delete.

2.  Click the "Delete selected group(s)" button (3) or right-click and select "Delete group".


### Troubleshooting Path Errors

1.  Look for red-colored file paths (13) in your sync groups.

2.  Check if the file exists and is accessible at the specified location.

3.  If the file is missing or inaccessible, locate the correct file and update the path.

4.  Click the "Refresh the source files" button (4) to re-read the updated path.

5.  If the error persists due to MD5 mismatch, refer to the [Advanced Features](#advanced-features) section for [MD5 correction methods](#md5-mismatch-correction).


### Replacing book metadata with Archived copy

KH can replace the book metadata files for the selected sync group, with the most recent archived copy.

- If there is no good version of the book already archived
  - Locate a book with the right set of highlights in the Books View selector
  - Right click to it and select "Archive"

1.  Press the "Archived" button to view the database books

2.  Select the book to make sure it contains the desired set of highlights

3.  Make changes if required (e.g. edit comments or delete entire highlights)

4.  Go to the Sync Groups View

5.  Right-click on the Sync Group containing the book

6.  Select "Copy Archived to Group" (this will display a warning dialog)

7.  Click OK to accept


# Advanced Features


### Database management

Right-clicking or pressing the arrow at the right edge of the "Archived" button, will present the database menu.

   ![11]

The following options are available:
- **Create new database** - KH keeps the archived metadata in a default `data.db` file. With this action we can create a different database file to store a different group of book metadata.
- **Reload database** - This action refreshes the current database to reflect potentially external changes.
- **Change database** - This action allows you to change the current database file, by loading a different one.
- **Compact database** - This just executes a vacuum command to the database. It might make it a little smaller if it's been used for a long time.  


To quickly change the current database, you can drag a database file (`.db`) from the explorer, and drop it on the Book Selector panel of the Books View, while in the database mode (the "Archived" button pressed)


### MD5 Mismatch Correction

There is a common reason why the MD5 checksum between two seemingly identical files, can be different.  
**One of them, has been re-saved.**  

Let's say we copy the same `epub` file to our reader and keep a copy at our PC.
Then, we open the file on our PC with an editor to change a minor detail in the book.  
Or we don't edit the file at all. Just read it with a software that saves the reading position inside the file itself (like older and perhaps also current(?) versions of  Calibre).  

In every case, the book gets re-saved, and the re-saved book is a totally different file than the one in our reader.  
The reason the MD5 check exists is that, if we try to sync the highlights of different books, all sorts of strange things can (and will) happen.  
But if we're absolutely sure that nothing has actually changed in the contents of the epub, then, there is a way to bypass the MD5 check.  

<ins>_**Warning! Use this at your own risk!**_</ins>  
If there is an MD5 mismatch, you can right-click the erroneous sync path (13) and select "Ignore MD5" on the popup menu.  
This will create an empty `ignore_md5` file next to the metadata file, and will allow sync to proceed.  
Right-clicking again on this path, will give you the option to delete the `ignore_md5` file by un-checking the "Ignore MD5" option. 


### Exporting to markdown with collapsible TOC levels

Note, this is an experimental feature designed to work with "2-save-full-chapter-path.lua" user patch.  
With the user patch installed, the highlights created in the KOReader metadata's "chapter" key, will contain the full path from the book's Table of Content, separated by the "▸" character as follows:

`[chapter] = "Some chapter ▸ Some sub-chapter ▸ Some sub-sub-chapter"`

When this feature is being utilized during the export, KH will split the TOC path into individual levels and map each to its corresponding markdown heading (##, ###, ####, etc.) producing a clean hierarchical structure.  

The following is an example of the output presented in Obsidian:


![5]

_To export to markdown with collapsible TOC levels, follow the following steps:_

Pre-requisite: The exported highlights were taken with the user patch already installed (validate by navigating to the book's metadata file (located in the corresponding .sdr folder)).   
Make sure the "chapter" key contains full path headings in the format:  
`[chapter] = "Heading L1 ▸ Heading L2 ▸ Heading L3"`

1.  Click on the Settings button to open the dialog

2.  Select "Custom Markdown" checkbox

3.  _**Right-click**_ on the "Edit" button next to the "Custom Markdown" checkbox.  
  This will open the "Edit Markdown Template" dialog like the normal click would, but with a notable difference.  
  At the bottom of the dialog window there will be a checkbox called "Split Chapters" with the level selectors from Levels 1 to Level 6  
![6]

4.  Customize the template to reflect your preferences. In the screenshot above, the template will map the book's name to the Heading 1 and assign Headings 2 to 6 to other TOC levels. The highlights will appear under the pages numbers (in p-{page\#} format) and will also use Obsidian's "Quote" callout '\>\[!quote\]' . The comments will appear in Italics.

5.  Press "OK" and finalize the export by following the prompts


#### KOReader user patch installation

- To install the user patch on KOReader, copy the content of the following patch code, and paste it to an empty text file.  
     
  **For KOReader version 2024.07 use:**
  ```lua
  local ReaderAnnotation = require("apps/reader/modules/readerannotation")
  local ReaderToc = require("apps/reader/modules/readertoc")
  
  ReaderToc.getFullTocTitleByPage = ReaderToc.getFullTocTitleByPage or function(self, pn_or_xp)
      local chapters = {}
      local toc_ticks_ignored_levels_orig = {}
      local toc_chapter_title_bind_to_ticks_orig = self.toc_chapter_title_bind_to_ticks -- backup the flag
      self.toc_chapter_title_bind_to_ticks = true -- honor self.toc_ticks_ignored_levels
      local max_depth = self:getMaxDepth()
      for depth = max_depth, 1, -1 do
          toc_ticks_ignored_levels_orig[depth] = self.toc_ticks_ignored_levels[depth] -- backup the level
          -- ignore the level if it should be ignored due to original settings
          self.toc_ticks_ignored_levels[depth] = self.toc_ticks_ignored_levels[depth] and toc_chapter_title_bind_to_ticks_orig
          local chapter = self:getTocTitleByPage(pn_or_xp)
          if chapter ~= "" and chapter ~= chapters[1] then
              table.insert(chapters, 1, chapter)
          end
          self.toc_ticks_ignored_levels[depth] = true -- ignore the level on next iterations
      end
      self.toc_chapter_title_bind_to_ticks = toc_chapter_title_bind_to_ticks_orig -- restore the flag
      table.move(toc_ticks_ignored_levels_orig, 1, max_depth, 1, self.toc_ticks_ignored_levels) -- restore all levels
      return chapters
  end
  
  ReaderAnnotation.addItem_orig = ReaderAnnotation.addItem
  ReaderAnnotation.addItem = function(self, item)
      item.chapter = table.concat(self.ui.toc:getFullTocTitleByPage(item.page), " ▸ ")
      return self:addItem_orig(item)
  end
  ```
     
  **For KOReader versions after 2024.07 use:**

  ```lua
  local ReaderAnnotation = require("apps/reader/modules/readerannotation")
  
  ReaderAnnotation.addItem_orig = ReaderAnnotation.addItem
  ReaderAnnotation.addItem = function(self, item)  
  
  item.chapter = table.concat(self.ui.toc:getFullTocTitleByPage(item.page), " ▸ ")
  return self:addItem_orig(item)
  end
  ```
 
- Rename this file to "2-save-full-chapter-path.lua".  
- Then, place the file into your KOReader's "patches" directory.


  [1]:  ./images/1_2.png
  [2]:  ./images/2_2.png
  [3]:  ./images/3_2.png
  [4]:  ./images/4_2.png
  [5]:  ./images/image6.png
  [6]:  ./images/image7.png
  [7]:  ./images/image5.png
  [8]:  ./images/8_2.png
  [9]:  ./images/9_2.png
  [10]: ./images/10_2.png
  [11]: ./images/11.png

 
