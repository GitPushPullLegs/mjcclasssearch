from collections import deque
from urllib.parse import urljoin

import requests
from lxml import etree

from mjc.helpers import *


class Client:
    _HEADERS = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    _HOST = r'https://myapps.yosemite.edu/'

    def __init__(self):
        self.session = requests.session()
        self.visit_history = deque(maxlen=10)
        self.session.headers.update(self._HEADERS)

    def get_courses(self, term: Term, subject: Subject = Subject.All, course_number=None, section_number=None,
                    title_keyword=None, zero_textbook_cost: bool = False, campus=None, environment=None, meet_days=None,
                    late_start: bool = False, short_term=None, start_date: str = None, end_date: str = None,
                    start_time=None, end_time=None, class_status=None, max_wait_list: int = -1,
                    instructor_last_name: str = None, include_columbia_college: bool = False):

        response = self.session.get(urljoin(self._HOST, 'mjcclasssearch'))
        self.session.cookies.update(response.cookies.get_dict())
        root = etree.fromstring(response.text, parser=etree.HTMLParser(encoding='utf8'))
        payload = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': root.xpath("//input[@id='__VIEWSTATE']")[0].get('value'),  #
            '__VIEWSTATEGENERATOR': 91753618,
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 0,
            '__EVENTVALIDATION': root.xpath("//input[@id='__EVENTVALIDATION']")[0].get('value'),  #
            'ctl00$ContentPlaceHolder1$ddl_Term': term.value,
            'ctl00$ContentPlaceHolder1$lb_Subject': subject.value,
            'ctl00$ContentPlaceHolder1$txt_CourseNo': '' if not course_number else course_number,
            'ctl00$ContentPlaceHolder1$txt_SecNum': '' if not section_number else section_number,
            'ctl00$ContentPlaceHolder1$txt_TitleKeyword': '' if not title_keyword else title_keyword,
            'ctl00$ContentPlaceHolder1$Button2': 'Submit',
            'ctl00$ContentPlaceHolder1$txt_StartDate': '' if not start_date else start_date,  # 03/15/2021
            'ctl00$ContentPlaceHolder1$txt_EndDate': '' if not end_date else end_date,
            'ctl00$ContentPlaceHolder1$ddl_StartTime': '' if not start_time else start_time,  # 06:00
            'ctl00$ContentPlaceHolder1$ddl_EndTime': '' if not end_time else end_time,  # 21:00
            'ctl00$ContentPlaceHolder1$txtWaitLess': '' if max_wait_list == -1 else max_wait_list
        }

        if zero_textbook_cost: payload['ctl00$ContentPlaceHolder1$cb_FreeResource'] = 'on'
        payload.update(self._payload_option_handler(campus))
        payload.update(self._payload_option_handler(environment))
        payload.update(self._payload_option_handler(meet_days))
        if late_start: payload['ctl00$ContentPlaceHolder1$cb_LateStartClasses'] = 'on'
        payload.update(self._payload_option_handler(short_term))
        payload.update(self._payload_option_handler(class_status))
        if instructor_last_name: payload['ctl00$ContentPlaceHolder1$txt_InstrName'] = instructor_last_name
        if include_columbia_college: payload['ctl00$ContentPlaceHolder1$cb_OtherCollege'] = 'on'

        response = self.session.post(urljoin(self._HOST, '/mjcclasssearch/SearchCriteria.aspx'), data=payload)
        root = etree.fromstring(response.text, parser=etree.HTMLParser(encoding='utf8'))
        table = root.xpath("//table[@id='ctl00_ContentPlaceHolder1_tbl_Result']")[0]

        rows = iter(table)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col.text for col in row]
            print(dict(zip(headers, values)))

    def _payload_option_handler(self, input):
        payload = {}
        if input:
            if isinstance(input, list):
                for each in list(set(input)):
                    payload[each.value] = 'on'
            else:
                payload[input.value] = 'on'
        return payload
