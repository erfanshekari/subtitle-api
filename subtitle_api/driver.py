from selenium.webdriver.remote.webdriver import BaseWebDriver, WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class SubtitleApiWebDriver:
    # base_url:str
    # driver:BaseWebDriver
    def __init__(self, driver:BaseWebDriver, base_url:str) -> None:
        self.base_url = base_url
        self.driver:WebDriver = driver
        print(self.driver)

    def page_is_valid(self, driver: WebDriver) -> bool:
        if driver.find_element(By.XPATH, '//*[@id="logo"]'):
            return True

    def get_html(self, url:str, timeout:int = 20) -> str:
        self.driver.get(url)
        self.driver.set_page_load_timeout(timeout)
        def get_source(driver):
            if (self.page_is_valid(driver)):
                return self.driver.page_source
        try:
            return WebDriverWait(self.driver, timeout).until(get_source)
        except Exception as exc:
            self.close()
            raise exc

    def search_by_title(self, title:str, timeout:int = 20) -> str:
        print(self, title)
        self.driver.get(self.base_url)
        self.driver.set_page_load_timeout(timeout)
        def handle_search(driver):
            if self.page_is_valid(driver):
                textbox = self.driver.find_element(By.XPATH, '//*[@id="query"]')
                search_button = self.driver.find_element(By.XPATH, '//*[@id="search-form"]/button')
                if textbox and search_button:
                    textbox.send_keys(title)
                    search_button.click()
                if 'searchbytitle' in self.driver.current_url and self.page_is_valid(self.driver):
                    return self.driver.page_source
        try:
            return WebDriverWait(self.driver, timeout).until(handle_search)
        except Exception as exc:
            self.close()
            raise exc

    def close(self) -> None:
        self.driver.quit()    
    