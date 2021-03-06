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

A simple bot that automatically logs in to Moodle learning management system and attends Adobe online classes. It uses
python's Selenium WebDriver and schedule module.

## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

Download and install all prerequisites based on you operating system.

* You need a browser, and its relevant driver so weather download and install:
  * chromium (version 88.0.4324.182 tested) [chromium.org](https://www.chromium.org/getting-involved/download-chromium) + chromedriver [chromedriver.chromium.org](https://chromedriver.chromium.org/)
  <br />**or**<br />
   * firefox (version 72.0.2 tested) [Download From ftp.mozilla.org](https://ftp.mozilla.org/pub/firefox/releases/) + geckodriver(version 0.26
  recommended) [Download from github.com/mozilla](https://github.com/mozilla/geckodriver/releases/)

   ** **NOTE**: 
   If using a unix-like os, instead of manual installation, simply use package manager to install them (package names will probably be: chromium chromium-driver or firefox geckodriver) and create symbolic links according to installation section to use them** 


* If python is not installed follow [Properly Installing Python](https://docs.python-guide.org/starting/installation/).
    * python selenium module and schedule module
* ~~Adobe Flash Player for firefox~~ [~~Download from Adobe~~](https://get.adobe.com/flashplayer/)

### Installation

1. Clone the repo or download the zip file
    ```sh
    git clone https://github.com/UZziell/moodle-bot.git
    ```
2. install selenium and schedule modules and colorama
    ```sh
    python3 -m pip install selenium schedule colorama
    ```

#### Linux

3. Extract and copy downloaded browser(chrome or firefox) to moodle-bot (Browser's executable must be
   at `moodle-bot/BROWSER/BROWSER`) 
     
4. Copy driver (weather `geckodriver` or `chromedriver`) file to `moodle-bot/drivers/` directory
5. Make sure both browser binary and driver are executable.
6. <del>Copy `lib*flashplayer.so` also to `moodle-bot/drivers/` and rename it to `libnflashplayer.so`</del>

#### windows

3. Install downloaded browser to `moodle-bot/BROWSER` directory (browser executable must be
   at `moodle-bot/BROWSER/BROWSER`)
4. Extract and copy driver file to `moodle-bot/drivers/` directory
5. <del>Install Adobe flash player</del>

**NOTE-1** BROWSER is weather firefox or chrome

<del>\* **NOTE-2** \*:  After extracting or installing firefox, you may probably want to delete updater executable.
In despite of setting `app.update.auto` and `app.update.enabled` to `False` firefox keeps automatically updating itself. So
search for `updater` and `maintainer` executables in firefox directory and **delete** them.<del>

<!-- USAGE EXAMPLES -->

## Usage

<!-- 1. You can whether rename `secrets.py.example` to `secrets.py` and fill it with your moodle username and password\
    or\
    supply --username YOUR_USERNAME and --password YOUR_PASSWORD command line arguments when running the script.
-->
** **NOTE** use --help for complete options and command line arguments ** 
1. Add your weekly schedule to script

   Well this is the ugliest part. To give the script your moodle course details(day of week and hour) you should
   manually edit the `schedule_me()` function in `moodle-bot.py`. So in `schedule_me()` function, for every class
   session of a course add an entry with the following format:

        schedule.every().DAY_OF_THE_WEEK.at("HH:MM").do(func, at_course="COURSE NAME", for_duration=Minutes)

   `DAY_OF_THE_WEEK` is the week day of the class {`saturday`, `sunday`, `monday`, `tuesday`, `wednesday`, `thursday`
   and maybe even`friday`}\
   Keep in mind that this is the name of the method and not a string, so doesn't need quotations.\
   `HH:MM` *str*  is the start time of the class\
   `COURSE NAME` *str*  is full or partial name of the course. For example, for the course `مباني داده کاوي` you could
   simply set it to `داده`\
   `Minutes` *int*   is how long the bot will be online in the class

   example:\
   ```schedule.every().saturday.at("08:00").do(func, at_course="زبان فا", for_duration=95)```

   For a course that has classes every other week, add the entry to `# Odd weeks` or `# Even week`

2. Finally, run the script (you should supply --url MOODLE_LOGIN_URL and also --username YOUR_USERNAME and --password
   YOUR_PASSWORD command line arguments when running the script.):
    ```sh
    ~$ cd moodle-bot
    ~/moodle-bot$ python3 moodle_bot.py -u teacher -p sandbox --url "https://sandbox.moodledemo.net/login/index.php"
    ```
   optionally you can pass -s or --headless command line argument to start browser in headless mode, for example:
    ```sh
    ~/moodle-bot$ python3 moodle_bot.py -u USERNAME -p PASSWORD --url URL --headless
    ```
   To disable auto-reply use --no-autoreply:
    ```sh
    ~/moodle-bot$ python3 moodle_bot.py -u USERNAME -p PASSWORD --url URL --no-autoreply
    ```
   Options all together:
    ```sh
    ~/moodle-bot$ python3 moodle_bot.py -u USERNAME -p PASSWORD --url URL --headless --no-autoreply
    ```
<!--
## Contribution
Contributions are genuinely welcomed.
-->   
