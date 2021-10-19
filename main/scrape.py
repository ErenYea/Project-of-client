from selenium import webdriver
from selenium.webdriver.chrome import options
import time
import re
import main.constants as const
from selenium.webdriver.support.ui import Select
from concurrent import futures
import pandas as pd


class Scrape(webdriver.Chrome):
    options = options.Options()
    options.headless = False
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # initializing the webdriver instance

    def __init__(self, ):
        super(Scrape, self).__init__(options=self.options)
        self.result = {}
        self.results = {}
        self.state = None
        self.states = {}
        self.city = None
        self.cities = []
        self.date_from = None
        self.date_to = None
        self.count = 0
        self.headers = ['State', 'City', 'Range of Dates from:', 'Range of Dates to:', 'FULL NAME OF THE DECEASED PERSON WITHOUT COMMAS', 'FULL NAME OF THE DECEASED PERSON WITH COMMAS', 'YEAR OF BIRTH', 'YEAR OF DEATH', 'DATE OF DEATH', 'Funeral Home Name',
                        'Funeral Home Street Address', 'Funeral Home City', 'Funeral Home State', 'Funeral Home ZIP Code', 'Upcoming Service Name', 'Upcoming Service Date', 'Upcoming Service City', 'List of Next of Kin', "Link to the deceased person's obituary"]
        self.implicitly_wait(const.IMPLICIT_WAIT)
        self.df = pd.DataFrame([], columns=self.headers)

    # Loading the frist page
    def land_on_first_page(self):
        self.get(const.BASE_URL)

    def click_on_popup(self):

        btn = self.find_element_by_xpath(
            "//div[@class='fc-dialog-container']/div/div[2]/div[2]/button")

        print(btn)

        btn.click()

    # Selecting the country
    def select_contry(self):
        select = Select(self.find_element_by_id(
            'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlCountry'))
        select.select_by_visible_text('United States')

    # Getting the names of state

    def get_states(self):
        states = self.find_elements_by_xpath(
            "//select[@id='ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlState']/option")
        for i in states:
            print(f"Value: {i.get_attribute('value')} , Text: {i.text}")
            self.states[i.get_attribute('value')] = i.text

    # Takingt the input of state
    def input_state(self, state=''):
        select = Select(self.find_element_by_id(
            'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlState'))

        if state == '':
            
            select.select_by_value('57')
            self.state = self.states['57']
            
        else:
            
            select.select_by_value(state)
            self.state = self.states[state]

     # selecting the keywords
    def keyword(self, keyword=''):
        key = self.find_element_by_id(
            'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_txtKeyword')
        self.city = keyword
        key.send_keys(keyword)

    # Selecting the date

    def select_date(self):
        select = Select(self.find_element_by_id(
            'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchWideControl_ddlSearchRange'))
        select.select_by_value('88888')

    # Selcting the date range
    def date_range(self, date_from='02/12/2020', date_to='02/12/2021'):
        div_tag_for_date = self.find_elements_by_class_name('DateValue')
        self.date_from = date_from
        self.date_to = date_to
        print(len(div_tag_for_date))
        date_from_tag = div_tag_for_date[0].find_element_by_tag_name('input')
        date_to_tag = div_tag_for_date[1].find_element_by_tag_name('input')
        date_from_tag.clear()
        date_to_tag.clear()
        date_from_tag.send_keys(date_from)
        date_to_tag.send_keys(date_to)

    # Clicking on search button
    def search(self):
        search = self.find_element_by_link_text("Search")
        search.click()

    # testing the condtition of result
    def get_result(self):
        try:
            result = self.find_element_by_class_name('RefineMessage').text
            print(result)
            if '1000+' in result:
                return True
            elif 'did not find any obituaries' in result:
                return 'Didnot'
            else:
                return False
        except:
            return False

    def click_all_results(self):
        try:
            result = self.find_element_by_class_name('RefineMessage').text
            if 'View all results.' in result:
                self.find_element_by_id(
                    'ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_uxSearchLinks_ViewAllLink').click()
        except:
            pass

    # scrolling down the window to show all the results
    def scrolldown(self):
        # Get scroll height
        last_height = self.execute_script("return document.body.scrollHeight")
        print(f"last_height {last_height}")

        while True:
            # Scroll down to bottom
            self.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(const.SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def result_to_csv(self, name='result.csv'):
        result = self.find_element_by_xpath('//div[@class="Obituaries"]')
        results = self.find_elements_by_xpath('//div[@class="mainScrollPage"]')

        for i in results:
            a = i.find_elements_by_class_name('entryContainer')
            print(len(a))
            for j in a:
                s = j.find_element_by_class_name("obitName")
                h = s.find_element_by_tag_name('a')
                print(f"TExt: {s.text}  link: {h.get_attribute('href')}")

                self.result[s.text] = h.get_attribute('href')
                print("\n")
        self.close()

    def read_result(self, key):
        driver = webdriver.Chrome(options=self.options)
        url = self.result[key]
        print(
            f"----------------- Extracting Data about {key} -----------------")
        print('')
        try:
            driver.get(url)
            driver.implicitly_wait(100)
            para = driver.find_element_by_xpath(
                "//div[@data-component='ObituaryParagraph']").text.split('.\n')

            try:
                dob = driver.find_element_by_xpath(
                    "//div[@class='Box-sc-5gsflb-0 iobueB']/div/div/div/div").text
                dod = driver.find_element_by_xpath(
                    "//div[@class='Box-sc-5gsflb-0 iobueB']/div/div[2]/div/div").text

            except:
                dob = '-'
                dod = '-'

            try:
                funeral_home_list = driver.find_element_by_xpath(
                    "//div[@class='Box-sc-5gsflb-0 iobueB']/div[2]/div").text.split('\n')
                funeral_home_name = funeral_home_list[1]
                funeral_home_street = funeral_home_list[2]
                funeral_home_city = funeral_home_list[3].split(',')[0]
                funeral_home_state = funeral_home_list[3].split(',')[1]
                funeral_home_zipcode = '-'

            except:
                try:
                    funeral_home_list = driver.find_element_by_xpath(
                        "//div[@class='Box-sc-5gsflb-0 iobueB']/div[2]/div").text.split('\n')
                    funeral_home_name = funeral_home_list[1]
                    funeral_home_street = funeral_home_list[2]
                    funeral_home_city = funeral_home_list[3].split(',')[0]
                    funeral_home_state = funeral_home_list[3].split(',')[1]
                    funeral_home_zipcode = '-'
                except:
                    funeral_home_name = '-'
                    funeral_home_street = '-'
                    funeral_home_city = '-'
                    funeral_home_state = '-'
                    funeral_home_zipcode = '-'
            try:
                date_of_death = re.findall(
                    "\w+.\s+\d{1,2},\s+\d{4}", para[0])[0]
            except:
                date_of_death = '-'

            TITLE = r"(?:[A-Z][a-z]*\.\s*)?"
            NAME1 = r"[A-Z][a-z]+,?\s+"
            MIDDLE_I = r"(?:[A-Z][a-z]*\.?\s*)?"
            NAME2 = r"[A-Z][a-z]+"
            res = re.findall(TITLE + NAME1 + MIDDLE_I + NAME2, para[0])
            if 'In Loving Memory' in res[0]:
                full_name = res[1]
            else:
                full_name = res[0]
            if ',' in full_name:
                full_name_with_commas = full_name
                full_name_without_commas = ''
            else:
                full_name_with_commas = ''
                full_name_without_commas = full_name

            try:
                upcoming_service_list = driver.find_elements_by_xpath(
                    "//div[@class='Box-sc-5gsflb-0 bQzMjo']/div[2]/div[@class='Box-sc-5gsflb-0 kwgeEM']")[0].text.split('\n')
                if 'Plant Memorial Trees' in upcoming_service_list[-1]:
                    upcoming_service_month = ''
                    upcoming_service_day = '-'
                    upcoming_service_name = upcoming_service_list[-1]
                else:
                    upcoming_service_month = upcoming_service_list[0]
                    upcoming_service_day = upcoming_service_list[1]
                    upcoming_service_name = upcoming_service_list[2]
            except:
                upcoming_divs = driver.find_elements_by_xpath(
                    "//div[@class='Box-sc-5gsflb-0 bQzMjo']/div[2]/div[@class='Box-sc-5gsflb-0 irxurr']")
                upcoming_service_month = []
                upcoming_service_day = []
                upcoming_service_name = []

                for i in upcoming_divs:
                    j = i.text.split('\n')
                    if 'Plant Memorial Trees' in j[-1]:
                        upcoming_service_month.append('-')
                        upcoming_service_day.append('-')
                        upcoming_service_name.append(j[-1])
                    else:
                        upcoming_service_month.append(j[0])
                        upcoming_service_day.append(j[1])
                        upcoming_service_name.append(j[2])

            upcoming_service_date = ''
            try:

                for i in range(0, len(upcoming_service_month)):
                    if i == len(upcoming_service_month)-1:
                        upcoming_service_date += f'{upcoming_service_month[i]}-{upcoming_service_day[i]}'
                    else:
                        upcoming_service_date += f'{upcoming_service_month[i]}-{upcoming_service_day[i]}, '

                if len(upcoming_service_name) == 1:
                    upcoming_service_name = upcoming_service_name[0]
                else:
                    upcoming_service_names = upcoming_service_name
                    upcoming_service_name = ''
                    for i in range(0, len(upcoming_service_names)):
                        if i == len(upcoming_service_names)-1:
                            upcoming_service_name += f'{upcoming_service_names[i]}'
                        else:
                            upcoming_service_name += f'{upcoming_service_names[i]}, '

            except:
                upcoming_service_name = ''
                upcoming_service_date = ''

            keywords = ['Preceded', 'Survived', 'Wife', 'Husband', 'Mother', 'Father', 'Sister', 'Brother', 'civil partner', 'daughter', 'son', 'parents', 'grandparent', 'grandchild', 'parent-in-law', 'son-in-law', 'daughter-in-law', 'sister-in-law', 'brother-in-law', 'stepmother', 'step mother', 'stepfather', 'step father', 'stepchild', 'step child', 'stepsister', 'step sister',
                        'stepbrother', 'step brother', 'foster child', 'guardian', 'domestic partner', 'fiancé', 'fiancée', 'bride', 'dad', 'mom', 'grandchild', 'grandchildren', 'granddaughter', 'grandfather', 'granddad', 'grandpa', 'grandmother', 'grandma', 'grandson', 'great-grandparents', 'groom', 'half-brother', 'mother-in-law', 'mum', 'mummy', 'nephew', 'niece', 'twin', 'twin-brother', 'siblings']
            lst = []
            for i in keywords:
                for j in para:
                    if i in j:
                        if j in lst:
                            continue
                        lst.append(j)

            lonok = ''
            for i in lst:
                lonok += i

            rows = {'State': self.state, 'City': self.city, 'Range of Dates from:': self.date_from, 'Range of Dates to:': self.date_to, 'FULL NAME OF THE DECEASED PERSON WITHOUT COMMAS': full_name_without_commas, 'FULL NAME OF THE DECEASED PERSON WITH COMMAS': full_name_with_commas, 'YEAR OF BIRTH': dob, 'YEAR OF DEATH': dod, 'DATE OF DEATH': date_of_death, 'Funeral Home Name': funeral_home_name,
                    'Funeral Home Street Address': funeral_home_street, 'Funeral Home City': funeral_home_city, 'Funeral Home State': funeral_home_state, 'Funeral Home ZIP Code': funeral_home_zipcode, 'Upcoming Service Name': upcoming_service_name, 'Upcoming Service Date': upcoming_service_date, 'Upcoming Service City': funeral_home_city, 'List of Next of Kin': lonok, 'Link to the deceased person': url}

            self.df = self.df.append(rows, ignore_index=True)

        except Exception as e:
            print(e)
            print('Url denied')
        driver.close()

    def runscrapper(self):
        with futures.ThreadPoolExecutor() as executor:
            # store the url for each thread as a dict, so we can know which thread fails
            future_results = {key: executor.submit(
                self.read_result, key) for key in self.result}
            for key, future in future_results.items():
                try:
                    future.result()  # can use `timeout` to wait max seconds for each thread
                except Exception as exc:  # can give a exception in some thread
                    print(
                        'url {:0} generated an exception: {:1}'.format(key, exc))
