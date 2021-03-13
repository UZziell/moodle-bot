#!/usr/bin/env python3

""" moodle bot
A simple bot that automatically logs in to Moodle learning management system and attends Adobe online classes.
It uses Selenium WebDriver and schedule module.
"""

import argparse
import datetime
import logging
import os
import pickle
import platform
import re
from datetime import datetime
# import threading
from time import sleep

import schedule
from selenium import webdriver, common
from selenium.common.exceptions import NoSuchElementException, WebDriverException
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# from secrets import USERNAME, PASSWORD

# PATHS
COOKIES_PATH = "cookies/"
PWD = os.getcwd()
FLASH_PATH = rf"{PWD}/drivers/libnflashplayer.so"
FIREFOX_DRIVER_PATH = rf"{PWD}/drivers/geckodriver"
FIREFOX_BINARY_PATH = rf"{PWD}/firefox/firefox-bin"
CHROME_DRIVER_PATH = rf"{PWD}/drivers/chromedriver"

# parse command line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-u', '--username', required=True,
                    help="Moodle username, if supplied will be replaced with USERNAME from secrets.py")
parser.add_argument('-p', '--password', required=True,
                    help="Moodle password, if supplied will be replaced with PASSWORD from secrets.py")
parser.add_argument('-r', '--url', required=True, help="Moodle login-page url")
parser.add_argument('-s', '--headless', '--silent', action='store_true', help="run browser in headless mode")
parser.add_argument('--debug', action='store_true', help="enable debugging")
parser.add_argument('--no-autoreply', action='store_true', help="disable auto-reply")

args = parser.parse_args()

# setup logging
log_level = logging.INFO
if args.debug:
    log_level = logging.DEBUG
logging.basicConfig(format="[%(asctime)s]  %(levelname)s - %(message)s", datefmt="%H:%M:%S", level=log_level)

# Options
AUTOREPLY = not args.no_autoreply
HEADLESS = args.headless
# User/pass + URL
LOGIN_URL = args.url
if args.username:
    if args.password is None:
        parser.error("--username requires --password too")
    else:
        USERNAME = args.username
        PASSWORD = args.password

logging.info(f"Initial Config:\n\t\t\t\tUsername: {USERNAME}\tPassword: {len(PASSWORD) * '*'}\tMoodleURL: {LOGIN_URL}"
             f"\n\t\t\t\tLog leve: {log_level}\tAuto-reply: {AUTOREPLY}\tHeadless: {HEADLESS}")


def chrome_builder():
    args_to_add = ["--disable-infobars", "--disable-password-generation", "--disable-password-manager-reauthentication",
                   "--disable-save-password-bubble", "--disable-features=EnableEphemeralFlashPermission"]
    options = webdriver.chrome.options.Options()

    for arg in args_to_add:
        options.add_argument(arg)

    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1480,920")
    # options.add_argument("--disable-gpu")
    # options.add_argument(f"--ppapi-flash-path={FLASH_PATH}")
    # options.add_argument("--ppapi-flash-version=32.0.0.433")
    # options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("user-data-dir=./Profile")
    # options.add_argument("--headless")
    options.headless = HEADLESS

    prefs = {
        "profile.default_content_setting_values.plugins": 1,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.setting": 1,
        "profile.managed_plugins_allowed_for_urls": ["https://ac.aminidc.com", "http://lms.ikiu.ac.ir/",
                                                     "https://www.whatismybrowser.com:443", LOGIN_URL],
        "plugins.run_all_flash_in_allow_mode": True,
        "plugins.RunAllFlashInAllowMode": True,

        # "browser.pepper_flash_settings_enabled": True,
        # "profile.default_content_setting_values.plugins": 1,
        # "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        # "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
        # "profile.content_settings.exceptions.plugins.*,*.setting": 1,
        # "profile.default_content_setting_values.flash_data": 1,
        # "profile.default_content_setting_values.flash-data": 1,
        # "DefaultPluginsSetting" : 1,
        # "PluginsAllowedForUrls": "https://www.whatismybrowser.com/detect/is-flash-installed"
    }

    options.add_experimental_option("prefs", prefs)

    # Chrome flash setup and check
    # manually_add_flash_chrome(browser, "https://ac.aminidc.com")
    # browser.get("chrome://settings/content/flash?search=flash")
    # # browser.get("chrome://version")
    # sleep(1)
    # browser.get("chrome://prefs-internals/")

    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    browser.get(f"file://{PWD}/stand-by.html")

    return browser


def firefox_builder():
    binary = FirefoxBinary(FIREFOX_BINARY_PATH)
    profile = FirefoxProfile()

    if platform.system().lower() != "windows":
        profile.set_preference("plugin.flash.path", FLASH_PATH)
    profile.set_preference("dom.ipc.plugins.flash.disable-protected-mode", True)
    profile.set_preference("plugins.flashBlock.enabled", False)
    profile.set_preference("plugin.state.flash", 2)
    profile.set_preference("app.update.auto", False)
    profile.set_preference("app.update.enabled", False)
    profile.set_preference("browser.link.open_newwindow.restriction",
                           0)  # apply the setting under (A) to ALL new windows (even script windows with features)
    profile.set_preference("browser.link.open_newwindow.override.external", 2)  # open external links in a new window
    profile.set_preference("browser.link.open_newwindow", 3)  # divert new window to a new tab
    ##
    # profile.set_preference("network.http.connection-timeout", 15)
    # profile.set_preference("network.http.connection-retry-timeout", 15)
    ##
    profile.update_preferences()

    opts = webdriver.firefox.options.Options()
    opts.headless = HEADLESS

    browser = webdriver.Firefox(firefox_binary=binary, options=opts, firefox_profile=profile,
                                executable_path=FIREFOX_DRIVER_PATH)
    # firefox flash check
    # browser.get("about:config")
    # browser.find_element_by_xpath('//*[@id="warningButton"]').click()
    # browser.find_element_by_css_selector(
    #     "window#config deck#configDeck vbox hbox#filterRow textbox#textbox input.textbox-input").send_keys(
    #     "flash" + Keys.ENTER)
    # browser.save_screenshot("sc.png")
    # logging.info("about:config => flash settings, screenshot captured")
    # sleep(1)

    # browser.get("https://isflashinstalled.com/")
    # logging.info(f"{browser.find_element_by_css_selector('body').text.split()[:4]}")
    # browser.get("https://www.whatismybrowser.com/detect/is-flash-installed")
    # is_installed = re.search("Flash \d\d?.\d\d?.\d\d? is installed",
    #                                browser.find_element_by_xpath('//*[@id="detected_value"]').text)
    # browser.implicitly_wait(10)
    # browser.get("https://toolster.net/flash_checker")
    # elmnt = browser.find_element_by_css_selector(
    #     "html body div#main div#center div#tool_padding div#flash_checker div#bottom_info div#double-version.vtor_info")
    # is_installed = re.search(r"You have installed Flash Player v.\d\d?.\d\d?.\d\d?", elmnt.text)
    #
    # assert is_installed, "Flash is disabled or not installed!"
    # logging.info(f"Check flash response: {is_installed.group()}")
    browser.get(f"file://{PWD}/stand-by.html")

    return browser


class MoodleBot:
    def __init__(self, moodle_username, moodle_password):
        self.moodle_username = moodle_username
        self.moodle_password = moodle_password
        self.browser = firefox_builder()

    def moodle_login(self, login_url=LOGIN_URL):
        cookie_file = f"{COOKIES_PATH}{self.moodle_username}-cookies.pkl"

        while True:
            self.browser.get(login_url)
            assert "آموزش مجازی" or "Log in" in self.browser.page_source, "Could not properly load LMS Login page!"
            logging.info("Loaded LMS login page")
            logging.debug(f"current URL: {self.browser.current_url}\tpage title: {self.browser.title}")

            # if exists(cookie_file):
            #     hour_ago = datetime.now() - timedelta(minutes=300)
            #     file_epoch = os.path.getmtime(cookie_file)
            #     file_mtime = datetime.fromtimestamp(file_epoch)
            #     if file_mtime > hour_ago:  # if the file was last modified during the last hour, load it
            #         session = pickle.load(open(cookie_file, "rb"))
            #         self.browser.delete_all_cookies()
            #         for cookie in session["cookies"]:
            #             self.browser.add_cookie(cookie)
            #         logging.info(f"Loaded cookie from file '{cookie_file}'")
            #         # browser.execute_script("window.open('about:newtab','_blank');")
            #         try:
            #             self.browser.refresh()
            #         except Exception as e:
            #             logging.exception(f"Cookies are probably expired."
            #                               f"Exception details: {e}")
            #             self.browser.delete_all_cookies()
            #             self.browser.refresh()
            #     else:
            #         os.remove(cookie_file)

            title = self.browser.title.lower()
            if "ورود" in title or "log in" in title or "log-in" in title:
                logging.info("Trying to login with credentials...")
                username_field = self.browser.find_element_by_xpath('//*[@id="username"]')
                passwd_field = self.browser.find_element_by_xpath('//*[@id="password"]')
                username_field.send_keys(f"{self.moodle_username}")
                passwd_field.send_keys(f"{self.moodle_password}")
                self.browser.find_element_by_xpath('//*[@id="rememberusername"]').click()
                sleep(0.5)
                self.browser.find_element_by_xpath('//*[@id="loginbtn"]').click()

            try:
                # is_loggedin = self.browser.find_element(By.ID, "page-wrapper").find_element(By.ID, "page-footer")
                is_loggedin = self.browser.find_element_by_xpath('//*[@id="page-footer"]/div/div[2]')
            except:
                logging.info("Login failed. Are username & password correct?")
                logging.debug(f"login with {self.moodle_username}/{self.moodle_password} failed. Trying again...")
                continue

            if is_loggedin:
                break

        logging.info(f"LoggedIn. LMS log: {is_loggedin.text}")
        executor_url = self.browser.command_executor._url
        session_id = self.browser.session_id
        session = {"session_id": session_id, "url": executor_url,
                   "cookies": self.browser.get_cookies()}
        # save cookie to file
        pickle.dump(session, open(cookie_file, "wb"))
        logging.info("Saved session to file")

    def load_course(self, course):
        course = course.replace("ی", "ي")
        course = course.replace("ک", "ك")
        try:
            self.browser.find_element_by_partial_link_text(course).click()
            sleep(2)
        except common.exceptions.NoSuchElementException:
            logging.exception(f"Could not find the course. Are you sure the course '{course}' exists?")
        assert course in self.browser.title, "Did not load course successfully"
        # except Exception as e:
        #     logging.error(f"Could not find course '{course}' in workspace.\n  Exception details: {e}")
        self.browser.find_element_by_partial_link_text('کلاس آنلاین').click()
        assert "پيوستن به كلاس" in self.browser.page_source, "Could not find 'پيوستن به کلاس' button"
        logging.info(f"Loaded course '{course}'")

    def switch_tab(self):
        windows = self.browser.window_handles
        if len(windows) == 1:
            self.browser.switch_to.window(windows[0])

        else:
            if self.browser.current_window_handle == windows[0]:
                self.browser.switch_to.window(windows[1])
            elif self.browser.current_window_handle == windows[1]:
                self.browser.switch_to.window(windows[0])

    def join_adobe_class(self, class_length_in_minutes=90):

        join_class = self.browser.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div/div/section/div/div[1]/form/div/div[2]/div[1]/input')
        join_class.click()

        # copy adobe class url and reopen it in a new tab
        self.switch_tab()
        links = set()
        for i in range(0, 60):
            sleep(0.2)
            links.add(self.browser.current_url)
        for link in links:
            if "session" in link:
                adobe_class_url = link

        logging.debug(f"Class URL: {adobe_class_url}")
        # adobe_class_url: property = self.browser.current_url
        self.browser.close()
        self.switch_tab()
        self.browser.find_element_by_partial_link_text('میز کار').send_keys(Keys.CONTROL, Keys.RETURN)
        # ActionChains(browser).move_to_element(browser.find_element_by_partial_link_text('میز کار')).send_keys(Keys.CONTROL, Keys.RETURN).perform()
        sleep(2)
        self.switch_tab()

        # fixing problem with adobe flash, open in browser
        self.browser.get(adobe_class_url + "&proto=true")
        sleep(5)
        # assert "Adobe Connect requires Flash" not in self.browser.page_source, "Flash is not working as expected, could not join online class"
        # assert "کلاس آنلاين"

        # Click Open in Browser and join class
        self.browser.find_element_by_xpath('/html/body/center/div[1]/div[3]/div[7]/button').click()
        logging.info(f"Joined adobe online class '{self.browser.title}'"
                     f"\n\t\t\twill be online in this class for '{class_length_in_minutes}' minutes")
        sleep(20)

        self.browser.switch_to.frame('html-meeting-frame')
        my_replys = []
        last_chat_len = 0

        def send_message(msg):
            my_replys.append(msg)
            self.browser.find_element_by_xpath('//*[@id="chatTypingArea"]').send_keys(f" {msg} ", Keys.RETURN)
            logging.info(f"Sent '{msg}'")

        def count_repeat(pattern, text):
            text_list = text.split("\n")
            logging.debug(f"'{pattern}' in '{text_list}'\t\t repeated '{len(re.findall(pattern, text))}' times")
            return len(re.findall(pattern, text))

        for i in range(class_length_in_minutes * 60):
            # TODO auto-reply
            replys = []
            try:
                chat_history = self.browser.find_element_by_xpath('//*[@id="chatContentAreaContainer"]').text
            except NoSuchElementException as e:
                logging.exception("Could not find chatContentAreaContainer element")
                continue
            except WebDriverException as e:
                logging.exception(f"WebDriverException\tcontinuing...")
                continue
            if AUTOREPLY and len(chat_history) > last_chat_len:  # if there were new messages
                last_chat_len = len(chat_history)
                for chat in chat_history.split("\n"):
                    if chat:
                        replys.append(chat.split(":")[1])

                last_10_reply = "\n".join(replys[-10:])
                # slm
                if (count_repeat(".*[sS]a?la?m.*", last_10_reply) + count_repeat(".*سلام.*", last_10_reply)) > 5 \
                        and "slm" not in my_replys[-3:]:
                    send_message("slm")
                # bale
                elif (count_repeat(".*[bB]a?le.*", last_10_reply) + count_repeat(".*بله.*", last_10_reply)) > 5 \
                        and "bale" not in my_replys[-3:]:
                    send_message("bale")

                # khaste nabashid
                elif (count_repeat(".*[kK]ha?steh?.*", last_10_reply) + count_repeat(".*خسته.*", last_10_reply)) > 4 \
                        and "خسته نباشید." not in my_replys[-3:]:
                    send_message("خسته نباشید.")
                    break  # exit class

            sleep(1)

        logging.info("Class finished, loading standby...")

    def load_standby(self):

        windows = self.browser.window_handles
        for win in windows[1:]:
            self.browser.switch_to.window(win)
            self.browser.close()
        self.browser.switch_to.window(windows[0])
        self.browser.get(f"file://{PWD}/stand-by.html")

        # find next class
        dates = [job.next_run for job in schedule.jobs]
        nearest_job = sorted(dates)[1]
        for job in sorted(schedule.jobs):
            if nearest_job == job.next_run:
                logging.info(f"Next class is {job}, will stay standby till then.")

    def run_all_in_thread(self, course, duration):
        # self.browser =
        self.browser.implicitly_wait(2)
        # self.browser.set_script_timeout(10)
        # self.browser.set_page_load_timeout(15)

        # login to moodle
        self.moodle_login()

        # load course
        self.load_course(course=course)

        # Join online class and wait 'duration' minutes then quit
        self.join_adobe_class(class_length_in_minutes=duration)
        self.load_standby()
        # self.browser.quit()

    def i_am_present(self, at_course, for_duration=90):
        # thread = threading.Thread(target=self.run_all_in_thread, args=(at_course, for_duration))
        # thread.start()
        # return thread
        self.run_all_in_thread(at_course, for_duration)


def is_even_week():
    now = datetime.now()
    if now.weekday() >= 5:
        week_number = int(now.strftime("%W"))
    else:
        week_number = int(now.strftime("%W")) - 1

    return not (week_number % 2)

    # if week_number % 2 == 0:
    #     return True
    # else:
    #     return False


def schedule_me(bot_obj):
    func = bot_obj.i_am_present

    # Test - only for testing purposes
    schedule.every().tag(bot_obj.moodle_username).saturday.at(
        datetime.now().strftime("%H:") + str(int(datetime.now().strftime("%M")) + 1).zfill(2)).do(func,
                                                                                                  at_course="تفسیر")

    # fixed jobs
    schedule.every().tag(bot_obj.moodle_username).saturday.at("08:00").do(func, at_course="ریاضی")
    schedule.every().tag(bot_obj.moodle_username).saturday.at("10:00").do(func, at_course="اینترنت")
    schedule.every().tag(bot_obj.moodle_username).saturday.at("13:00").do(func, at_course="شبکه")
    schedule.every().tag(bot_obj.moodle_username).saturday.at("17:00").do(func, at_course="پایگاه")

    schedule.every().tag(bot_obj.moodle_username).sunday.at("08:00").do(func, at_course="تفسیر")
    schedule.every().tag(bot_obj.moodle_username).sunday.at("15:00").do(func, at_course="مبانی")

    schedule.every().tag(bot_obj.moodle_username).tuesday.at("15:00").do(func, at_course="آیین")

    # schedule based on week's odd-even status
    if is_even_week():  # Even Weeks
        logging.info("This week is Even")
        schedule.every().tag(bot_obj.moodle_username).saturday.at("15:00").do(func, at_course="مبانی")
        schedule.every().tag(bot_obj.moodle_username).sunday.at("13:00").do(func, at_course="ریاضی")
        schedule.every().tag(bot_obj.moodle_username).monday.at("08:00").do(func, at_course="اینترنت")

    else:  # Odd Weeks
        logging.info("This week is Odd")
        schedule.every().tag(bot_obj.moodle_username).saturday.at("15:00").do(func, at_course="پایگاه")

    logging.info(f"Bot: {bot_obj.moodle_username} All jobs added")


if __name__ == "__main__":
    bot = MoodleBot(moodle_username=USERNAME, moodle_password=PASSWORD)
    schedule_me(bot)

    # bot2 = MoodleBot(moodle_username="", moodle_password="")
    # schedule_me(bot2)

    jobs = schedule.jobs

    bots = {list(job.tags)[0] for job in jobs}
    for bot in bots:
        print(f"\tbot: {bot}\n\t\tjobs:")
        datetimes = [job.next_run for job in jobs if bot in job.tags]
        for time in sorted(datetimes):
            for job in jobs:
                if time == job.next_run and bot in job.tags:
                    print(f"\t\t\t{job} {job.next_run}")

    while True:
        schedule.run_pending()
        sleep(1)
