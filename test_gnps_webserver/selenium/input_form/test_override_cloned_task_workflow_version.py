# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import unittest, time, re

class OverrideClonedTaskWorkflowVersion(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(30)
        self.base_url = "https://proteomics3.ucsd.edu/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_override_cloned_task_workflow_version(self):
        driver = self.driver
        driver.get("{}/ProteoSAFe/user/login.jsp?test=true".format(self.base_url))
        # log in as test user
        print("Logging in as test user.")
        for i in range(60):
            try:
                if self.is_element_present(By.NAME, "user"): break
            except: 
                pass
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
        # clone reference task (version "1.2.5") and verify that input form is loaded
        print("Cloning reference task with version \"1.2.5\".")
        driver.get("{}/ProteoSAFe/index.jsp?task=e95433bf446741dfb10fbe94153bfaee&test=true".format(self.base_url))
        for i in range(60):
            try:
                if "visibility: hidden;" == driver.find_element_by_id("overlay").get_attribute("style"): break
            except:
                pass
            time.sleep(1)
        else: self.fail("time out")

        print("XXXX")

        # get current value of workflow selector drop-down list
        workflow_selector = Select(driver.find_element_by_id("workflowselector_select"))
        selected_workflow = workflow_selector.first_selected_option
        if not selected_workflow:
            self.fail("Could not find selected workflow.")
        # get selected workflow version; should be the same as the cloned task version
        version = re.search(r'\((.*?)\)', selected_workflow.text).group(1)
        if not version:
            self.fail("could not extract version from selected workflow value [" + selected_workflow + "].")
        self.assertEqual(version, "1.2.5")
        # clone reference task and explicitly set workflow version to "release_8"
        print("Cloning reference task, setting version to \"release_8\".")
        driver.get("{}/ProteoSAFe/index.jsp?task=e95433bf446741dfb10fbe94153bfaee&params={%22workflow_version%22:%22release_8%22}&test=true".format(self.base_url))
        for i in range(60):
            try:
                if "visibility: hidden;" == driver.find_element_by_id("overlay").get_attribute("style"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        # verify that selected workflow version is "release_8"
        workflow_selector = Select(driver.find_element_by_id("workflowselector_select"))
        selected_workflow = workflow_selector.first_selected_option
        if not selected_workflow:
            self.fail("Could not find selected workflow.")
        version = re.search(r'\((.*?)\)', selected_workflow.text).group(1)
        if not version:
            self.fail("could not extract version from selected workflow value [" + selected_workflow + "].")
        self.assertEqual(version, "release_8")
        # clone reference task and set workflow version to "current"
        print("Cloning reference task, setting version to \"current\".")
        driver.get("{}/ProteoSAFe/index.jsp?task=e95433bf446741dfb10fbe94153bfaee&params={%22workflow_version%22:%22current%22}&test=true".format(self.base_url))
        for i in range(60):
            try:
                if "visibility: hidden;" == driver.find_element_by_id("overlay").get_attribute("style"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        # verify that selected workflow version is "release_8"
        workflow_selector = Select(driver.find_element_by_id("workflowselector_select"))
        selected_workflow = workflow_selector.first_selected_option
        if not selected_workflow:
            self.fail("Could not find selected workflow.")
        version = re.search(r'\((.*?)\)', selected_workflow.text).group(1)
        if not version:
            self.fail("could not extract version from selected workflow value [" + selected_workflow + "].")
        # the current version will presumably change over time, but it
        # should always be different from both versions already tested
        self.assertNotEqual(version, "1.2.5")
        self.assertNotEqual(version, "release_8")
        
    
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
