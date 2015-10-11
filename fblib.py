#!/usr/bin/python
# -*- coding: latin-1 -*-

import facebook
import requests

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException



def test():
    print "test"


def login():

    try:
        browser = webdriver.Firefox() #open the firefox browser
        wait = WebDriverWait(browser, 10)
        browser.maximize_window()
        browser.get('https://www.facebook.com')

        #assert 'Welcome to Facebook - Log In, Sign Up or Learn More' in browser.title #control if the title matches

        elem_name = wait.until(EC.presence_of_element_located((By.NAME,'email')))
        elem_pw = wait.until(EC.presence_of_element_located((By.NAME,'pass')))

        #SET MAIL AND PASSWORD!
        elem_name.send_keys('')
        elem_pw.send_keys('' + Keys.RETURN)

    except Exception, e:
        raise e

    finally:
        print "Login Terminated!"

    return browser

def logout(browser):
    browser.quit()


def get_page_fan_links(page_id):
    """
    This function returns a list of 100 IDs of the people that like a given page
    It is indipendent from the login
    """

    browser = webdriver.Firefox() #open the firefox browser
    browser.maximize_window()

    browser.get('https://www.facebook.com/plugins/fan.php?connections=100&id=' + str(page_id))

    result_list = []

    #FB's social plugin returns only 100 results at time. we'll refresh the page to get others
    for x in range (1,100):
        try:

            print "/html/body/div/div/div/div[5]/ul/li[%d]/a" % x
            result_list.append(browser.find_element_by_xpath('/html/body/div/div/div/div[5]/ul/li[%d]/a' % x).get_attribute('href'))

        except NoSuchElementException:
            
            print "missing element, go on"
            continue

    return result_list #to be precise returns a list of fb link e.g. "facebook.com/marta.sala9"


def get_group_member_ids(group_id):
    """
    This function returns a list containing the IDs of the members of a group
    It is indipendent from the login
    """

    graph = facebook.GraphAPI(access_token='')

    group_members = graph.get_connections(id = str(group_id), connection_name='members')

    result_list = []    #lista da ritornare

    x = 0

    while True:
        try:
            result_list.append(group_members[u'data'][x][u'id'])
            x += 1
        except IndexError:
            print "trovati : " + str(x) + " membri"
            break
        
    print result_list[160:170]

    return result_list


def send_friend_request(browser, person_id):

    wait = WebDriverWait(browser, 10)

    try:
        time.sleep(3)

        ##PER LISTE DI ID
        browser.get('https://www.facebook.com/' + person_id)

        ##PER LIST DI LINKS
        #browser.get(person_id)

        elem_add_request = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'FriendRequestAdd')))
        elem_add_request.click() #friendship request sent

        time.sleep(3)

        browser.refresh()   #necessary, it doesn't work without a refresh

        elem_amicizia_inviata = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'FriendRequestOutgoing')))

        action = webdriver.common.action_chains.ActionChains(browser)
        action.move_to_element_with_offset(elem_amicizia_inviata, 5, 5)
        action.click()
        action.perform()

        elem_amicizia_cancel = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'FriendListCancel')))
        elem_amicizia_cancel.click()

        elem_amicizia_confirm_cancel = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'layerConfirm')))
        elem_amicizia_confirm_cancel.click()

    except TimeoutException:
        print "Time exceeded for finding the element! :("
    except Exception, e:
        raise e

    finally:
        print "E questo è fatto"
   