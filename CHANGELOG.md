
# Change Log
All notable changes to Pipeline will be documented in this file.

## [2.8.4 / 11/11/18]
* [fix] bug when version got reordered and causing inablity to save new versions

## [2.8.3 / 22.02.2018] Hotfix

* [fix] bug when loading project that has no users
* [fix] cosmetics bug
* [fix] bug with library trying to populate nothing at startup

## [2.8.0 / 21.02.2018]

* [added] Added new permissions control system
* [added] Added support for MayaAscii & MayaBinary (on a per task level and even version-master!)
* [added] Note editor is now more comfortable
* [added] New CSS with a more responsive feel
* [added] Add masters origin indicator
* [fixed] Navigate to current open file on pipeline load is working again
* [fixed] Load preset from file dialog spontaneously closing or not showing up at all
* [fixed] Load project dialog spontaneously closing or not showing up at all
* [fixed] Reload pipeline working again
* [removed] The file lock system was removed, unfortunately it was causing more pain then assistance

## [2.7.0 / 7.10,2017]

* [added] multithreaded navigation!
* [fixed] Library will no do batter work on suggesting hints

## [2.6.11 / 23.9.2017]

* [added] option for 'step' increment when generating categories
* [added] saving master added an option to not open the file 
* [added] trailing zeros on preset generation
* [added] option to use '-' for object names
* [fixed] import action is now preserving references
* [fixed] bug when closing the dock and trying to call it again throws a 'internal c++ object already deleted'

## [2.3.8 / 27.3.2017]

* [added] Save version script to map to a Hotkey 
* [fixed] Increased stability by keeping track of the main UI instance
* [fixed] Multiple typo's 

## [2.2.6 / 24.3.2017]

* [fixed] Playblast can now handle windows machines with no H.264 installed
* [fixed] Component with .avi and .mov playblasts were causing exceptions
* [fixed] Preset generator sliders were limited up to 99

## [2.2.3 / 18.3.2017]

* [added] Publishing automation
* [added] Add saved files to maya's 'recently opened' list
* [fixed] Project without users dose not get admin privileges
* [fixed] Fix critical bug when loading maya files with error, this drives the UI crazy sometimes
* [fixed] Versions table ui issue - missing scrollbar

## [2.0.0 / 4.3.2017]

* Dynamic project structure and naming conventions.
* Folder structure templates and templates editor.
* Support for underscores in item names.
* Playblasts with masters.
* Quick projects switcher.
* New interface.
* New documentation.
* Automatic update checker.
* Supported in Maya 14-17 Win/OSX. (Maya 2017 update 2+)