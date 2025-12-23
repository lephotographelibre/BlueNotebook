# **BlueNotebook - Technical Documentation**


**Document Version:** V2.6.2
**Date:** October 17, 2025
**Author:** Jean-Marc Digne

## 1. Introduction and Product Vision

`BlueNotebook` is a cross-platform desktop application (Windows, Linux) **designed for note-taking and personal journaling**. Its fundamental principle is to provide a text-centric writing environment based on **Markdown** syntax, while offering rich features for navigation, search, and customization. This application was inspired by the [rednotebook](https://github.com/jendrikseipp/rednotebook) software developed by Jendrik Seipp.

The application is aimed at users who appreciate the simplicity and portability of plain text format but want to benefit from a modern graphical interface and advanced tools to organize and retrieve their information.

The product vision is to combine the best of both worlds:

*   **Data Longevity:** The journal is a simple folder of `.md` files, readable by any text editor.
*   **Efficiency of a Dedicated Application:** Calendar-based navigation, full-text search, tag indexing, real-time preview, professional exports (PDF, EPUB), and web service integrations.

Copyright (C) 2025 Jean-Marc DIGNE (Word indexing and search removed in V3.1.1)

*This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.*

[![License GNU](https://img.shields.io/github/license/lephotographelibre/BlueNotebook)](https://www.gnu.org/licenses/>)



## **Table of Contents**
1.  [Introduction and Product Vision](#1-introduction-and-product-vision)
2.  [Software Architecture](#2-software-architecture)
    *   [2.1. Overview](#21-overview)
    *   [2.2. Component Description](#22-component-description)
3.  [Technologies and Dependencies](#3-technologies-and-dependencies)
4.  [Detailed Feature Description](#4-detailed-feature-description)
    *   [4.1. Application Core](#41-application-core)
    *   [4.2. User Interface (GUI)](#42-user-interface-gui)
    *   [4.3. External Integrations](#43-external-integrations)
5.  [Data Management](#5-data-management)
    *   [5.1. The Journal Directory](#51-the-journal-directory)
    *   [5.2. Indexing Files](#52-indexing-files)
    *   [5.3. Configuration Files](#53-configuration-files)
6.  [Recommended Improvements](#6-recommended-improvements)
    *   [6.1. Technical Improvements](#61-technical-improvements)
    *   [6.2. Functional Improvements](#62-functional-improvements)
7.  [Conclusion](#7-conclusion)

---

## 2. Software Architecture

### 2.1. Overview

The application is developed in Python 3 and follows a modular architecture that clearly separates responsibilities. The project structure is organized as follows:

```
bluenotebook/
├── core/         # Business logic, independent of the interface
├── gui/          # All graphical interface components (PyQt5)
├── integrations/ # Modules for interacting with external services
├── resources/    # Static files (icons, templates, CSS, themes)
├── tests/        # Unit tests
└── main.py       # Application entry point
```

This separation allows for good maintainability and facilitates the independent evolution of different parts of the application. For example, the indexing logic in `core` could be reused with another interface (web, mobile), and the `gui` interface could be modified without impacting how files are managed.

### 2.2. Component Description

#### `main.py`

The application's entry point. It is responsible for:

*   Initializing `QApplication`.
*   Managing internationalization (i18n) for Qt components.
*   Parsing command-line arguments (e.g., `--journal`).
*   Instantiating and displaying the main window (`MainWindow`).

#### `core/` (Business Logic)

This package contains the fundamental logic of the application, with no dependency on the graphical interface.

*   **`settings.py` (`SettingsManager`)**: Manages loading and saving user preferences from a `settings.json` file located in the system's configuration directory (`~/.config/BlueNotebook`).
*   **`file_handler.py` (`FileHandler`)**: Provides static methods for reading and writing files, ensuring UTF-8 encoding.
*   **`markdown_parser.py` (`MarkdownParser`)**: Wraps the `markdown` library to convert Markdown text to HTML.
*   **`tag_indexer.py` (`TagIndexer`)** and **`word_indexer.py` (`WordIndexer`)**: Crucial components for the search functionality. They operate asynchronously (via `QRunnable`) to scan the journal directory, extract tags (`@@tag`) and words, and generate index files (`index_tags.json`, `index_words.json`).
*   **`quote_fetcher.py` (`QuoteFetcher`)**: Retrieves the "quote of the day" by scraping the `citations.ouest-france.fr` website. Includes a caching mechanism to avoid repeated requests.
<!-- Word indexing and search removed in V3.1.1 -->
#### `gui/` (Graphical Interface)

This package contains all the widgets and windows that make up the user interface, built with PyQt5.

*   **`main_window.py` (`MainWindow`)**: The central class of the application. It assembles all other interface components, manages menus, actions, the status bar, and orchestrates communication between the different panels.
*   **`editor.py` (`MarkdownEditor`)**: The core of the user experience. It is a composite widget that includes:
    *   `QTextEditWithLineNumbers`: A custom `QTextEdit` with line number display.
    *   `MarkdownHighlighter`: A `QSyntaxHighlighter` that applies real-time syntax highlighting to the Markdown text.
*   **`preview.py` (`MarkdownPreview`)**: Displays the HTML rendering of the Markdown text using `QWebEngineView`. It manages the application of CSS themes.
*   **`navigation.py` (`NavigationPanel`)**: The left-side panel, which contains the calendar for time-based navigation, the search field, and tag and word clouds.
*   **`outline.py` (`OutlinePanel`)**: Displays a clickable tree of the current document's headings (H1, H2, etc.).
*   **`preferences_dialog.py` (`PreferencesDialog`)**: A complex window allowing the user to customize the appearance (themes, fonts, colors) and behavior of the application in detail.
*   Other widgets: `date_range_dialog.py` (for exports), `search_results_panel.py`, `tag_cloud.py`.

#### `integrations/` (External Services)

This package handles communication with external APIs or processes.

*   **`pdf_exporter.py`** and **`epub_exporter.py`**: Contain the logic for converting the entire journal into PDF or EPUB files, using `WeasyPrint` and `EbookLib` respectively. They run in the background (`QRunnable`) to avoid blocking the interface.
*   **`weather.py`**: Queries the `WeatherAPI.com` API to retrieve weather data.
*   **`youtube_video.py`**: Extracts the ID and title of a YouTube video from its URL.
*   **`gps_map_generator.py`**: Uses `staticmaps` to generate a static map image and `geopy` to get the name of a place from GPS coordinates.
*   **`image_exif.py`**: Extracts EXIF metadata from images (GPS, date, camera) using `Pillow`.

## 3. Technologies and Dependencies

The application is built on a set of robust and proven Python libraries.

*   **Language**: Python (version 3.13.5 is targeted in the launch scripts).
*   **Graphical Interface Framework**:
    *   **PyQt5**: Used to build the entire desktop interface.
    *   **PyQtWebEngine**: Used for the real-time HTML preview panel.

*   **Main Dependencies** (from `requirements.txt`):
    *   `markdown` & `pymdown-extensions`: For converting Markdown text to HTML.
    *   `Pygments`: For syntax highlighting of code blocks in the HTML preview.
    *   `requests`: For all HTTP requests (weather, quote, YouTube videos).
    *   `beautifulsoup4` & `lxml`: For HTML parsing (scraping the quote of the day, processing exports).
    *   `appdirs`: For locating the application's cache directory in a cross-platform way.

*   **Optional Dependencies** (required for certain features):
    *   `WeasyPrint`: Needed for exporting the journal to PDF format.
    *   `EbookLib`, `Pillow`, `cairosvg`: Needed for exporting to EPUB format.
    *   `staticmaps`, `geopy`: Needed for generating GPS maps.

## 4. Detailed Feature Description

### 4.1. Application Core

*   **File-Based Journal Management**: The application is centered around a "journal directory." Each entry corresponds to a `YYYYMMDD.md` file. This approach ensures that the user's data is transparent, portable, and durable.
*   **Asynchronous Indexing**: On startup and when a journal is selected, the application launches background tasks to index all words and tags (`@@...`). This allows for almost instantaneous search without ever blocking the user interface. Indexes are stored in JSON files for quick reloads.
*   **Centralized Settings Management**: All user preferences (color themes, fonts, panel visibility, API keys) are managed by the `SettingsManager` class and stored in a single `settings.json` file, which facilitates backup and portability of the configuration.

### 4.2. User Interface (GUI) (Word indexing and search removed in V3.1.1)

*   **Advanced Markdown Editor**:
    *   **Real-Time Syntax Highlighting**: The `MarkdownHighlighter` analyzes the text as you type to color headings, bold, italics, lists, code, links, tags, etc.
    *   **Extreme Customization**: The user can change the font and color of each syntax element via the preferences window.
    *   **Line Numbers**: An optional margin displays line numbers.
*   **Real-Time HTML Preview**:
    *   The preview panel updates automatically a few milliseconds after the text is modified.
    *   It uses the same rendering engine as a modern browser (`QWebEngine`), ensuring a faithful display.
    *   CSS themes (inspired by GitHub, etc.) allow for complete customization of the preview's appearance.
*   **Smart Navigation**:
    *   **Calendar**: Highlights days where a note was written, allowing direct access.
    *   **Word and Tag Clouds**: Generated from the indexes, they provide an overview of the journal's recurring themes. Clicking on a term initiates a search.
    *   **Full-Text Search**: The search field allows finding tags throughout the entire journal. Results are displayed with their context, and clicking a result opens the corresponding file directly to the correct line.
*   **Modular Panels**: The Navigation, Outline, and Preview panels can be shown or hidden (via buttons or the `F5`-`F7` keys) to create a personalized workspace.

### 4.3. External Integrations

*   **PDF and EPUB Export**:
    *   Generation of high-quality documents including a cover page, a table of contents, pagination, and proper image handling.
    *   The EPUB export goes further by integrating a clickable tag index and embedding all images for total portability.
*   **Backup and Restore**: The user can create a complete `.zip` archive of their journal and restore it, with a security mechanism that backs up the existing journal before overwriting it.
*   **Content Enrichment**:
    *   **Weather**: Inserts an HTML block with current weather conditions.
    *   **YouTube Video**: Inserts a clickable thumbnail and a `@@Video` tag from a simple URL.
    *   **GPS Maps**: Generates a static map from coordinates, with reverse lookup of the location name.
    *   **EXIF Data**: Extracts and formats metadata from a photo (location, date, camera) to insert it under the image.

## 5. Data Management

### 5.1. The Journal Directory
This is the main folder chosen by the user. It contains:
*   Daily notes in `YYYYMMDD.md` format.
*   An `images/` subfolder where all inserted local images are copied.
*   The index files generated by the application.

### 5.2. Indexing Files
Generated and updated automatically in the journal directory:
*   `index_tags.json`: A dictionary where each key is a tag and the value contains the number of occurrences and a detailed list of each occurrence (file, line, context, date).
*   `index_tags.csv`: An alternative version of the tag index in CSV format for potential external use.

### 5.3. Configuration Files
*   `~/.config/BlueNotebook/settings.json`: A single file containing all user preferences (fonts, colors, themes, API keys, etc.).
*   `resources/templates/`: Contains note templates (`.md`) that the user can create and use.
*   `resources/themes/`: Contains the editor's color themes in JSON format.
*   `resources/css_preview/`: Contains CSS themes for the preview panel.

## 6. Recommended Improvements

### 6.1. Technical Improvements

1.  **Modernize Dependency Management**: Migrate from `requirements.txt` to a modern tool like [Poetry](https://python-poetry.org/) or [PDM](https://pdm-project.org/) with a `pyproject.toml` file. This would improve dependency management, build reproducibility, and the separation of development dependencies.

2.  **Improve Test Coverage**: The project has a test base for the `core` components. It would be beneficial to:
    *   Extend unit tests to cover all business logic.
    *   Introduce integration tests.
    *   Implement tests for the graphical interface using `pytest-qt` to simulate user interactions and verify UI behavior.

3.  **Refactoring and Typing**:
    *   Strengthen static typing with `mypy` across the entire codebase to reduce runtime errors and improve readability.
    *   Some parts of `main_window.py` are very long. Consider delegating certain logics (e.g., export management, backups) to dedicated classes to lighten `MainWindow` and better adhere to the single-responsibility principle.

4.  **Set Up CI/CD**: Integrate a continuous integration pipeline (e.g., GitHub Actions) to automate the execution of tests, linting (`ruff`, `black`), and typing (`mypy`) on each commit.

5.  **Optimize Indexing**: Indexing is already asynchronous, which is excellent. For very large journals, a database approach (e.g., SQLite with an FTS5 extension) could be considered instead of JSON files, which could offer better read and write performance for incremental updates.

### 6.2. Functional Improvements

1.  **Cloud Synchronization**: This is the most requested feature for this type of application. Allowing users to synchronize their journal directory with services like Dropbox, Google Drive, or Nextcloud would significantly increase the application's value.

2.  **Companion App (Mobile/Web)**: Develop a lightweight mobile app (or a PWA) that could read and edit the `.md` files of the journal synchronized via the cloud.

3.  **Editor Enhancements**:
    *   Integrate a spell checker.
    *   Add editing modes (e.g., "Focus" mode that fades out inactive text, "Typewriter" mode where the active line stays centered).
    *   Support for Vim/Emacs keybindings.

4.  **Plugin/Extension System**: Create a plugin architecture to allow the community (or the user) to develop their own integrations (e.g., new weather services, export to other formats, etc.) without modifying the application's core.

5.  **Note Encryption**: Offer an option to encrypt notes (either per file or the entire journal) with a password to ensure data confidentiality.

6.  **Advanced Search**: Enhance the search engine with Boolean operators (`word1 AND word2`, `tag:project NOT tag:archive`), date range search, etc.

## 7. Conclusion

BlueNotebook is already a very complete and well-designed journaling application. Its modular architecture, transparent data management, and rich features (especially the PDF/EPUB exports and integrations) make it a powerful tool.

The technical recommendations aim to modernize its foundations to ensure its longevity and maintainability, while the functional recommendations suggest ways to align it with the expectations of users of modern note-taking applications. The project has a solid base on which to build for future versions.
