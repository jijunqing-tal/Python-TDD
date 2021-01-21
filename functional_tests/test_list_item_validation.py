from .base import FunctionalTest

from selenium.webdriver.common.keys import Keys
from unittest import skip

class NewViewerTest(FunctionalTest):
    def test_cannot_add_empty_list_item(self):
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda :
                self.browser.find_element_by_css_selector('#id_text:invalid')
        )
        self.get_item_input_box().send_keys('Buy milk')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy milk')

        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda:
                      self.browser.find_element_by_css_selector('#id_text:invalid')
        )

        self.get_item_input_box().send_keys('Make tea')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy milk')
        self.wait_for_row_in_list_table('2:Make tea')