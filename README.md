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

A simple bot that automatically logs in to Moodle learning management system then attends Adobe online class.
 It uses Selenium WebDriver and schedule module. 

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites
Download all prerequisites based on you operating system.
* firefox (version < 69, since from 69 it does not support allowing flash player without asking.
I tested with version 68.0-64bit).
 After extracting firefox, you could optionally delete updater binary.
  I could not figure out how to stop firefox from automatically update itself except deleting updater binary.
        [Download From ftp.mozilla.org](https://ftp.mozilla.org/pub/firefox/releases/)

* geckodriver - version 0.26 recommended  [Download from github.com/mozilla](https://github.com/mozilla/geckodriver/releases/tag/v0.26.0)
* Adobe Flash Player for firefox [Download from Adobe](https://get.adobe.com/flashplayer/)
* If python is not installed follow [Properly Installing Python](https://docs.python-guide.org/starting/installation/).
* python selenium module and schedule module

### Installation
#### Linux
1. Clone the repo or download the zip file
    ```sh
    git clone https://github.com/UZziell/moodle-bot.git
    ```
2. Extract and copy downloaded firefox to moodle-bot directory (FF executable must be at `moodle-bot/firefox/firefox`)
3. Copy `geckodriver` file to `moodle-bot/drivers/` directory
4. Copy `lib*flashplayer.so` also to `moodle-bot/drivers/`
5. install selenium and schedule modules
    ```sh
    pip3 install selenium schedule
    ```
6. rename `secrets.py.example` to `secrets.py` and fill it with your moodle username and password.

#### windows
1. Clone the repo or download the zip file
    ```sh
    git clone https://github.com/UZziell/moodle-bot.git
    ```
2. Install downloaded firefox to `moodle-bot/firefox` directory (FF executable must be at `moodle-bot/firefox/firefox`)
3. Extract and copy `geckodriver.exe` file to `moodle-bot/drivers/` directory
4. Install Adobe flash player
5. install selenium and schedule modules
    ```sh
    pip3 install selenium schedule
    ```
6. rename `secrets.py.example` to `secrets.py` and fill it with your moodle username and password.

<!-- USAGE EXAMPLES -->
## Usage

* Add your weekly schedule to script

Well this is the ugly part. To give the script your moodle course details(day of week and hour) you should manually
edit the moodle-bot.py. In schedule_me function add entries per course with following format:

    schedule.every().DAY OF THE WEEK.at("HH:MM").do(func, at_course="COURSE NAME", for_duration=M)

example:
    ```schedule.every().saturday.at("08:00").do(func, at_course="زبان فا", for_duration=95)```


For a course that has classes every other week, add the entry to `# Odd weeks` or `# Even week`

* Finally run the script:
    ```sh
    ~$ cd moodle-bot
    ~/moodle-bot$ python3 moodle_bot.py
    ```
optionally you can pass -l or --headless to start browser in headless mode
```sh
~/moodle-bot$ python3 moodle_bot.py --headles
```