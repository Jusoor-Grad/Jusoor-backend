from django.test import TestCase
from channels.testing import ChannelsLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


class ChatTests(ChannelsLiveServerTestCase):

    serve_static = True

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        try:
            cls.driver = webdriver.Chrome()
        except:
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self):

        try:
            # entering the same chat room in 2 different browser tabs
            self._entter_chat_room('room_1')
            self._open_new_window()
            self._enter_chat_room('room_1')

            # sending hello in first tab for room_1
            self._switch_to_window(0)
            self._post_message('hello')
            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 1 from window 1"
            )

            # checking the content of room_1 in second tab
            self._switch_to_window(1)
            WebDriverWait(self.driver, 2).until(
                lambda _: "hello" in self._chat_log_value,
                "Message was not received by window 2 from window 1"
            )

        finally:
            self._close_all_new_windows()

    def test_when_chat_message_posted_then_not_seen_by_anyone_in_different_room(self):

        try:

            # entering 2 chat rooms in 2 different browser tabs
            self._enter_chat_room('room_1')
            self._open_new_window()
            self._enter_chat_room('room_2')

            # sending hello in first tab in room_1
            self._switch_to_window(0)
            self._post_message('hello')
            WebDriverWait(self.driver, 2).until(
                lambda _: 'hello' in self._chat_log_value,
                'Message was not received by window 1 from window 1'
            )

            # switching to second tab and verifying that hello is not received there
            self._switch_to_window(1)
            self._post_message('world')
            WebDriverWait(self.driver, 2).until(
                lambda _: 'world' in self._chat_log_value,
                'Message was not received by window 2 from window 2'
            )

            self.assertTrue(
                'hello' not in self._chat_log_value,
                "Message was improperly recieved by window 2 from window 1"
            )

        finally:
            self._close_all_new_windows()
    
    def _enter_chat_room(self, room_name):
        """Utility function to enter chat room"""
        self.driver.get(self.live_server_url + '/chat/')
        # sending keyboard stroked to the auto-focused text field in the HTML page 
        # to enter the named chat room
        ActionChains(self.driver).send_keys(room_name, Keys.ENTER).perform()
        # confirm that the page URL has moved to the deisgnated room channel
        WebDriverWait(self.driver, 2).until(
            lambda _: room_name in self.driver.current_url
        )

    def _open_new_window(self):
        self.driver.execute_script('window.open("about:blank", "_blank");')
        self._switch_to_window(-1) ## go to last opened window

    
    def _close_all_windows(self):

        while len(self.driver.window_handles) > 1:

            self._switch_to_window(-1)
            self.driver.execute_script('window.close();')
        
        if len(self.driver.window_handles) == 1:
            self._switch_to_window(0)

    def _switch_to_window(self, window_index):
        self.driver.switch_to.window(self.driver.window_handles[window_index])

    def _post_message(self, message):
        ActionChains(self.driver).send_keys(message, Keys.ENTER).perform()
