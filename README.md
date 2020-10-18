# moodle-bot

<!-- TABLE OF CONTENTS 
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements) -->


<!-- ABOUT THE PROJECT -->
## About

A simple bot that automatically logs in to Moodle learning management system then attends Adobe online classes.
 It uses Selenium WebDriver and schedule module. 


## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites
Download all prerequisites based on you operating system.
* firefox (version < 69, since from 69 it does not support allowing flash player without asking.
I tested with version 68.0-64bit). [Download From ftp.mozilla.org](https://ftp.mozilla.org/pub/firefox/releases/)

* geckodriver - version 0.26 recommended  [Download from github.com/mozilla](https://github.com/mozilla/geckodriver/releases/tag/v0.26.0)
* Adobe Flash Player for firefox [Download from Adobe](https://get.adobe.com/flashplayer/)
* If python is not installed follow [Properly Installing Python](https://docs.python-guide.org/starting/installation/).
* python selenium module and schedule module

### Installation
1. Clone the repo or download the zip file
    ```sh
    git clone https://github.com/UZziell/moodle-bot.git
    ```
2. install selenium and schedule modules
    ```sh
    pip3 install selenium schedule
    ```
#### Linux

3. Extract and copy downloaded firefox to moodle-bot directory (FF executable must be at `moodle-bot/firefox/firefox`)
4. Copy `geckodriver` file to `moodle-bot/drivers/` directory
5. Copy `lib*flashplayer.so` also to `moodle-bot/drivers/`

#### windows

3. Install downloaded firefox to `moodle-bot/firefox` directory (FF executable must be at `moodle-bot/firefox/firefox`)
4. Extract and copy `geckodriver.exe` file to `moodle-bot/drivers/` directory
5. Install Adobe flash player

\* **NOTE** \*:  After extracting or installing firefox, you may probably want to delete updater executable.
 Despite of setting `app.update.auto` and `app.update.enabled` to `False` firefox keeps automatically updating itself.
 So search for `updater` and `maintainer` executables in firefox directory and **delete** them.
<!-- USAGE EXAMPLES -->
## Usage
1. You can whether rename `secrets.py.example` to `secrets.py` and fill it with your moodle username and password\
    or\
    supply --username YOUR_USERNAME and --password YOUR_PASSWORD command line arguments when running the script.

2. Add your weekly schedule to script

    Well this is the ugliest part. To give the script your moodle course details(day of week and hour) you should manually
    edit the `schedule_me()` function in `moodle-bot.py`. So in `schedule_me()` function add entries per course with following format:
    
        schedule.every().DAY_OF_THE_WEEK.at("HH:MM").do(func, at_course="COURSE NAME", for_duration=Minutes)
        
   `DAY_OF_THE_WEEK` is the week day of the class\
   `HH:MM` *str*  is the start time of the class\
   `COURSE NAME` *str*  is full or partial name of the course. For example, for the course `مباني داده کاوي` you could simply set it to `داده`\
   `Minutes` *int*   is how long the bot will be online in the class
    
    example:\
        ```schedule.every().saturday.at("08:00").do(func, at_course="زبان فا", for_duration=95)```
    
    For a course that has classes every other week, add the entry to `# Odd weeks` or `# Even week`

3. Finally run the script:
    ```sh
    ~$ cd moodle-bot
    ~/moodle-bot$ python3 moodle_bot.py
    ```
    optionally you can pass -l or --headless command line argument to start browser in headless mode
    ```sh
    ~/moodle-bot$ python3 moodle_bot.py --headless
    ```
<!--
## Contribution
Contributions are genuinely welcomed.
-->   