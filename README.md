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
## About The Project

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
* Adobe Flash Player [Download from Adobe](https://get.adobe.com/flashplayer/)
* If python is not installed follow [Properly Installing Python](https://docs.python-guide.org/starting/installation/).
* python selenium module and schedule module
```sh
pip3 install selenium schedule
```
*if you got "pip3 not found", try:*
```sh
sudo apt install python3-pip
```
then try to install selenium and schedule with pip again

### Installation

1. Clone the repo
```sh
git clone https://github.com/UZziell/moodle-bot.git
```
2. Copy downloaded firefox to moodle-bot directory (FF executable must be at `moodle-bot/firefox/firefox`)
3. Copy `geckodriver` file to `moodle-bot/drivers/` directory
4. Copy `lib*flashplayer.so` also to `moodle-bot/drivers/`
5. rename `secrets.py.example` to `secrets.py` and fill it with your moodle username and password.



<!-- USAGE EXAMPLES -->
## Usage

Well this is the ugly part. To give the script your moodle course details(day of week and hour) you should manually
edit the moodle-bot.py. In schedule_me function add entries per course with following format:

`schedule.every().{DAY OF THE WEEK}.at("HH:MM").do(func, at_course="PARTIAL COURSE NAME")`

For a course that has classes every other week, add the entry to `# Odd weeks` or `# Even week`

Finally run the script:
```sh
~$ cd moodle-bot
~/moodle-bot$ python moodle_bot.py
```