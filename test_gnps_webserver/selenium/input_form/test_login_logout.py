# -*- coding: utf-8 -*-
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re

class Proteomics2LoginLogout(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(30)
        self.base_url = os.environ.get("SERVER_URL", "https://gnps.ucsd.edu/")
        print("Testing", self.base_url)
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_proteomics2_login_logout(self):
        driver = self.driver
        driver.get("{}/ProteoSAFe/user/login.jsp?test=true".format(self.base_url))
        for i in range(60):
            try:
                if self.is_element_present(By.NAME, "user"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_name("user").clear()
        driver.find_element_by_name("user").send_keys("test")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("testtest")
        driver.find_element_by_name("login").click()
        for i in range(60):
            try:
                if "Successful login" == driver.find_element_by_xpath("//h1").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        for i in range(60):
            try:
                if "Logout" == driver.find_element_by_xpath("//a[@href=\"/ProteoSAFe/user/logout.jsp\"]").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.find_element_by_link_text("Logout").click()
        for i in range(60):
            try:
                if "Successful logout" == driver.find_element_by_xpath("//h1").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: 
            return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
