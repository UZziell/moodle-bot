#!/usr/bin/env python3

""" moodle bot
A simple bot that automatically logs in to Moodle learning management system and attends Adobe online classes.
It uses Selenium WebDriver and schedule module.
"""

import argparse
import datetime
import logging
import colorama
from colorama import Fore, Back, Style
import os
import pickle
import re
import sys
from datetime import datetime, timedelta
# import threading
from time import sleep

import schedule
from selenium import webdriver, common
from selenium.common.exceptions import NoSuchElementException, WebDriverException, NoAlertPresentException, \
    UnexpectedAlertPresentException, TimeoutException  # ,InvalidSessionIdException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# from secrets import USERNAME, PASSWORD

# PATHS
COOKIES_PATH = "cookies/"
PWD = os.getcwd()
FLASH_PATH = rf"{PWD}/drivers/libnflashplayer.so"
FIREFOX_DRIVER_PATH = rf"{PWD}/drivers/geckodriver"
FIREFOX_BINARY_PATH = rf"{PWD}/firefox/firefox"
CHROME_BINARY_PATH = rf"{PWD}/chrome/chrome"
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
logging.basicConfig(format="[%(asctime)s]  %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=log_level)
colorama.init()

# Options
AUTOREPLY = not args.no_autoreply
HEADLESS = args.headless
# User/pass + URL
LOGIN_URL = args.url
# if args.username:
#     if args.password is None:
#         parser.error("--username requires --password too")
#     else:
USERNAME = args.username
PASSWORD = args.password

logging.info(f"Current input and config:\
                \n\t\t\t\tUsername: {USERNAME: <15}MoodleURL: {LOGIN_URL: <25}Headless: {HEADLESS}"
             f"\n\t\t\t\tPassword: {len(PASSWORD) * '*': <15}Log leve: {log_level: <25}Auto-reply: {AUTOREPLY}")


def chrome_builder():
    # args_to_add = ["--no-sandbox", "--disable-password-generation", "--disable-password-manager-reauthentication",
    #                "--disable-save-password-bubble", "--disable-features=EnableEphemeralFlashPermission",
    #                "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.4389.114 Safari/537.36",
    #                "--disable-infobars", "--window-size=1480,920", "--disable-popup-blocking"]
    # for arg in args_to_add:
    #    options.add_argument(arg)

    options = ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/89.0.114 Safari/537.36")
    options.headless = HEADLESS
    # options.binary_location = CHROME_BINARY_PATH

    # options.add_argument("--disable-gpu")
    # options.add_argument(f"--ppapi-flash-path={FLASH_PATH}")
    # options.add_argument("--ppapi-flash-version=32.0.0.433")
    # options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("user-data-dir=./Profile")

    # prefs = {
    #     "profile.default_content_setting_values.plugins": 1,
    #     "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    #     "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    #     "profile.content_settings.exceptions.plugins.*,*.setting": 1,
    #     "profile.managed_plugins_allowed_for_urls": ["https://ac.aminidc.com", "http://lms.ikiu.ac.ir/",
    #                                                  "https://www.whatismybrowser.com:443", LOGIN_URL],
    #     "plugins.run_all_flash_in_allow_mode": True,
    #     "plugins.RunAllFlashInAllowMode": True,
    #
    #     # "browser.pepper_flash_settings_enabled": True,
    #     # "profile.default_content_setting_values.plugins": 1,
    #     # "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    #     # "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    #     # "profile.content_settings.exceptions.plugins.*,*.setting": 1,
    #     # "profile.default_content_setting_values.flash_data": 1,
    #     # "profile.default_content_setting_values.flash-data": 1,
    #     # "DefaultPluginsSetting" : 1,
    #     # "PluginsAllowedForUrls": "https://www.whatismybrowser.com/detect/is-flash-installed"
    # }
    # options.add_experimental_option("prefs", prefs)

    # Chrome flash setup and check
    # manually_add_flash_chrome(browser, "https://ac.aminidc.com")
    # browser.get("chrome://settings/content/flash?search=flash")
    # # browser.get("chrome://version")
    # sleep(1)
    # browser.get("chrome://prefs-internals/")

    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    return browser


def firefox_builder():
    binary = FirefoxBinary(FIREFOX_BINARY_PATH)
    profile = FirefoxProfile()

    # Flash settings
    # if platform.system().lower() != "windows":
    #     profile.set_preference("plugin.flash.path", FLASH_PATH)
    # profile.set_preference("dom.ipc.plugins.flash.disable-protected-mode", True)
    # profile.set_preference("plugins.flashBlock.enabled", False)
    # profile.set_preference("plugin.state.flash", 2)

    profile.set_preference("general.useragent.override",
                           "UserAgent: Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0")
    profile.set_preference("app.update.auto", False)
    profile.set_preference("app.update.enabled", False)

    # apply the setting under (A) to ALL new windows (even script windows with features)
    profile.set_preference("browser.link.open_newwindow.restriction", 0)
    profile.set_preference("browser.link.open_newwindow.override.external", 2)  # open external links in a new window
    profile.set_preference("browser.link.open_newwindow", 3)  # divert new window to a new tab
    ##
    # profile.set_preference("network.http.connection-timeout", 15)
    # profile.set_preference("network.http.connection-retry-timeout", 15)
    ##
    profile.update_preferences()

    opts = FirefoxOptions
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
    # "html body div#main div#center div#tool_padding div#flash_checker div#bottom_info div#double-version.vtor_info")
    # is_installed = re.search(r"You have installed Flash Player v.\d\d?.\d\d?.\d\d?", elmnt.text)
    #
    # assert is_installed, "Flash is disabled or not installed!"
    # logging.info(f"Check flash response: {is_installed.group()}")
    return browser


class MoodleBot:
    def __init__(self, moodle_username, moodle_password):
        self.moodle_username = moodle_username
        self.moodle_password = moodle_password
        # self.browser = firefox_builder()
        self.browser = chrome_builder()
        self.browser.get(f"file://{PWD}/stand-by.html")
        self.last_course = ""

        # self.browser.execute_script("""navigator.__defineGetter__('platform', function(){
        #     return 'Linux x86_64' });""")
        # logging.info(f"Platform: {self.browser.execute_script('return navigator.platform')}")
        logging.info(f"UserAgent: {self.browser.execute_script('return navigator.userAgent')}")

    def get_element_wait_presence(self, by, element, wait=40):
        try:
            element = WebDriverWait(self.browser, wait).until(ec.presence_of_element_located((by, element)))
            return element
        except TimeoutException:
            logging.exception("TimeoutException, full stack trace")
            raise
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(f"Could not find element: '{element}' by: '{by}' on page: '{self.browser.current_url}'")
            logging.exception(e)

    def get_element_wait_clickable(self, by, element, wait=40):
        try:
            element = WebDriverWait(self.browser, wait).until(ec.element_to_be_clickable((by, element)))
            return element
        except (NoSuchElementException, WebDriverException) as e:
            logging.exception(f"Could not find element '{element}' by '{by}' on page {self.browser.current_url}")
            logging.exception(e, e.args)

    def moodle_login(self, login_url=LOGIN_URL):
        cookie_file = f"{COOKIES_PATH}{self.moodle_username}-cookies.pkl"
        is_loggedin = False
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
                username_field = self.get_element_wait_presence(by=By.XPATH, element='//*[@id="username"]')
                passwd_field = self.get_element_wait_presence(by=By.XPATH, element='//*[@id="password"]')
                username_field.send_keys(f"{self.moodle_username}")
                passwd_field.send_keys(f"{self.moodle_password}")
                # check remember me
                self.get_element_wait_clickable(by=By.XPATH, element='//*[@id="rememberusername"]').click()
                sleep(0.5)
                self.get_element_wait_clickable(by=By.XPATH, element='//*[@id="loginbtn"]').click()

            try:
                # is_loggedin = self.browser.find_element(By.ID, "page-wrapper").find_element(By.ID, "page-footer")
                is_loggedin = self.get_element_wait_presence(by=By.XPATH, element='//*[@id="page-footer"]/div/div[2]')
                # is_loggedin = self.browser.find_element_by_xpath('//*[@id="page-footer"]/div/div[2]')
            except TimeoutException:
                logging.warning(f"loading {self.browser.current_url} timeout! \tretrying...")
            except Exception as e:
                logging.info("Login failed. Are username & password correct?")
                logging.debug(f"login with {self.moodle_username}/{self.moodle_password} failed. Trying again...")
                logging.exception(e, e.args)
                continue

            if is_loggedin:
                break

        logging.info(f"LoggedIn. LMS log: {is_loggedin.text}")
        # executor_url = self.browser.command_executor._url
        session_id = self.browser.session_id
        session = {"session_id": session_id, "url": self.browser.current_url,
                   "cookies": self.browser.get_cookies()}
        # save cookie to file
        pickle.dump(session, open(cookie_file, "wb"))
        logging.info("Saved session to file")

    def load_course(self, course):
        self.last_course = course

        course = course.replace("ی", "ي")
        course = course.replace("ک", "ك")
        try:
            self.get_element_wait_clickable(by=By.PARTIAL_LINK_TEXT, element=course).click()
            logging.info(f"Loaded course '{course}'")
            # self.browser.find_element_by_partial_link_text(course).click()
            # sleep(2)
        except common.exceptions.NoSuchElementException:
            logging.exception(f"Could not find the course. Are you sure the course '{course}' exists?")
        assert course in self.browser.title, "Did not load course successfully"

        self.get_element_wait_clickable(by=By.PARTIAL_LINK_TEXT, element='کلاس آنلاین').click()
        # self.browser.find_element_by_partial_link_text('کلاس آنلاین').click()
        assert "پيوستن به كلاس" in self.browser.page_source, "Could not find 'پيوستن به کلاس' button"

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
        join_class_button = self.get_element_wait_clickable(
            by=By.XPATH,
            element='/html/body/div[1]/div[2]/div/div/section/div/div[1]/form/div/div[2]/div[1]/input')
        # join_class = self.browser.find_element_by_xpath(
        #     '/html/body/div[1]/div[2]/div/div/section/div/div[1]/form/div/div[2]/div[1]/input')
        join_class_button.click()

        # copy adobe class url and reopen it in a new tab
        self.switch_tab()
        self.get_element_wait_presence(by=By.XPATH, element='//*[@id="systemContainer"]')
        adobe_class_url = ""
        referrer = self.browser.execute_script('return window.document.referrer')
        if "session" in referrer.lower():
            adobe_class_url = referrer
        else:
            links = set()
            for i in range(0, 60):
                sleep(0.2)
                links.add(self.browser.current_url)
            for link in links:
                if "session" in link.lower():
                    adobe_class_url = link
        if not adobe_class_url:
            logging.exception("did not find class url, exiting...")

        logging.debug(f"Class URL: {adobe_class_url}")
        # adobe_class_url: property = self.browser.current_url
        self.browser.close()
        self.switch_tab()
        self.browser.find_element_by_partial_link_text('میز کار').send_keys(Keys.CONTROL, Keys.RETURN)
        # ActionChains(browser).move_to_element(browser.find_element_by_partial_link_text('میز کار')).send_keys(
        #    Keys.CONTROL, Keys.RETURN).perform()
        sleep(0.5)
        self.switch_tab()

        # fixing problem with adobe flash, open in browser
        self.browser.get(adobe_class_url + "&proto=true")
        # sleep(5)
        # assert "Adobe Connect requires Flash" not in self.browser.page_source, "Flash is not working as expected"

        # Click Open in Browser and join class
        # if platform.system().lower() == "windows":
        self.get_element_wait_clickable(by=By.XPATH, element='/html/body/center/div[1]/div[3]/div[7]/button')
        self.browser.execute_script("""openMeetingInHtmlClient();""")

        logging.info(f"Joined adobe online class '{self.browser.title}'"
                     f"\n\t\t\twill be online in this class for '{class_length_in_minutes}' minutes")

        # ## Auto-Reply ## #
        # Switch to default adobe meeting frame
        WebDriverWait(self.browser, 120).until(
            ec.frame_to_be_available_and_switch_to_it((By.ID, 'html-meeting-frame')))

        # try to remove share pod
        try:
            wait_seconds = 30
            sharepod_id = "connectPod20"
            self.get_element_wait_presence(by=By.XPATH, element='//*[@id="connectPod20"]', wait=wait_seconds)
            self.browser.execute_script("""document.getElementById("connectPod20").outerHTML = "";""")
        except TimeoutException:
            logging.warning(f"{Fore.YELLOW}Share pod not found after '{wait_seconds}' seconds.{Style.RESET_ALL}")
        except:
            logging.error(f"Could not remove Share pod! 'id={sharepod_id}'")
        else:
            logging.info(f"Share pod removed successfully. 'id={sharepod_id}'")

        # sleep(30)
        # self.browser.switch_to.frame(By.ID, 'html-meeting-frame')

        my_replys = []
        chat_messages = ""
        last_chat_len = 0

        def send_message(msg, reply_list):
            reply_list.append(msg)
            self.get_element_wait_presence(by=By.XPATH, element='//*[@id="chatTypingArea"]').send_keys(f" {msg} ",
                                                                                                       Keys.RETURN)
            logging.info(f"{Fore.GREEN}Sent '{msg}' at {datetime.now()}{Style.RESET_ALL}")

        def count_repeat(pattern, text):
            text_list = text.split("\n")
            logging.debug(f"'{pattern}' in '{text_list}'\t\t repeated '{len(re.findall(pattern, text))}' times")
            return len(re.findall(pattern, text))

        def spinning_cursor():
            while True:
                for cursor in '|/-\\':
                    yield cursor

        spinner = spinning_cursor()
        sleep_seconds = 5
        const = int(60 / sleep_seconds)
        exception_threshold = 5
        exception_count = 0

        for i in range(class_length_in_minutes * const):
            sys.stdout.write(f"waiting to reply {next(spinner)}")
            sys.stdout.flush()
            sleep(sleep_seconds)
            sys.stdout.write('\r')

            if AUTOREPLY:
                try:
                    if exception_count > exception_threshold:
                        logging.warning(
                            "Exceptions exceeding threshold. Raising Unknown Ex to compel rejoining class (JUSTinCASE)")
                        raise WebDriverException
                    self.get_element_wait_presence(by=By.XPATH, element='//*[@id="chatIndividualMessageContent"]',
                                                   wait=6)
                    chat_messages = self.browser.find_elements_by_xpath('//*[@id="chatIndividualMessageContent"]')
                except NoSuchElementException as e:
                    exception_count += 1
                    logging.exception("Could not get chat history element text", e)
                    continue
                except TimeoutException:
                    exception_count += 1
                    logging.warning("TimeoutException - No messages in chat box yet, continuing...")
                except:
                    logging.error(f"{Fore.BLACK}{Back.RED}Unknown exception! Due to possible driver crash,"
                                  f" relaunching a new browser...{Style.RESET_ALL}")
                    try:
                        self.browser.quit()
                    #     popup = self.browser.switch_to.alert
                    #     popup.accept()
                    # except NoAlertPresentException:
                    #     pass
                    except UnexpectedAlertPresentException:
                        alert = self.browser.switch_to.alert
                        alert.accept()
                    sleep(1)
                    self.browser = chrome_builder()
                    minutes_left = class_length_in_minutes - (int(i * sleep_seconds / 60) + 1)
                    self.i_am_present(at_course=self.last_course, for_duration=minutes_left)
                    break

                    # Click Open in Browser and join class
                    # self.get_element_wait_clickable(by=By.XPATH,
                    #                                element='/html/body/center/div[1]/div[3]/div[7]/button')
                    # self.browser.execute_script("""openMeetingInHtmlClient();""")
                    # logging.info(f"Rejoined class\t\twill be online in this class for '{i}' minutes")
                    # WebDriverWait(self.browser, 120).until(
                    #    ec.frame_to_be_available_and_switch_to_it((By.ID, 'html-meeting-frame')))
                    # self.get_element_wait_presence(by=By.XPATH, element='//*[@id="chatIndividualMessageContent"]')
                    # chat_messages = self.browser.find_elements_by_xpath('//*[@id="chatIndividualMessageContent"]')
                    # continue

                if len(chat_messages) > last_chat_len:  # if there were new messages
                    last_chat_len = len(chat_messages)

                    last_replies_list = []
                    for message in chat_messages[-10:]:
                        last_replies_list.append(message.text)

                    last_replies = "\n".join(last_replies_list[-10:])

                    # slm
                    if (count_repeat(".*[sS]a?la?m.*", last_replies) + count_repeat(".*سلام.*", last_replies)) > 4 \
                            and "slm" not in my_replys[-5:]:
                        send_message("slm", my_replys)
                    # bale
                    elif (count_repeat(".*[bB]a?le.*", last_replies) + count_repeat(".*بله.*", last_replies)) > 4 \
                            and "bale" not in my_replys[-3:]:
                        send_message("bale", my_replys)

                    # khaste nabashid
                    elif (count_repeat(".*[kK]ha?steh?.*", last_replies) + count_repeat(".*خسته.*", last_replies)) > 4 \
                            and "خسته نباشید." not in my_replys and i > 30 * const:

                        send_message("خسته نباشید.", my_replys)
                        break  # exit class

        logging.info("Class finished.")

    def load_standby(self):
        logging.info("Closing other tabs and loading standby page...")

        windows = self.browser.window_handles
        for win in windows[1:]:
            self.browser.switch_to.window(win)
            try:
                self.browser.close()
            except NoAlertPresentException:
                pass
            except UnexpectedAlertPresentException:
                alert = self.browser.switch_to.alert
                alert.accept()

        self.browser.switch_to.window(windows[0])
        self.browser.get(f"file://{PWD}/stand-by.html")

        # find next class
        dates = [job.next_run for job in schedule.jobs]
        nearest_job = sorted(dates)[1]
        for job in sorted(schedule.jobs):
            if nearest_job == job.next_run:
                logging.info(f"Next class is {job} at {job.next_run}, will stay standby till then.")

    def run_all_in_thread(self, course, duration):
        # self.browser.implicitly_wait(2)
        # self.browser.set_script_timeout(10)
        # self.browser.set_page_load_timeout(15)

        # login to moodle
        self.moodle_login()

        # load course
        self.load_course(course=course)

        # Join online class and wait 'duration' minutes then quit
        self.join_adobe_class(class_length_in_minutes=duration)
        self.load_standby()

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
    # def minute_from_now(m=1):
    #     now_plus_m = datetime.now() + timedelta(minutes=m)
    #     return now_plus_m.strftime("%H:%M")
    #
    # mfrom = minute_from_now
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(1)).do(func, at_course="ریاضی", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(5)).do(func, at_course="آیین", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(9)).do(func, at_course="تفسیر", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(13)).do(func, at_course="منطقی", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(17)).do(func, at_course="پردازنده", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(21)).do(func, at_course="سیستم عامل", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(25)).do(func, at_course="شبکه", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(29)).do(func, at_course="پایگاه داده", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(33)).do(func, at_course="مبانی", for_duration=3)
    # schedule.every().tag(bot_obj.moodle_username).day.at(mfrom(37)).do(func, at_course=" اینترنت", for_duration=3)

    # fixed jobs
    schedule.every().tag(bot_obj.moodle_username).saturday.at("08:00").do(func, at_course="ریاضی")
    schedule.every().tag(bot_obj.moodle_username).saturday.at("10:00").do(func, at_course="اینترنت", for_duration=120)
    schedule.every().tag(bot_obj.moodle_username).saturday.at("14:00").do(func, at_course="شبکه")
    schedule.every().tag(bot_obj.moodle_username).saturday.at("18:00").do(func, at_course="پایگاه")

    schedule.every().tag(bot_obj.moodle_username).sunday.at("08:00").do(func, at_course="تفسیر")
    schedule.every().tag(bot_obj.moodle_username).sunday.at("16:00").do(func, at_course="مبانی")

    schedule.every().tag(bot_obj.moodle_username).tuesday.at("16:00").do(func, at_course="آیین")
    schedule.every().tag(bot_obj.moodle_username).wednesday.at("08:00").do(func, at_course="سیستم")
    schedule.every().tag(bot_obj.moodle_username).thursday.at("10:00").do(func, at_course="پردازنده")

    # schedule based on week's odd-even status
    if is_even_week():  # Even Weeks
        logging.info("This week is Even")
        schedule.every().tag(bot_obj.moodle_username).saturday.at("16:00").do(func, at_course="مبانی")
        schedule.every().tag(bot_obj.moodle_username).sunday.at("14:00").do(func, at_course="ریاضی")
        schedule.every().tag(bot_obj.moodle_username).monday.at("08:00").do(func, at_course="اینترنت", for_duration=120)

    else:  # Odd Weeks
        logging.info("This week is Odd")
        schedule.every().tag(bot_obj.moodle_username).saturday.at("16:00").do(func, at_course="پایگاه")

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
