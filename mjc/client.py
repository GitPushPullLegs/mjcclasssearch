import requests
from urllib.parse import urlsplit, urljoin, quote, unquote
from collections import deque
from mjc.helpers import *
from lxml import etree




class Client:
    _HEADERS = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    _HOST = r'https://myapps.yosemite.edu/'

    def __init__(self):
        self.session = requests.session()
        self.visit_history = deque(maxlen=10)
        self.session.headers.update(self._HEADERS)

    def get_courses(self, term: Term, subject: Subject=Subject.All, course_number=None, section_number=None, title_keyword=None):
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
            'ctl00$ContentPlaceHolder1$txt_StartDate': '',
            'ctl00$ContentPlaceHolder1$txt_EndDate': '',
            'ctl00$ContentPlaceHolder1$ddl_StartTime': '',
            'ctl00$ContentPlaceHolder1$ddl_EndTime': '',
            'ctl00$ContentPlaceHolder1$txtWaitLess': ''
        }

        response = self.session.post(urljoin(self._HOST, '/mjcclasssearch/SearchCriteria.aspx'), data=payload)
        root = etree.fromstring(response.text, parser=etree.HTMLParser(encoding='utf8'))
        table = root.xpath("//table[@id='ctl00_ContentPlaceHolder1_tbl_Result']")[0]

        rows = iter(table)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col.text for col in row]
            print(dict(zip(headers, values)))