import re
import pandas as pd
from django.test import LiveServerTestCase
from parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from core.models import Task
from topic.models import Topic

SCENARIOS_PATH = "https://docs.google.com/spreadsheets/d/1siwC0S1vgs_BB9lQC6z7J1smTDFA3P0oJMfcSy7DYME/export?gid=0&format=csv"


class SyntheticDataIntegrationTestCase(LiveServerTestCase):

    def setUp(self) -> None:

        with open('./fixtures/test_ingest.py') as f:
            exec(f.read())
        self.df = pd.read_csv(
            SCENARIOS_PATH,
        )

    @parameterized.expand([(i,) for i in pd.read_csv(SCENARIOS_PATH).scenario.tolist()])
    def test_stuff(self, scenario):
        print("test")
        selenium = webdriver.Chrome(ChromeDriverManager().install())
        selenium.get(self.live_server_url)
        user = selenium.find_element(By.ID, 'id_login')
        password = selenium.find_element(By.ID, 'id_password')
        submit = selenium.find_element(By.XPATH, "/html/body/div/form/button")

        user.send_keys('test_user')
        password.send_keys('test_user@example.com')

        submit.send_keys(Keys.RETURN)

        assert 'Start Judgment' in selenium.page_source

        select = Select(selenium.find_element(By.ID, 'slct'))
        select.select_by_visible_text(scenario)
        submit = selenium.find_element(By.XPATH, "//*[@id='container']/div/div/button")
        submit.send_keys(Keys.RETURN)

        print(0)
        while True:
            if 'task_status = "complete"' in selenium.page_source:
                break
            l_doc = selenium.find_element(By.ID, "left-doc")
            r_doc = selenium.find_element(By.ID, "right-doc")

            l_title = re.search("^Title: (\w\d+)", l_doc.text).group(1)
            r_title = re.search("^Title: (\w\d+)", r_doc.text).group(1)

            if l_title[0] < r_title[0]:
                submit = selenium.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/form/button[1]")
                submit.send_keys(Keys.RETURN)
            elif l_title[0] > r_title[0]:
                submit = selenium.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/form/button[3]")
                submit.send_keys(Keys.RETURN)
            elif l_title[0] == r_title[0]:
                submit = selenium.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/form/button[2]")
                submit.send_keys(Keys.RETURN)
        submit = WebDriverWait(selenium, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ccomplete-modal"]/div/div/div[2]/form/button')))
        submit.click()
        assert 'Start Judgment' in selenium.page_source
        WebDriverWait(selenium, 20)
        topic = Topic.objects.filter(title=scenario).first()
        task = Task.objects.filter(topic_id=topic.id).first()
        got = ''.join(sum([[y[0] for y in x.split('|') if y] for x in task.best_answers.split('--') if x], []))
        expected = ''.join([x[0] for x in self.df[self.df.scenario == scenario].iloc[0].expected.split()])
        assert got == expected
