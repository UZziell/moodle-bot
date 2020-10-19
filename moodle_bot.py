# moodle bot
# A simple bot that automatically logs in to Moodle learning management system then attends Adobe online classes.
# It uses Selenium WebDriver and schedule module.

import argparse
import datetime
import logging
import os
import pickle
import platform
import re
# import threading
from os.path import exists
from time import sleep

import schedule
from selenium import webdriver, common
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import Select

from secrets import USERNAME, PASSWORD

# PATHS
COOKIES_PATH = "cookies/"
PWD = os.getcwd()
FLASH_PATH = rf"{PWD}/drivers/libnflashplayer.so"
FIREFOX_DRIVER_PATH = rf"{PWD}/drivers/geckodriver"
FIREFOX_BINARY_PATH = rf"{PWD}/firefox/firefox"
CHROME_DRIVER_PATH = rf"{PWD}/drivers/chromedriver-86"

# setup logging
logging.basicConfig(format="[%(asctime)s]  %(levelname)s - %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--headless', action='store_true', help="run browser in headless mode")
parser.add_argument('-u', '--username', required=False,
                    help="Moodle username, if supplied will be replaced with USERNAME from secrets.py")
parser.add_argument('-p', '--password', required=False,
                    help="Moodle password, if supplied will be replaced with PASSWORD from secrets.py")
args = parser.parse_args()

HEADLESS = args.headless
if args.username:
    if args.password is None:
        parser.error("--username requires --password too")
    else:
        USERNAME = args.username
        PASSWORD = args.password


def chrome_builder():
    args_to_add = ["--disable-infobars", "--disable-password-generation", "--disable-password-manager-reauthentication",
                   "--disable-save-password-bubble", "--disable-features=EnableEphemeralFlashPermission"]
    options = webdriver.chrome.options.Options()

    for arg in args_to_add:
        options.add_argument(arg)

    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1480,920")
    # options.add_argument("--disable-gpu")
    options.add_argument(f"--ppapi-flash-path={FLASH_PATH}")
    options.add_argument("--ppapi-flash-version=32.0.0.433")
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("user-data-dir=./Profile")
    # options.add_argument("--headless")
    options.headless = HEADLESS

    prefs = {
        "profile.default_content_setting_values.plugins": 1,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.setting": 1,
        "profile.managed_plugins_allowed_for_urls": ["https://ac.aminidc.com", "http://lms.ikiu.ac.ir/",
                                                     "https://www.whatismybrowser.com:443"],
        "plugins.run_all_flash_in_allow_mode": True,
        "plugins.RunAllFlashInAllowMode": True,

        # "browser.pepper_flash_settings_enabled": True,
        # "profile.default_content_setting_values.plugins": 1,
        # "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        # "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
        # "profile.content_settings.exceptions.plugins.*,*.setting": 1,
        # "profile.default_content_setting_values.flash_data": 1,
        # "profile.default_content_setting_values.flash-data": 1,

        # # r"profile.content_settings.exceptions.flash_data.'https://aminidccom:443,*'.expiration": "0",
        # # r"profile.content_settings.exceptions.flash_data.https://aminidc.com:443,*.last_modified": "13246572488176725",
        # "profile.content_settings.exceptions.flash_data.[https://aminidc.com]:443,*.model": 0,
        # "profile.content_settings.exceptions.flash_data.[https://aminidc.com:443],*.setting.flashPreviouslyChanged": True,

        # "profile.content_settings.exceptions.flash-data.*,*.model": 0,
        # "profile.content_settings.exceptions.flash-data.*,*.setting.flashPreviouslyChanged": "true",
        # "DefaultPluginsSetting" : 1,
        # "PluginsAllowedForUrls": "https://www.whatismybrowser.com/detect/is-flash-installed"
    }

    options.add_experimental_option("prefs", prefs)

    # Chrome SETUP
    # browser = webdriver.Chrome(
    #     executable_path=r'./drivers/chromedriver-86', options=options)

    # Chrome flash check
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
    profile.set_preference("network.http.connection-timeout", 15)
    profile.set_preference("network.http.connection-retry-timeout", 15)
    ##
    profile.update_preferences()

    opts = webdriver.firefox.options.Options()
    opts.headless = HEADLESS

    browser = webdriver.Firefox(firefox_binary=binary, options=opts, firefox_profile=profile,
                                executable_path=FIREFOX_DRIVER_PATH)
    # firefox flash check
    browser.get("about:config")
    browser.find_element_by_xpath('//*[@id="warningButton"]').click()
    browser.find_element_by_css_selector(
        "window#config deck#configDeck vbox hbox#filterRow textbox#textbox input.textbox-input").send_keys(
        "flash" + Keys.ENTER)
    browser.save_screenshot("sc.png")
    logging.info("about:config => flash settings, screenshot captured")
    sleep(1)

    browser.get("https://toolster.net/flash_checker")
    elmnt = browser.find_element_by_css_selector(
        "html body div#main div#center div#tool_padding div#flash_checker div#bottom_info div#double-version.vtor_info")
    is_installed = re.search(r"You have installed Flash Player v.\d\d?.\d\d?.\d\d?", elmnt.text)

    # browser.get("https://isflashinstalled.com/")
    # logging.info(f"{browser.find_element_by_css_selector('body').text.split()[:4]}")
    # browser.get("https://www.whatismybrowser.com/detect/is-flash-installed")
    # is_installed = re.search("Flash \d\d?.\d\d?.\d\d? is installed",
    #                                browser.find_element_by_xpath('//*[@id="detected_value"]').text)

    assert is_installed, "Flash is disabled or not installed!"
    logging.info(f"{is_installed.group()}")
    browser.get(f"file://{PWD}/stand-by.html")

    return browser


class MoodleBot:
    def __init__(self, moodle_username, moodle_password):
        self.moodle_username = moodle_username
        self.moodle_password = moodle_password
        self.browser = firefox_builder()

    def moodle_login(self, login_url="http://lms.ikiu.ac.ir/"):
        cookie_file = f"{COOKIES_PATH}{self.moodle_username}-cookies.pkl"
        self.browser.get(login_url)
        assert "آموزش مجازی" in self.browser.page_source, "Could not properly load LMS Login page!"
        logging.info("Loaded LMS login page")

        if exists(cookie_file):
            session = pickle.load(open(cookie_file, "rb"))
            self.browser.delete_all_cookies()
            for cookie in session["cookies"]:
                self.browser.add_cookie(cookie)
            logging.info(f"Loaded cookie from file '{cookie_file}'")
            # browser.execute_script("window.open('about:newtab','_blank');")
            try:
                self.browser.refresh()
            except Exception as e:
                logging.exception(f"Cookies are probably expired."
                                  f"Exception details: {e}")
                self.browser.delete_all_cookies()
                self.browser.refresh()

        if "ورود" in self.browser.title:
            logging.info("Trying to login with credentials...")
            username_field = self.browser.find_element_by_xpath('//*[@id="username"]')
            passwd_field = self.browser.find_element_by_xpath('//*[@id="password"]')
            username_field.send_keys(f"{self.moodle_username}")
            passwd_field.send_keys(f"{self.moodle_password}")
            self.browser.find_element_by_xpath('//*[@id="rememberusername"]').click()
            sleep(0.5)
            self.browser.find_element_by_xpath('//*[@id="loginbtn"]').click()

        try:
            is_loggedin = self.browser.find_element(By.ID, "page-wrapper").find_element(By.ID, "page-footer")
        except:
            logging.info("Login failed. Are username & password correct?")
        if is_loggedin:
            logging.info(f"LoggedIn. {is_loggedin.text}")
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
        # browser.find_element_by_xpath('/html/body/div[1]/nav/ul[2]/li[2]/div/div/div/div/div/div/a[2]').click()
        # browser.find_element_by_partial_link_text("مشاهده موارد بیشتر").click()
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
        sleep(5)
        adobe_class_url: property = self.browser.current_url
        self.browser.close()
        self.switch_tab()
        self.browser.find_element_by_partial_link_text('میز کار').send_keys(Keys.CONTROL, Keys.RETURN)
        # ActionChains(browser).move_to_element(browser.find_element_by_partial_link_text('میز کار')).send_keys(Keys.CONTROL, Keys.RETURN).perform()
        sleep(2)
        self.switch_tab()
        self.browser.get(adobe_class_url)
        sleep(5)
        assert "Adobe Connect requires Flash" not in self.browser.page_source, "Flash is not working as expected, could not join online class"
        assert "کلاس آنلاين"
        logging.info(f"Joined adobe online class '{self.browser.title}'"
                     f"\n\t\t\twill be online in this class for '{class_length_in_minutes}' minutes")

        # sleep(class_length_in_minutes * 60)
        for i in range(class_length_in_minutes * 60):
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
    now = datetime.datetime.now()
    if now.weekday() >= 5:
        week_number = int(now.strftime("%W"))
    else:
        week_number = int(now.strftime("%W")) - 1
    return week_number % 2


def schedule_me(bot_obj):
    func = bot_obj.i_am_present

    # fixed jobs
    schedule.every().saturday.at("08:00").do(func, at_course="زبان فا")
    schedule.every().saturday.at("10:00").do(func, at_course="سيگنال")
    schedule.every().sunday.at("10:00").do(func, at_course="مدار")
    schedule.every().sunday.at("15:00").do(func, at_course="آز فيزيك")
    schedule.every().sunday.at("18:30").do(func, at_course="ورزش", for_duration=120)
    schedule.every().monday.at("13:00").do(func, at_course="شبکه")
    schedule.every().monday.at("15:00").do(func, at_course="مديريت اطلاعات")  # mis
    schedule.every().tuesday.at("10:00").do(func, at_course="مباني داده")
    # schedule based on week's odd-even status
    if is_even_week():  # Even Weeks
        schedule.every().saturday.at("13:00").do(func, at_course="زبان فا")
        schedule.every().saturday.at("15:00").do(func, at_course="مديريت اطلاعات")
        schedule.every().wednesday.at("10:00").do(func, at_course="شبکه")
    else:  # Odd Weeks
        schedule.every().saturday.at("15:00").do(func, at_course="سيگنال")
        schedule.every().sunday.at("13:00").do(func, at_course="مدار")
        schedule.every().tuesday.at("15:00").do(func, at_course="مباني داده")

    logging.info(f"All jobs added\n\t jobs:\n {schedule.jobs}")


if __name__ == "__main__":
    bot = MoodleBot(moodle_username=USERNAME, moodle_password=PASSWORD)
    # bot.i_am_present(at_course="ورزش")
    schedule_me(bot)

    while True:
        schedule.run_pending()
        sleep(1)


def manually_add_flash_chrome(driver, web_url):
    def expand_root_element(element):
        return driver.execute_script("return arguments[0].shadowRoot", element)

    driver.get("chrome://settings/content/siteDetails?site=" + web_url)
    print(driver.title)

    root1 = driver.find_element_by_css_selector("settings-ui")
    shadow_root1 = expand_root_element(root1)

    root2 = shadow_root1.find_element(By.ID, "container")

    root3 = root2.find_element(By.ID, "main")
    shadow_root3 = expand_root_element(root3)

    root4 = shadow_root3.find_element(
        By.CSS_SELECTOR, "settings-basic-page.cr-centered-card-container.showing-subpage")
    # root4 = shadow_root3.find_element(By.CLASS_NAME, "showing-subpage")
    shadow_root4 = expand_root_element(root4)

    root5 = shadow_root4.find_element(By.ID, "basicPage")

    # root56 = root5.find_element(By.TAG_NAME, "settings-section")
    root56 = root5.find_element(By.CSS_SELECTOR, "settings-section.expanded")
    # shadow_root56 = expand_root_element(root56)

    root6 = root56.find_element(By.CSS_SELECTOR, "settings-privacy-page")
    shadow_root6 = expand_root_element(root6)

    # root7 = shadow_root6.find_element(By.TAG_NAME, "settings-animated-pages")
    root7 = shadow_root6.find_element(By.ID, "pages")
    # shadow_root7 = expand_root_element(root7)

    root8 = root7.find_element(
        By.CSS_SELECTOR, "settings-subpage.iron-selected")
    # root8 = shadow_root7.find_element_by_xpath('//*[@id="pages"]/settings-subpage')
    # shadow_root8 = expand_root_element(root8)

    root9 = root8.find_element(By.CSS_SELECTOR, "site-details")
    shadow_root9 = expand_root_element(root9)

    root10 = shadow_root9.find_element(
        By.CSS_SELECTOR, "div.list-frame site-details-permission[id='plugins']")

    # root10 = root910.find_element(By.ID, "plugins")
    shadow_root10 = expand_root_element(root10)

    root11 = shadow_root10.find_element(By.ID, "details")
    root12 = root11.find_element(By.ID, "permissionItem")
    root13 = root12.find_element(By.ID, "permission")
    Select(root13).select_by_value("allow")
