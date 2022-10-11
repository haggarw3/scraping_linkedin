from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def login():
    driver = webdriver.Firefox(executable_path='/Users/himanshuaggarwal/PycharmProjects/pythonProject/geckodriver')
    driver.maximize_window()

    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    driver.find_element_by_id('username').send_keys(Keys.COMMAND + "a")
    driver.find_element_by_id('username').send_keys(Keys.DELETE)
    time.sleep(2)
    driver.find_elements_by_id('username')[0].send_keys('himanshu.aggarwal@ironhack.com')
    # driver.find_elements_by_id('username')[0].send_keys('himanshuag098@gmail.com')
    time.sleep(3)
    # print("username successful")
    driver.find_element_by_id('password').send_keys(Keys.COMMAND + "a")
    driver.find_element_by_id('password').send_keys(Keys.DELETE)
    time.sleep(2)
    driver.find_elements_by_id('password')[0].send_keys('Himagga11!')
    # driver.find_elements_by_id('password')[0].send_keys('Hello123')
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    time.sleep(2)
    if 'checkpoint' in driver.current_url:
        driver.find_element_by_xpath('/html/body/div/main/div/section/footer/form[2]/button').click()
        time.sleep(2)
    driver.find_element_by_id('ember24').click()
    time.sleep(2)
    return driver, driver.current_url


if __name__ == 'main':
    login()
