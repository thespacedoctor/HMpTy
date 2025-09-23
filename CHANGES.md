
## Release Notes

**v1.7.2 - September 22, 2025**

* **REFACTOR** more optimisations

**v1.7.1 - September 22, 2025**

* **FIXED** small fix to Numpy 2.* compatibility

**v1.7.0 - September 22, 2025**

* **REFACTOR** defaulting to htmid mesh 7 for matching 2 lists of coordinates together (faster than the original 12)
* **REFACTOR** optimising the HTM level targets for various conesearch radius sizes
* **REFACTOR** speed optimisations for DB queries
* **ENHANCEMENT** HTMID07 add to 10, 13 and 16 when adding indexes to db tables

**v1.6.1 - July 17, 2025**

* **FIXED** small hmpty fix for finding intersecting trixels 

**v1.6.0 - May 6, 2025**

* **FIXED** compatibility with Python=3.12

**v1.5.10 - October 12, 2023**

* **ENHANCEMENT** updating conesearch to work for bespoke HTM database IDs

**v1.5.8 - September 6, 2022**

* **FIXED** fixed issue with ISO C++17 not allow dynamic exception specifications. Install on Ubuntu 22.04 now works.

**v1.5.6 - May 10, 2022**

* **FIXED** doc fixes

**v1.5.5 - December 8, 2021**

* **FIXED** Install on macOS monterey

**v1.5.4 - August 16, 2021**

* **FIXED** Command-line tools

**v1.5.3 - June 23, 2020**

* **FIXED** When matching 2 lists of coordinates, if a list location was matched against more than one item in the second match list the angular separation of the first match got over-written by the second match.

**v1.5.1 - May 19, 2020**

* **FIXED** MacOS install was needlessly involved.

**v1.5.0 - May 8, 2020**


* Now compatible with python 3.\*
