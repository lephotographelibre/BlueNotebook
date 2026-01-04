# Online Help - BlueNotebook V4.1.5

## Table of Contents
*   [1. Introduction](#introduction)
*   [2. Launching and Journal Configuration](#launching)
*   [3. The Main Interface](#interface)
*   [4. The "Note of the Day" Concept](#concept-journal)
*   [5. Managing and Using Templates](#templates)
*   [6. Navigating Through the Journal](#time-navigation)
*   [7. Managing Images and Attachments](#images-files)
    *   [7.1 Inserting a Bookmark](#bookmarks)
    *   [7.2 Inserting Images (Markdown and HTML)](#images-markdown)
    *   [7.3 Managing Attachments](#attachments)
    *   [7.4 Inserting Images with EXIF Data](#exif-data)
    *   [7.5 Inserting Links (local and remote)](#local-links)
*   [8. The Reader Panel (EPUB and PDF)](#reader-panel)
*   [9. Notes Management (File Explorer)](#notes-management)
    *   [9.1 Search and Sort](#notes-search)
    *   [9.2 Displaying Detail Columns](#notes-columns)
    *   [9.3 File and Folder Operations](#notes-operations)
*   [10. Integrations (Weather, YouTube, etc.)](#integrations)
    *   [10.1 Inserting the Day's Weather](#weather)
    *   [10.2 Integrating a GPX Trace](#gpx-trace)
    *   [10.3 Integrating a Static Map (GPS)](#gps-maps)
    *   [10.4 Integrating a YouTube Video](#youtube-video)
        *   [10.4.1 Retrieving the Transcript](#youtube-transcript)
    *   [10.5 Integrating a Book (Amazon ISBN)](#amazon-isbn)
    *   [10.6 Inserting the Quote of the Day](#quote-of-the-day)
    *   [10.7 Inserting the Day's Astronomical Data](#astro-of-the-day)
    *   [10.8 Converting a PDF to Markdown](#pdf-to-markdown)
    *   [10.9 Converting a URL/HTML to Markdown](#url-to-markdown)
*   [11. Advanced Search and Navigation](#advanced-search)
*   [12. Exploring the Menus](#menus)
*   [13. File Export](#file-export)
    *   [12.1. Export to HTML (single file)](#export-html-single)
    *   [12.2. Export to PDF (single file)](#export-pdf-single)
    *   [12.3. Export Journal to PDF](#export-journal-pdf)
    *   [12.4. Export Journal to EPUB](#export-journal-epub)
*   [14. Backup and Restore](#backup-restore)
*   [15. Advanced Customization](#preferences)
    *   [14.1 Editor Themes](#editor-themes)
    *   [14.2 HTML Preview Themes](#preview-themes)
    *   [14.3 PDF Export Themes](#pdf-themes)
*   [15. Keyboard Shortcuts](#shortcuts)
*   [16. Frequently Asked Questions (FAQ)](#faq)
*   [17. Main Python Packages](#packages)

## 1. Introduction <a id="introduction"></a>
Welcome to BlueNotebook! This guide explains how to use the application to keep your personal journal in Markdown and manage your associated notes and documents.

BlueNotebook is a simple text editor that lets you focus on writing. It uses Markdown syntax and displays a real-time preview of your document.

Advanced search and navigation features allow users to quickly find information in the various daily notes with the support of tags and automatic indexing.

New document management features allow you to manage, along with the chronological notes of the journal, Markdown documents, PDFs, Epub ebooks, maps and images that will gradually build your personal knowledge base integrated into the journal through link objects, bookmarks and attachments.

## 2. Launching and Journal Configuration <a id="launching"></a>
### How to Launch BlueNotebook
*   **On Windows**: Double-click the `run_bluenotebook.bat` file. A terminal window will open to configure the environment, then the application will launch.
*   **On Linux**: Open a terminal, make the script executable once with the command `chmod +x run_bluenotebook.sh`, then launch it with `./run_bluenotebook.sh`.

### Configure your Journal Directory
BlueNotebook needs to know where to save your notes. There are three ways to tell it, in order of priority:

1.  **Command Line Argument `--journal` (Highest Priority)**<br>
    You can specify a journal folder directly at launch. This is the most flexible method.<br>
    - On Linux: `./run_bluenotebook.sh --journal /path/to/my/journal`<br>
    - On Windows: `run_bluenotebook.bat --journal C:\Users\YourName\Documents\Journal`
2.  **Environment Variable `JOURNAL_DIRECTORY`**<br>
    You can set this variable for BlueNotebook to use it by default at each launch.<br>
    - On Linux (temporary): `export JOURNAL_DIRECTORY="/path/to/my/journal" && ./run_bluenotebook.sh`<br>
    - On Windows (temporary): `set JOURNAL_DIRECTORY=C:\path\to\journal && run_bluenotebook.bat`
3.  **Default Directory (Lowest Priority)**<br>
    If none of the above methods are used, BlueNotebook will create and use a folder named `bluenotebook` in your home directory.

### The First Start Screen
On the very first launch of BlueNotebook (when no configuration file exists), a welcome screen is displayed to guide you through the initial setup. This screen allows you to define the essential parameters before starting to use the application.

Here are the options you can configure:

*   **Application Language:** Choose between "Français" and "English" for the application interface. This choice can be changed later in `Preferences > General`.
*   **Journal Directory:** This is the location where all your notes, images and attachments will be saved. By default, a `BlueNotebookJournal` folder is proposed in your home directory, but you can choose another location. The necessary subfolders (`notes`, `images`, etc.) will be created automatically.
*   **Backup Directory:** Choose where the backup archives of your journal will be stored (created via `File > Backup Journal...`). By default, a `BlueNotebookBackup` folder is proposed.

Once you have made your choices, click on **"Done"**. BlueNotebook will save these settings, create the necessary folders and launch, ready to be used.

## 3. The Main Interface <a id="interface"></a>
The interface is divided into several panels to adapt to your way of working:

*   **"Notes" Panel (`F9`):** Located on the far left, is a powerful and integrated file manager, designed to organize all documents associated with your journal notes.
*   **Navigation Panel (`F6`):** Contains the calendar, search tools and tag cloud.
*   **"Document Outline" Panel (`F7`):** Displays the structure of the titles (`#`, `##`, etc.) of your current note. Click on a title to navigate instantly.
*   **The Editor:** The central area where you write your text in Markdown. This panel is always visible.
*   **The HTML Preview (`F5`):** Displays the final rendering of your text, formatted in real time.
*   **The Reader (`F8`):** A dedicated panel for reading documents (EPUB, PDF).

Just below the main menu bar, a **panel toolbar** allows you to quickly show or hide these panels using toggle buttons. The state of these buttons (on/off) is synchronized with the preferences you set in `Preferences > Panels`. The keyboard shortcuts (`F5`, `F6`, `F7`, `F8`) are also functional.

The **status bar**, located at the very bottom of the window, is a valuable source of information. From left to right, you will find:

*   The name of the **current file** (e.g. `20250920.md`).
*   A modification indicator (`●`) that appears if your work is not saved.
*   Statistics on your document (lines, words, characters).
*   At the far right, the path to your **journal folder** and the **indexing statistics**.
    The latter is clickable: a click on it manually relaunches the indexing of tags, which is useful if you have modified files outside the application.

## 4. The "Note of the Day" Concept <a id="concept-journal"></a>
BlueNotebook is organized around a simple but powerful concept: your journal is a folder on your computer, and each day is a text file.

### The Note of the Day
At each launch, BlueNotebook checks your journal folder. It looks for a file corresponding to the current date, named according to the format `YYYYMMDD.md` (for example, `20250920.md`). If this file exists, it opens it automatically. Otherwise, it presents you with a new blank page, ready to become the entry of the day.

### Smart Saving
The save action (`File > Save` or `Ctrl+S`) is at the heart of this system:

*   **If the note of the day does not yet exist**, it will simply be created with the content of the editor in your journal folder.
*   **If the note of the day already exists**, a dialog box will offer you two choices:
    *   **Append to the end**: Your new text will be added to the end of the existing content, separated by a line. This is the ideal option for adding thoughts or notes throughout the day without losing previous information.
    *   **Replace**: The original content of the note of the day will be completely overwritten and replaced by what is currently in the editor. Be careful with this option!

## 5. Managing and Using Templates <a id="templates"></a>
Templates are pre-filled note structures that allow you to start your work quickly. BlueNotebook offers you complete management of templates to create, use and insert recurring structures.

### Using a template for a new note
When you create a new document via `File > New...` (`Ctrl+N`), a dialog box opens and offers you:

*   **Create a blank file:** To start with a blank page.
*   **Use a template:** A drop-down list presents you with all the available templates (`.md` files) in the `resources/templates/` folder. By choosing a template, your new note will be pre-filled with its content.

### Creating your own templates
Do you have a note structure that you use often? Turn it into a template!

1.  Write or open the note you want to use as a template.
2.  Go to the `File > Save as Template...` menu.
3.  A dialog box will open, inviting you to give a name to your template (for example, `weekly_report.md`).
4.  Validate. Your template is now saved and will be available in the list when creating a new note.

### Inserting a template into an existing note
Need to add a structured section (like a meeting report) in the middle of your daily note?

*   Place your cursor where you want to insert the content.
*   Go to the `Edit > Insert Template...` menu.
*   Choose the desired template from the dialog box. Its content will be inserted at the cursor position.

### Dynamic placeholders
To make your templates even more powerful, you can use "placeholders" that will be automatically replaced when using the template:

*   `{{date}}`: Will be replaced by the full date of the day (e.g. "Monday 28 October 2025").
*   `{{timestamp}}`: Will be replaced by the current time (e.g. "14:32").

Feel free to modify the existing templates (`default.md`, `meeting.md`, etc.) or create your own to adapt BlueNotebook to your needs!

## 6. Navigating Through the Journal <a id="time-navigation"></a>
The Navigation panel (`F6`) offers you several tools to travel in time through your notes.

*   **The Calendar:** The days for which a note exists are highlighted. Click on a date to open the corresponding note.
*   **Navigation Buttons:** Just above the calendar, the `Previous` and `Next` buttons allow you to jump to the nearest existing note, while `Today` brings you back to the note of the day.

## 7. Managing Images and Attachments <a id="images-files"></a>
### 7.1 Inserting a Bookmark <a id="bookmarks"></a>
The "Bookmark" feature allows you to create rich links to web pages. BlueNotebook will check the URL, retrieve the page title and generate a formatted Markdown link.

#### How does it work?
1.  **Launch the action:** Go to `Insert > 🔖 Bookmark` or right-click in the editor and choose `Links > 🔖 Bookmark`.
2.  **URL Selection:**
    *   If you have already selected a URL in the editor, it will be used automatically.
    *   Otherwise, a dialog box will open for you to enter the URL.
3.  **Verification and formatting:** The application checks the URL in the background. If it is valid, a formatted link is inserted.
    *   If a page title is found: `🔖 [Bookmark | Page Title - URL](URL)`
    *   If no title is found: `🔖 [Bookmark | URL](URL)`

### 7.2 Inserting Images (Markdown and HTML) <a id="images-markdown"></a>
To ensure that your journal remains complete and portable, BlueNotebook adopts a robust and intelligent management of the images you insert, whether they come from your computer or a remote URL.

#### The Automatic Process
Whether you use `Insert > Markdown Image` or `Insert > Image (<img>)`, the application systematically performs the following actions in the background:

1.  **Systematic copy to the journal:** Whether the image is selected from a local file or a remote URL, it is now always copied to the `images/` directory of your journal.
2.  **Renaming with timestamp:** To avoid conflicts and keep a chronological record, the copied image is renamed using the format `YYYYMMDDHHMMSS_original_name.extension`. For example, `photo.jpg` becomes `20251026103000_photo.jpg`.
3.  **Generation of clickable Markdown:** The generated Markdown tag is now a clickable image. It takes the form `[![alt_text](path/image.jpg)](path/image.jpg)`. In the HTML preview, a click on the image will open it in large in your browser.
4.  **Optimized display:** Images inserted in Markdown are automatically resized so as not to exceed 600px in width or height in the preview, while maintaining their proportions.

### The Advantages
*   **Portability:** Your journal becomes completely autonomous. You can move or copy your journal folder to another computer, and all your images will continue to be displayed, because they are included.
*   **Security:** The original image on your computer is not modified.
*   **Durability:** Links to images on the internet are no longer at risk of "breaking" if the remote site disappears.
*   **Organization:** All the visual resources of your journal are centralized in a single folder.

### 7.3 Managing Attachments <a id="attachments"></a>
In addition to images, BlueNotebook allows you to attach any type of file to your notes (PDF, documents, archives, etc.). This feature is designed to centralize all resources related to your journal in one place.

#### How to insert an attachment?
1.  Place your cursor where you want to insert the link to the attachment.
2.  Go to the `Insert > 📎 Attachment` menu.
3.  A dialog box will open, allowing you to:
    *   Paste a **URL** to a remote file (e.g. an online PDF).
    *   Click on **"Browse..."** to select a file on your computer.

#### What happens in the background?
When you validate, BlueNotebook performs several actions to ensure the portability of your journal:

*   **Creation of a dedicated folder:** A folder named `attachments` is created at the root of your journal directory (if it does not already exist).
*   **Copy and rename:** The file you selected (whether local or remote) is copied to this `attachments` folder. For better organization, it is automatically renamed using the format `YYYYMMDD_original_name.extension`, where `YYYYMMDD` corresponds to the date of the note in which you insert the attachment.
*   **Insertion of a Markdown link:** A formatted link is inserted into your editor, for example:<br>`📎 [Attachment | 20251026_report.pdf](attachments/20251026_report.pdf)`

Thanks to this system, even if you move your journal folder to another computer, all links to your attachments will continue to work because the files are stored locally in the journal.

### 7.4 Inserting images with EXIF data <a id="exif-data"></a>
To enrich your notes, especially for a travel journal, BlueNotebook can extract and display the EXIF (Exchangeable image file format) data contained in your photos.

#### How does it work?
1.  Use the `Insert > Markdown Image` menu to choose a local image.
2.  After choosing the size of the image, the application analyzes the file.
3.  If relevant EXIF data (GPS coordinates, date, camera model, etc.) are found, a dialog box will ask you: **"Do you want to insert them under the image?"**
4.  If you accept, a line of metadata formatted in Markdown will be added under the image, presenting the information in a compact and readable way.

#### What information is displayed?
If available in the image, you can see:

*   **Location:** The city or village is automatically found from the GPS coordinates.
*   **GPS coordinates:** With a direct link to OpenStreetMap.
*   **Date and time** of the shot.
*   **Technical information:** Camera model, aperture, speed, focal length and ISO sensitivity.

This feature transforms a simple image into a complete information sheet, perfect for remembering the details of each captured moment.

### 7.5 Inserting Links (local and remote) <a id="local-links"></a>
The `Insert > Link` menu has been improved to allow you to create links not only to websites, but also to any local file on your computer, while ensuring the portability of your journal.

#### How does it work?
1.  Go to the `Insert > Link` menu. A dialog box opens.
2.  **For a web link:** Fill in the "Link text" and paste the URL (`http://...`) in the "URL or path" field.
3.  **For a local file:**
    *   Click the **"Browse..."** button. A file selector will open, positioned by default at the root of your journal.
    *   Select any file (document, image, note, etc.). The "Link text" field will be automatically filled with the file name.

#### Smart management of local files
*   **If the file is already in your journal:** A relative link is created. Your journal remains portable.
*   **If the file is outside your journal:** A dialog box will ask you if you want to copy the file to your journal. If you accept, you can choose a destination folder (by default `notes/` or `attachments/`). The file will be copied there, and a relative link will be created. This ensures that you never lose a link if you move your journal.

The link generated for a local file will have the following format: `🔗 [[[Link text]]](relative/path/to/file)`. The 🔗 emoji allows you to visually identify links to local files, and the `[[[...]]]` syntax is recognized by the editor for syntax highlighting, while remaining a perfectly functional link in the preview.

This feature allows you to link your notes, reference documents and images together in a simple and robust way.

## 8. The Reader Panel (EPUB and PDF) <a id="reader-panel"></a>
BlueNotebook now integrates a powerful document reader, allowing you to consult books in **EPUB** format and **PDF** documents directly next to your notes. It is the ideal tool for research, taking notes from sources or simply for reading.

### Activation and Opening
*   **Activation:** Click the **"Reader"** button in the panel toolbar or use the shortcut `F8`.
*   **Open a document:** Go to the `File > Open Document...` menu to select an `.epub` or `.pdf` file on your computer.
*   **Smart behavior:** If you activate the "Reader" panel without a document being loaded, the application will automatically invite you to choose one. The application also remembers the last opened document to reload it at the next startup.

### Reader Features
The Reader panel is divided into two parts: the table of contents on the left and the reading area on the right.

*   **Multiple navigation:** Navigate through the document by clicking on a chapter in the **table of contents**, using the **drop-down list** under the text, or with the **Previous/Next** buttons.
*   **Integrated search:** Use the search bar at the top to find text throughout the document. The "Next" and "Previous" buttons allow you to navigate between the occurrences, which are highlighted.
*   **Text selection and Copy-paste:** You can select text with the mouse in EPUB and PDF documents. a right click will open a context menu offering options to copy the selected text or select all.
*   **Image management:** If you right-click on an image (in an EPUB or PDF), the context menu will offer to save it (converted to JPEG format by default) or copy it to the clipboard. The application remembers the last used save folder.
*   **Space optimization:** Click the `<` or `>` button to the left of the search bar to hide or show the table of contents and maximize your reading space.
*   **Contextual information:** Below the navigation bar, the document title, its author and your current position (Chapter X / Y) are permanently displayed.
*   **Dynamic zoom:** Hold down the `Ctrl` key and use the **mouse wheel** to zoom in or out on the page.
*   **Advanced text selection and Copy-paste:** The text selection system has been improved to be particularly precise and intuitive in PDFs. The context menu offers options to copy the selected text, select all, or copy the text of the entire page.

## 9. Notes Management (File Explorer) <a id="notes-management"></a>
The "Notes" panel (`F9`), located on the far left, is much more than a simple addition: it is a real file explorer integrated into BlueNotebook, designed to organize all documents, ideas and resources that are not directly related to a specific date. It transforms your journal into a real "second brain".

#### Key Features of the "Notes" Panel
*   **File Exploration:** Displays a tree view of the special `notes/` folder of your journal. You can create a hierarchy of subfolders there to organize your projects, research, or document collections. The panel is now resizable in width to adapt to your needs.
*   **Intelligent Filtering:** The view is streamlined to display only relevant file types:
    *   **Text:** `.md`, `.txt`
    *   **Documents:** `.pdf`, `.epub`, `.html` (openable in the editor)
    *   **Media:** Images (`.jpg`, `.png`), videos (`.mp4`) and audio (`.mp3`).
*   **Visual Customization:**
    *   **Folder coloring:** Right-click on a folder and choose a color from 10 to mark it visually. This choice is saved.
    *   **Zoom:** Hold `Ctrl` and use the mouse wheel to enlarge or reduce the text size in the tree for better reading comfort.
*   **Persistence:** The application remembers the last folder you selected and automatically re-opens it at the next startup.

### 9.1 Search and Sort <a id="notes-search"></a>
To navigate more efficiently in your notes, the panel now integrates search and sort tools.

*   **Search bar:** Located at the top of the panel, it allows you to instantly filter the tree. The search is case-insensitive and accent-insensitive. Press `Enter` or the "Search" button to launch the filter. An erase button allows you to reset the view.
*   **Sort by column:** Click on the column headers ("Name", "Size", "Last modification") to sort files and folders. A second click on the same header reverses the sort order.

### 9.2 Displaying detail columns <a id="notes-columns"></a>
By default, only the file name is displayed. You can display additional information:

*   Use the keyboard shortcut `Ctrl+M` to show or hide the "Size", "Type" and "Last modification" columns.

### 9.3 File and Folder Operations (Context Menu) <a id="notes-operations"></a>
A right-click in the "Notes" panel opens a rich context menu that adapts to what you select.

**On a folder:**

*   **`New note...`:** Creates an `.md` file, asks you for a name, and opens it in the editor.
*   **`Create a subfolder...`:** Creates a new directory inside the selected folder.
*   **`Import a file...`:** Copies a file from your computer or downloads from a URL into the selected folder.
*   **`Expand all` / `Collapse all`:** Recursively expands or collapses the entire tree of a folder.
*   **`Cut` / `Copy` / `Paste`:** Manage your files with classic clipboard operations.
*   **`Rename...` / `Delete...`:** Deletion displays a smart confirmation, warning you if the folder is not empty and how many items it contains.

**On a file:**

*   **`Open`:** Opens the file in the appropriate panel (Editor, Reader) or with your system's default application for media.
*   `.html` files are now opened directly in the Markdown editor.
*   As well as the `Cut`, `Copy`, `Rename`, `Delete` options.

**In an empty area:**

*   **`Create a folder...`:** Creates a new folder at the root of the `notes/` directory.
*   **`Paste`:** Pastes a previously copied/cut file or folder.

## 10. Integrations (Weather, YouTube, etc.) <a id="integrations"></a>
BlueNotebook can interact with external services to enrich your notes. These features are found in the `Integrations` menu.

### 10.1 Inserting the Day's Weather <a id="weather"></a>
Add the current weather conditions to your daily notes, which is perfect for a logbook or to contextualize your writings.

1.  **Initial configuration:** Before you can use this feature, you must configure it.
    *   Go to `Preferences > Integrations`.
    *   In the "Weather Weatherapi.com" section, fill in your **City** and your **API Key**. You can get a free API key on the [weatherapi.com](https://www.weatherapi.com) website.
    *   Validate the preferences. This information is saved locally and securely.
2.  **Insertion:**
    *   Place your cursor at the desired location in the editor.
    *   Go to the `Integrations > Weather Weatherapi.com` menu.
    *   A line of text in Markdown format, containing a weather emoji and the information (temperature, conditions, wind, humidity), will be inserted into your note.

### 10.2 Integrating a GPX Trace <a id="gpx-trace"></a>
For hiking, cycling or travel enthusiasts, BlueNotebook allows you to integrate a map of your route directly from a GPX trace file.

1.  Go to the `Integrations > GPX Trace` menu.
2.  A dialog box opens, allowing you to:
    *   Paste a **URL** to an online GPX file.
    *   Click on **"Browse..."** to select a GPX file on your computer.
3.  Then choose the **width** of the map image in pixels.
4.  The application will then automatically:
    *   Analyze the GPX file to extract the track, the start/end date and time.
    *   Save a copy of the GPX file in the `gpx/` folder of your journal.
    *   Generate a static map image (`.png`) with the track and a start marker, then save it in the `images/` folder.
    *   Insert a block of text in Markdown format into your note.

The result is an image of your route, clickable to open the map on OpenStreetMap with a marker on the starting point. The legend is rich and interactive: it contains the name of the place (clickable), the start date and time, as well as the total duration of the route.

### 10.3 Integrating a Static Map (GPS) <a id="gps-maps"></a>
You can generate and insert a static map directly into your notes from GPS coordinates. This feature is ideal for documenting travel locations, hikes or points of interest.

1.  Go to the `Integrations > GPS Map` menu.
2.  A dialog box will ask you to enter the **Latitude** and **Longitude**. You can also select text in the format `[46.514, 0.338]` in the editor before launching the action to pre-fill the fields.
3.  Then choose the **width** of the map image in pixels.
4.  The application will then:
    *   Contact a geolocation service to find the name of the nearest place (e.g. "Ligugé").
    *   Generate a static map image (a `.png` file) and save it in the `images/` folder of your journal.
    *   Insert a block of text in Markdown format into your note.

The result is a clickable image that links to OpenStreetMap (with a marker on the location), accompanied by a clear legend indicating the coordinates and the name of the place, also clickable.
```
[![Map of Poitiers...](images/20251026_map_Poitiers.png)](https://www.openstreetmap.org/...)

**GPS:** [46.58, 0.34] - [Poitiers](https://www.openstreetmap.org/...)
```

### 10.4 Integrating a YouTube Video <a id="youtube-video"></a>
You can easily integrate a YouTube video or playlist into your notes, with a clickable thumbnail that links to the YouTube site.

1.  Go to the `Integrations > YouTube Video` menu.
2.  If you have already selected a YouTube URL (video or playlist) in the editor, it will be used automatically.
3.  Otherwise, a dialog box will open with the message "Enter the URL of the YouTube video or playlist:". Paste your link there.
4.  The application automatically detects if it is a video or a playlist and inserts a block of text in Markdown format with:
    *   For a **video**: the title and the thumbnail.
    *   For a **playlist**: the title, the author, the number of tracks and the thumbnail.

**Tip:** You can enable or disable this feature in `Preferences > Integrations`.

#### 10.4.1 Retrieving the Transcript <a id="youtube-transcript"></a>
To further enrich your notes, BlueNotebook can automatically retrieve the textual transcript of a YouTube video, if available.

1.  **Automatic process:** When you integrate a video, the application checks in the background if a transcript exists (in French or English). This search does not block the interface, and a message `Retrieving transcript in progress...` is displayed in the status bar.
2.  **Proposal to the user:** If a transcript is found, a dialog box appears: "For this YouTube video a transcript in {language} exists, do you want to add it?".
3.  **Formatted insertion:** If you accept, the text of the transcript, intelligently formatted into paragraphs, is added under the video block, preceded by the title `**Transcript of the YouTube video**`.

This feature is extremely useful for taking notes, searching for keywords in a video or keeping a written record of an oral content.

**Configuration:** You can control this feature in `Preferences > Integrations` via the checkbox `"Allow display of YouTube video transcripts in the Markdown editor"`. Note that this option is only active if the main YouTube integration is itself authorized.

### 10.7 Inserting the Day's Astronomical Data <a id="astro-of-the-day"></a>
Add the sunrise/sunset times and the phase of the moon for the city of your choice, ideal for a logbook or for noting the day's conditions.

1.  **Initial configuration:** Before you can use this feature, you must configure it.
    *   Go to `Preferences > Integrations`.
    *   In the "Astro Sun and Moon" section, enter the name of your **City** and click on **"Search"**. The application will automatically find the latitude and longitude.
    *   Validate the preferences. This information is saved locally.
2.  **Insertion:**
    *   Place your cursor at the desired location in the editor.
    *   Go to the `Integrations > Astro of the day` menu.
    *   A block of text in Markdown format containing the information (sunrise/sunset, moon phase) for your city will be inserted into your note.

### 10.8 Converting a PDF to Markdown <a id="pdf-to-markdown"></a>
This powerful integration allows you to transform the textual content of a PDF file (local or remote) into a clean and editable Markdown document. It is the perfect tool for extracting the content of articles, reports or documents that you want to archive and make searchable in your journal.

1.  Go to the `Integrations > PDF-Markdown Conversion` menu.
2.  A dialog box opens, inviting you to provide the path to a local PDF file (via the "Browse..." button) or to paste the URL of an online PDF.
3.  After validation, the application downloads and analyzes the PDF in the background.
4.  Once the conversion is complete, the Markdown content is automatically loaded into the editor, ready to be modified, annotated and saved as a new note.

**Note:** This feature relies on the `markitdown` library from Microsoft. The quality of the conversion depends on the structure of the source PDF (text-based PDFs work better than image-based ones).

### 10.9 Converting a URL/HTML to Markdown <a id="url-to-markdown"></a>
Transform any web page or local HTML file into a clean and readable Markdown note. This feature is ideal for archiving blog articles, technical documentation or any other web page that you want to keep and annotate.

1.  Go to the `Integrations > URL(HTML)-Markdown Conversion` menu.
2.  A dialog box opens. If you had selected a URL in the editor, it will already be pre-filled. You can also paste a URL or browse your disk to choose an `.html` file.
3.  You can refine the conversion with several options:
    *   **Add title as #:** Automatically adds the page title as a level 1 heading at the top of the document.
    *   **Keep Markdown links:** Keeps all hyperlinks from the original page.
    *   **Use Readability to clean:** This is the most powerful option. It uses an algorithm to extract only the main content of the article, removing ads, menus and other superfluous elements.
4.  After validation, a window asks you where to save the new `.md` file (by default in the `notes/` folder of your journal).
5.  The file is created and immediately opened in the editor, ready to be used.

### 10.6 Inserting the Quote of the Day <a id="quote-of-the-day"></a>
Start your day with an inspiring thought. BlueNotebook can retrieve a famous quote and insert it into your note.

*   **At startup:** If the option is enabled in `Preferences > Integrations`, a window displaying the quote of the day will appear at the launch of the application.
*   **Manually:** At any time, you can go to the `Integrations > Quote of the day` menu to insert the current quote (formatted as a Markdown quote) where your cursor is.

## 11. Advanced Search and Navigation by Tags <a id="advanced-search"></a>
The Navigation panel integrates powerful tools to find your information: the tag cloud and a search field.

### The Tag Cloud
Under the calendar, you will find the "tag cloud":

*   **Tag Cloud:** Displays the tags (`@@word`) that you use most often. The more frequent a tag is, the larger it appears.

**Interaction:** Click on a tag in the cloud to automatically insert it into the search field and **immediately launch the search**.

**Attention:** Not all tags appear in the cloud, only the most frequent ones. Nevertheless, you can launch a search on any tag by direct entry in the Search field.

### The Search Field
Located under the calendar, this field allows you to launch a precise search. It is designed to be fast and efficient.

*   **Search for a tag:** You must prefix your search with `@@` (e.g. `@@project`).
*   **List of tags:** Click the `▼` button to the right of the field to display the list of all your tags. Clicking on a tag in this list selects it and **automatically launches the search**.
*   **Clear the search:** Click the icon that appears on the right in the field to clear its content and return to the cloud display.

### The Search Results Panel <a id="search-results-panel"></a>
The search results panel is always visible in the navigation panel, just below the tag cloud, and occupies all the remaining space. Each line corresponds to a found occurrence and contains two columns: "Date" and "Text". The displayed context corresponds to **the entire end of the line** where the tag was found, giving you a much more complete overview. The results are sorted by default from most recent to oldest (you can reverse the sort by clicking on the "Date" header).

**Default behavior and search:**

*   **By default**, if no search has been performed, this panel displays the list of `@@TODO` tasks with the title "✔ @@TODO Task List".
*   As soon as a **search is launched**, the title becomes "🔍 Search Results" and the panel displays the corresponding results.
*   If you search for the `@@TODO` tag again, the title switches back to "✔ @@TODO Task List".

**Interaction:** Click on a result line to open the corresponding note **directly to the right line** in the editor!

**Refreshing the index:** For more convenience, you can manually relaunch the indexing of tags by clicking directly on:
*   The main title of the panel: **"Journal Navigation"**.
*   The title of the results panel: **"✔ @@TODO Task List"** or **"🔍 Search Results"**.

## 12. Exploring the Menus <a id="menus"></a>
Here is a visual guide to all the features accessible from the menu bar.
```
File
├── New... (Ctrl+N): Creates a new file, offering a blank document or a template.
├── Open... (Ctrl+O): Opens a file (Markdown, EPUB, PDF) and displays it in the appropriate panel (editor or reader).
├── ---
├── Save in Journal (Ctrl+S): Saves the note in the journal directory.
├── Save as Template...: Saves the current document as a new reusable template.
├── Save as... (Ctrl+Shift+S): Saves the current note in a new file of your choice.
├── ---
├── Open Journal: Allows you to select a new folder that will serve as a journal.
├── Backup Journal...: Creates a complete ZIP archive of your current journal.
├── Restore Journal...: Restores a journal from a ZIP archive.
├── ---
├── Export HTML...: Exports the note as an HTML file.
├── Export to PDF...: Exports the current note as a PDF file.
├── Export Journal PDF...: Creates a PDF document of your journal, with selection of dates, title and author.
├── Export Journal EPUB...: Creates a digital book in EPUB format of your journal.
├── ---
├── Preferences...: Opens the application customization window.
├── ---
└── Quit (Ctrl+Q): Closes BlueNotebook.

Edit
├── Insert Template...: Inserts the content of a template at the cursor position.
├── ---
├── Undo (Ctrl+Z): Undoes the last action.
├── Redo (Ctrl+Y): Redoes the last undone action.
├── ---
└── Search (Ctrl+F): Searches for text in the editor.

Format
├── Headings
│   ├── Level 1 (#)
│   ├── Level 2 (##)
│   ├── Level 3 (###)
│   ├── Level 4 (####)
│   └── Level 5 (#####)
├── Text Style
│   ├── Bold (**text**)
│   ├── Italic (*text*)
│   ├── Strikethrough (~~text~~)
│   └── Highlight (==text==)
├── Code
│   ├── Monospace (inline)
│   └── Code Block
├── Lists
│   ├── Unordered List
│   ├── Ordered List
│   └── Task List
├── ---
└── Clear Formatting: Removes all Markdown formatting from the selection.

Insert
├── Image (Ctrl+Shift+I): Inserts an image with the Markdown syntax `!`. Copies local images to the journal.
├── 🔗 Link: Opens a dialog box to create a `text` link. Manages remote links and local files (with copy to journal if necessary).
├── URL/Email Link: Encloses a selected URL or email with angle brackets `< >` to make it clickable.
├── 📎 Attachment: Inserts a link to an attached file (local or remote), copied to the `attachments` directory of the journal.
├── 🔖 Bookmark: Creates a rich link to a web page, with automatic title retrieval.
├── ---
├── Horizontal Line: Inserts a `---` separation line.
├── HTML Comment
├── Table
├── Quote
├── ---
└── Tag (@@): Inserts a `@@` tag or transforms the selection into a tag.
├── Time: Inserts the current time (HH:MM).
├── ---
└── Emoji: Opens a submenu to insert emojis.

Integrations
├── Quote of the day: Inserts the quote of the day (retrieved from the Internet) into your note.
├── GPX Trace: Generates a map from a GPX trace file.
├── GPS Map: Generates and inserts a static map from GPS coordinates.
├── YouTube Video: Inserts a YouTube video or playlist with its thumbnail from a URL.

Help
├── Online Documentation: Opens this manual.
└── About: Displays information about the application, its version and its license.
```

## 13. File Export <a id="file-export"></a>

### 13.1. Export to HTML (single file) <a id="export-html-single"></a>
This function allows you to export the content of the currently open Markdown note into a static HTML file. It is ideal for quickly sharing a note or viewing it in a web browser.
*   **Access:** Via the `File > Export HTML...` menu.
*   **File name:** A default file name is suggested, based on the name of your note and the current date.
*   **Memorization:** The application remembers the last used export directory to facilitate future exports.
*   **Appearance:** The generated HTML file uses the same visual theme as your preview in the application.

### 13.2. Export to PDF (single file) <a id="export-pdf-single"></a>
Export the currently open Markdown note to a PDF document. This option is useful for archiving a specific note or sharing it in a universal format.
*   **Access:** Via the `File > Export to PDF...` menu.
*   **Technology:** The export is carried out using the `WeasyPrint` library, ensuring a faithful rendering of the content.
*   **Image management:** The paths of the images (including those located in the `Journal/images/` folder or its subdirectories) are correctly resolved, ensuring their display in the PDF.
*   **File name:** A default file name is suggested, based on the name of your note.
*   **Memorization:** The application remembers the last used export directory.

### 13.3. Export Journal to PDF <a id="export-journal-pdf"></a>
BlueNotebook allows you to create a professional and paginated PDF document of your journal, ideal for archiving, printing or sharing. This feature is accessible via `File > Export Journal PDF...`.

When you launch this action, a dialog box appears, giving you full control over the content of the export:
*   **Date range:** You can choose a start date and an end date to export only a specific period of your journal. By default, the application offers to export all of your notes.
*   **Document title:** Customize the title that will appear on the cover page of your PDF. By default, "BlueNotebook Journal" is used.
*   **Author's name:** You can add your name on the cover page.
*   **Cover photo:** Add a personal touch by selecting an image (PNG, JPG) that will be displayed on the cover page (max size 400x400px).
*   **Filtering by tag:** A drop-down list allows you to select a tag from those that have been indexed in your journal. If you choose a tag, only the notes containing this tag (and included in the date range) will be included in the export. Leave on "(No tag)" to export all notes of the period.

**Smart memorization:** To save you time, BlueNotebook remembers the last destination folder used, as well as the title and author name you entered for future exports.

#### Structure of the generated PDF:
1.  **Cover page:** Displays the title, the author's name, your photo (if chosen) or the BlueNotebook logo and the relevant date range. If a tag has been selected for the filter, it will also be mentioned on this page.
2.  **Journal notes:** Each daily note is added on a new page, respecting the formatting of the HTML preview.
3.  **Pagination:** All pages are numbered at the bottom for easy reading.

Once the options are chosen, the application generates the PDF file in the background. A flashing notification "Please wait..." appears in the status bar during the process.

### 13.4. Exporting the Journal to EPUB <a id="export-journal-epub"></a>
In addition to PDF, BlueNotebook allows you to transform your journal into a real digital book in EPUB format, compatible with all e-readers (Kobo, Kindle, etc.) and reading applications. This feature is accessible via `File > Export Journal EPUB...`.

The EPUB export is designed to offer an optimal reading experience and includes many advanced features:
*   **Similar configuration to PDF:** You can choose the date range, the title of the book, the author's name and a base image for the cover.
*   **Custom cover:** The application generates a professional book cover by combining the image you have chosen with the title, author and date range on an elegant background.
*   **Table of contents:** A clickable table of contents is automatically created, with an entry for each daily note, allowing you to easily navigate through your book.
*   **Image integration:** All images from your notes (local or web) are automatically downloaded, resized, compressed and integrated into the EPUB file. Your book is thus 100% autonomous.
*   **Tag index:** For thematic navigation, an index of all your tags (`@@tag`) is generated at the end of the book. Each tag is followed by a list of clickable links that take you directly to each occurrence of the tag in the journal.

The result is a high-quality `.epub` file, ready to be transferred to your e-reader for a comfortable rereading of your memories.

**Note:** To use this feature, the Python libraries `EbookLib`, `Pillow`, `BeautifulSoup4`, `requests` and `cairosvg` must be installed.

## 14. Backup and Restore of the Journal <a id="backup-restore"></a>
To ensure the security of your writings, BlueNotebook integrates simple tools to back up and restore your entire journal.

### Backing up your Journal (`File > Backup Journal...`)
This action allows you to create a complete backup copy of your journal directory.

1.  By clicking on this option, a dialog box will open.
2.  Choose a location and a name for your file. By default, a smart name including the date and time (e.g. `BlueNotebook-Backup-MyJournal-2025-09-26-15-45.zip`) is proposed to avoid overwriting old backups. The application also remembers the last folder you used to propose it to you next time.
3.  BlueNotebook will then compress all your note files (`.md`), as well as the index files, into a single `.zip` archive.

This is an excellent habit to take regularly, or before making major changes.

### Restoring your Journal (`File > Restore Journal...`)
If you need to revert to a previous version of your journal, or transfer it to a new computer, this function is there for you.

1.  Select the menu option. A window will ask you to choose the `.zip` archive file you want to restore.
2.  **Security action:** Before proceeding, BlueNotebook will automatically rename your current journal directory (for example, from `bluenotebook` to `bluenotebook.bak-20250923-153000`). **Your current data is not deleted.**
3.  A dialog box will ask you to confirm the operation, informing you of the name of the backup that has just been created.
4.  After confirmation, the content of the archive will be extracted, replacing the content of your journal directory.
5.  The application will inform you that the restoration is complete and will invite you to restart it to load the new journal.

## 15. Customization (Preferences) <a id="preferences"></a>
The Preferences window, accessible via `File > Preferences...`, is the control center for adapting BlueNotebook to your tastes. The changes are applied immediately after clicking "Validate".

### "General" Tab
*   **Application font:** Allows you to choose a font and size that will be applied to the entire application interface (menus, buttons, panels, etc.). This setting is ideal for improving readability or adapting the application to your visual preferences. A restart of the application is necessary for this change to be taken into account everywhere.
*   **Indexing statistics:** Check to permanently display the number of words and tags in the status bar.
*   **Tags to exclude from clouds:** Allows you to hide certain tags from the clouds without removing them from the search index.

### "Display" Tab
This tab is the heart of visual customization. It is itself divided into sub-tabs for the Editor, the Preview, etc.

#### 15.1 Editor Themes <a id="editor-themes"></a>
In the **"Markdown Editor"** sub-tab, you can change every aspect of the appearance of the writing area. BlueNotebook offers you total flexibility, whether you want to use a ready-made theme or create your own.

**Display line numbers? :**
Check this box to display a margin with line numbers to the left of the editor. This is practical for finding your way around long documents.

**Editor Themes (Light & Dark)**

For a quick setup, BlueNotebook includes themes developed by BlueNotebook as well as themes inspired by the excellent Markdown editor [Ghostwriter](https://ghostwriter.kde.org/en/).
*   **Select a theme:** Click this button to choose a ready-made theme (like "Classic Light" or "Classic Dark"). The selection instantly updates the colors in the preferences window so you can preview the result.

**Advanced customization and theme creation**

If you want to go further, you can adjust each color individually (background, text, headings, code, etc.) and even the font.
*   **Save as theme:** Once you have created a color palette that you like, click this button to save it as a new theme. It will then be available in the selection list.
*   **Display line numbers:** Check this box to display a margin with line numbers, practical for finding your way around long documents.

#### 15.2 HTML Preview Themes <a id="preview-themes"></a>
In the **"HTML Preview"** sub-tab, you can radically change the appearance of the preview panel, which will also affect the appearance of your **HTML exports**.

The appearance is controlled by CSS style sheets. To help you choose, a preview of the rendering is integrated directly into the preferences window.
*   **Select a CSS theme:** Click this button to choose a style from those offered. You will find light and dark themes inspired by the appearance of GitHub.
*   **Instant preview:** As soon as you select a theme from the list, a mini-preview window below is updated to show you the rendering of headings, paragraphs, links and code blocks. This allows you to judge the appearance before validating your choice.

The theme you validate is saved and will be automatically applied at each launch of BlueNotebook.

#### 15.3 PDF Export Themes <a id="pdf-themes"></a>
In the same way as for the HTML preview, you can now choose a CSS theme **specific to your PDF exports**. This feature is very useful for using a dark theme for on-screen editing, and a light theme, optimized for printing, for your PDF documents.
*   **Access:** Go to `Preferences > Display > PDF Export`.
*   **Select a CSS theme for the PDF:** Click this button to choose a style from the dedicated `resources/css_pdf/` folder. These themes are specially designed for the layout of PDF documents.
*   **Instant preview:** As for the HTML preview, a mini-window shows you the rendering of the selected theme before you validate your choice.

This separation gives you maximum flexibility so that your final documents have exactly the appearance you want, regardless of your daily work theme.

The **"Default display values"** button, present in the "Display" tab, resets all the options of this tab (editor colors, preview theme, etc.) to their factory values.

### "Panels" Tab
Control which panels are visible by default at application startup for a tailor-made workspace:
*   **"Notes" Panel (`F9`)**
*   **Navigation Panel (`F6`)**
*   **'Document Outline' Panel (`F7`)**
*   **'HTML Preview' Panel (`F5`)**
*   **'Reader' Panel (`F8`)**

### "Integrations" Tab
Manage additional features.

### The `settings.json` file
All the changes you make in the Preferences window are saved in a text file named `settings.json`. This file is the guardian of your personal configuration.

#### What is it for?
It keeps all your customization choices:
*   The fonts and colors of the editor.
*   The default visibility of the panels.
*   The words and tags you want to exclude from indexes or clouds.
*   Integration options, such as displaying the quote of the day.

Thanks to this file, BlueNotebook remembers your preferences every time you launch it. You can even save it to transfer your configuration to another computer.

#### Where is it?
The location depends on your operating system:
*   **On Linux:** `~/.config/BlueNotebook/settings.json` (where `~` is your home folder).
*   **On Windows:** `C:\Users\YourName\.config\BlueNotebook\settings.json`

**Warning:** It is not recommended to modify this file manually, unless you know what you are doing. A syntax error could lead to the reset of your preferences. Always use the Preferences window to modify the settings safely.

## 16. Keyboard Shortcuts <a id="shortcuts"></a>
| Action | Shortcut |
| :--- | :--- |
| New file | `Ctrl+N` |
| Open file | `Ctrl+O` |
| Save | `Ctrl+S` |
| Save as... | `Ctrl+Shift+S` |
| Quit application | `Ctrl+Q` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Search | `Ctrl+F` |
| Bold | `Ctrl+B` |
| Show/Hide details (Notes Panel) | `Ctrl+M` |
| Insert image | `Ctrl+I` |
| Toggle preview | `F5` |
| Toggle navigation | `F6` |
| Toggle document outline | `F7` |
| Toggle document reader | `F8` |
| Toggle notes explorer | `F9` |

## 17. Frequently Asked Questions (FAQ) <a id="faq"></a>
Here you will find the answers to the most frequently asked questions about using the application.

### Journal and Note Management
<dl>
    <dt>Q: How to create a new note for the day?</dt>
    <dd>**A:** It's automatic! At launch, BlueNotebook opens or creates a file for you for the current date (e.g. `20250927.md`). You just have to start writing.</dd>

    <dt>Q: How to add information to an existing note of the day?</dt>
    <dd>**A:** When you save (`Ctrl+S`) a note for a day that already exists, BlueNotebook asks you if you want to **"Append to the end"** or **"Replace"**. Choose "Append to the end" to keep your previous writings and add the new ones.</dd>

    <dt>Q: How can I view or edit a note from another day?</dt>
    <dd>**A:** You have two main options:
        1. **Use the calendar** in the Navigation panel on the left. The days with a note are in blue. Click on a date to open the corresponding note.
        2. Use the `File > Open` (`Ctrl+O`) menu to manually browse your journal folder.
    </dd>
</dl>

### The Markdown Editor
<dl>
    <dt>Q: What is Markdown?</dt>
    <dd>**A:** Markdown is a very simple syntax for formatting text. Instead of clicking buttons, you use symbols to indicate the formatting, which allows you to not leave your keyboard. The preview on the right shows you the result in real time.</dd>

    <dt>Q: How to make text bold or italic?</dt>
    <dd>**A:** For **bold**, surround your text with two asterisks: `**bold text**`. For *italic*, surround it with a single asterisk: `*italic text*`. You can also use the `Format > Text Style` menu.</dd>
</dl>
<dl>
    <dt>Q: Is there a quick way to format text without using the menus?</dt>
    <dd>**A:** Yes! In addition to keyboard shortcuts, you can now **right-click** on text you have selected. A context menu will appear, giving you direct access to formatting options, including submenus for **Headings**, **Lists**, **Text Style** and **Code**.</dd>
</dl>
<dl>
    <dt>Q: What is the difference between "Markdown Link" and "URL/Email Link"?</dt>
    <dd>**A:**
        *   **Markdown Link**: Opens a dialog box to create a link with custom text (e.g. `Visit our site`). If you have not selected anything, the fields are empty. If you have selected text, it is used as the link text.
        *   **URL/Email Link**: Is a quick action. Select a URL or an email address in your text, and this action will enclose it in angle brackets (`<https://example.com>`) to make it automatically clickable in the preview.
    </dd>
</dl>
<dl>
    <dt>Q: How to clean up a badly formatted paragraph (for example, after a PDF conversion)?</dt>
    <dd>**A:** Select the paragraph containing line breaks or superfluous spaces, right-click, then choose `Formatting > Clean paragraph`. The application will merge the lines into a single fluid paragraph and remove the extra spaces.</dd>
</dl>

### Search and Navigation
<dl>
    <dt>Q: How to quickly find information in my journal?</dt>
    <dd>**A:** Use the search field located in the Navigation panel, under the calendar. You can search for tags there.</dd>

    <dt>Q: How to search for a specific tag (e.g. `@@project`)?</dt>
    <dd>**A:** Simply type `@@project` in the search field and press `Enter`. The search is case-insensitive and accent-insensitive: searching for `@@météo` will find the tag `@@METEO`. You can also click the `▼` button to see the list of all your tags (which are displayed in their normalized, uppercase form).</dd>

    <dt>Q: What are the "Tag/Word Clouds" for?</dt>
    <dd>**A:** They show you the tags and words you use most frequently. It's a way to see the main themes of your journal. **Click on a word or a tag in a cloud to immediately launch a search for that term!**</dd>

    <dt>Q: What happens when I click on a search result?</dt>
    <dd>**A:** The application opens the corresponding note and positions the cursor **directly at the line** where the occurrence was found. It's an ultra-fast way to find the exact context of a piece of information.</dd>
</dl>

### Backup and Security
<dl>
    <dt>Q: How to make a full backup of my entire journal?</dt>
    <dd>**A:** Go to `File > Backup Journal...`. This will create a `.zip` archive containing all your notes and index files. It's a good practice to do this regularly.</dd>

    <dt>Q: How to restore my journal from a backup?</dt>
    <dd>**A:** Use `File > Restore Journal...`. The procedure is very secure: before restoring, BlueNotebook renames your current journal to make a backup of it (e.g. `MyJournal.bak-20250923-153000`). **Your current data is not deleted.** You will simply have to restart the application after the restoration.</dd>
</dl>

### Export and Share
<dl>
    <dt>Q: How can I share one of my notes?</dt>
    <dd>**A:** The best way to share a note is to export it to HTML. Go to `File > Export HTML...`. A dialog box will open proposing a smart file name (`BlueNotebook-name-date.html`) and will remember the last folder you used. The generated HTML file will use the same visual theme as your preview in the application.</dd>

    <dt>Q: How can I create a PDF of all or part of my journal?</dt>
    <dd>**A:** Use the `File > Export Journal PDF...` function. It is a powerful tool that allows you to create a professional PDF document. A dialog box will allow you to:
        *   Select a **date range** to include only certain notes.
        *   Define a **title**, an **author name** and even a **cover image** for the cover page.
    The application remembers your choices (folder, title, author) to save you time on future exports. The result is a paginated document, perfect for archiving or printing.</dd>

    <dt>Q: How to turn my journal into a digital book (EPUB)?</dt>
    <dd>**A:** BlueNotebook offers a very complete EPUB export function via `File > Export Journal EPUB...`. It transforms your journal into a real digital book for e-readers. In addition to the date, title and author options, the EPUB export includes:
        *   A **custom cover** generated automatically.
        *   A clickable **table of contents**.
        *   The **integration of all your images**, resized and compressed.
        *   A **tag index** at the end of the book for navigation by theme.
    This is the ideal solution for a comfortable rereading of your memories on any e-reader.</dd>
</dl>

### Customization and Themes
<dl>
    <dt>Q: How can I create my own color theme for the BlueNotebook Markdown editor?</dt>
    <dd>**A:** It's very simple!
        1. Go to `Preferences > Display > Markdown Editor`.
        2. Go to `Preferences > Display > Markdown Editor`.
        3. Adjust the different colors (background, text, headings, etc.) and the font until you get a result that you like.
        4. Click the `Save as theme` button.
        5. Give a name to your theme (e.g. "My Dark Theme") and validate. 
        Your theme is now saved and you can select it at any time from the `Select a theme` button.
    </dd>

    <dt>Q: How to modify an existing theme?</dt>
    <dd>**A:**
        1. Open the `Preferences > Display > Markdown Editor`.
        2. Open the `Preferences > Display > Markdown Editor`.
        3. Click on `Select a theme` and choose the theme you want to modify. Its colors are then loaded into the interface.
        4. Change the colors or the font you want to adjust.
        5. Click on `Save as theme`. You can either give it a new name to create a variation, or use the same name to overwrite and update the existing theme.
    </dd>
</dl>

## 18. Main Python Packages <a id="packages"></a>
Here is a list of the main Python libraries that power the BlueNotebook project, with an explanation of their role.

### Graphical Interface and Base Components
*   **PyQt5**: This is the heart of the application. This framework is used to create the entire user interface, from windows to buttons, through menus and panels. The `QWebEngineWidgets` part is specifically used for the real-time HTML preview.
    *   **Author:** Riverbank Computing
    *   **Official Site:** [www.riverbankcomputing.com](https://www.riverbankcomputing.com)

### Markdown and HTML Processing
*   **python-markdown**: This library is essential for converting the text you write in Markdown to the HTML format that is displayed in the preview panel.
    *   **Author:** Waylan Limberg and contributors
    *   **GitHub Repository:** [github.com/Python-Markdown/markdown](https://github.com/Python-Markdown/markdown)
*   **Pygments**: Used by `python-markdown` to perform syntax highlighting of code blocks in the HTML preview, which makes the code much more readable.
    *   **Author:** Georg Brandl and contributors
    *   **GitHub Repository:** [github.com/pygments/pygments](https://github.com/pygments/pygments)
*   **pymdown-extensions**: Provides additional Markdown features that are not in the basic version, such as highlighting (`==text==`) or strikethrough text (`~~text~~`).
    *   **Author:** Isaac Muse
    *   **GitHub Repository:** [github.com/facelessuser/pymdown-extensions](https://github.com/facelessuser/pymdown-extensions)
*   **BeautifulSoup4 (`bs4`)**: A very powerful tool used in several places to parse HTML code. It is used in particular to extract the quote of the day, but also to find and process images and tags during the EPUB export.
    *   **Author:** Leonard Richardson
    *   **Official Site:** [www.crummy.com/software/BeautifulSoup/](https://www.crummy.com/software/BeautifulSoup/)

### Document Export
*   **WeasyPrint**: This is the library that allows to generate high-quality PDF exports. It takes the HTML content of the journal and transforms it into a paginated PDF document.
    *   **Author:** Kozea
    *   **GitHub Repository:** [github.com/Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint)
*   **EbookLib**: The central library for creating files in EPUB format. It manages the assembly of chapters, the creation of the table of contents, the integration of the cover and images.
    *   **Author:** Aleksandar Erkalovic
    *   **GitHub Repository:** [github.com/aerkalov/ebooklib](https://github.com/aerkalov/ebooklib)

### PDF Management
*   **PyMuPDF (`fitz`)**: An extremely fast and versatile library for reading, rendering and extracting data from PDF files. It is at the heart of the PDF reader, managing the display of pages, the extraction of the table of contents and text selection.
    *   **GitHub Repository:** [github.com/pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF)

### Document Conversion
*   **markitdown**: A Microsoft library used for the new PDF to Markdown conversion feature. It analyzes the structure of the PDF to generate an equivalent Markdown file.
    *   **GitHub Repository:** [github.com/microsoft/markitdown](https://github.com/microsoft/markitdown)

### Image Manipulation
*   **Pillow** (a fork of PIL): Used for everything related to image manipulation. It is mainly used to create the composite cover image for the EPUB export (by combining an image and text) and to resize/compress images before including them in the digital book.
    *   **Author:** Alex Clark and contributors
    *   **GitHub Repository:** [github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow)
*   **cairosvg**: A specialized library that allows to convert images in SVG vector format to PNG format, as Pillow cannot read SVG natively. This is crucial for the EPUB export.
    *   **Author:** Kozea
    *   **GitHub Repository:** [github.com/Kozea/cairosvg](https://github.com/Kozea/cairosvg)

### Integrations and Network
*   **requests**: This is the reference library for making requests on the internet. It is used to retrieve the quote of the day, information on YouTube videos, weather data, and to download images from URLs during the EPUB export.
    *   **Author:** Python Software Foundation (current maintainer)
    *   **GitHub Repository:** [github.com/psf/requests](https://github.com/psf/requests)
*   **geopy**: Used for geolocation, especially to convert city names into geographic coordinates (latitude and longitude) for the "Astro of the Day" integration.
    *   **Author:** Geopy Contributors
    *   **GitHub Repository:** [github.com/geopy/geopy](https://github.com/geopy/geopy)

---
*This manual was written for BlueNotebook V4.1.54*

If you encounter errors or malfunctions, you can notify them on the [developer's site](https://github.com/lephotographelibre/BlueNotebook/issues).

BlueNotebook is free software distributed under the terms of the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html).
