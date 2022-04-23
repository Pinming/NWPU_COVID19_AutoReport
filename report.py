from datetime import *
import requests
import re
from bs4 import BeautifulSoup
import location
import user_config
from pusher import Pusher
from lxml import etree
import time

# URL 常量
url_jrsb = 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp'  # 获取表格并进行操作
url_ry_util = 'https://yqtb.nwpu.edu.cn/wx/ry/ry_util.jsp'  # 用于 POST 申报的内容
url_cas_login = 'https://uis.nwpu.edu.cn/cas/login'  # 用于 Validate 登录状态
url_rzxx_list = 'https://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/rzxx_list.jsp'  # 日报列表


# 构造疫情填报网站对象，attr 实际上为 POST Form 时所需要的一些值
class NWPU_Yqtb_Site(object):
    def __init__(self):
        self.session = requests.Session()
        # 从 CAS 登录页作为登录过程起点
        self.session.get(url_cas_login)
        # 供填报时使用的数据
        self.name = ""
        self.xymc = ""
        self.xssjhm = ""
        self.szcsbm = ""
        self.szcsmc = ""
        # self.hsjc = ""
        self.sign = ""
        self.timeStamp = ""
        self.submit_err_info = ""
        self.data_for_submit = None
    
    # 登录
    def login(self, username, password):
        header_for_login = {
            'referer': url_cas_login,
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
            'content-Type': 'application/x-www-form-urlencoded',
            'origin': 'https://uis.nwpu.edu.cn',
            'cookie': 'SESSION=' + str((self.session.cookies.values()[0])),
            'authority': 'uis.nwpu.edu.cn',
            'path': '/cas/login',
            'scheme': 'https',
            'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'upgrade-insecure-requests': '1',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'cache-control': 'no-cache'
        }
        data_for_login = {
            'username': username,
            'password': password,
            '_eventId': 'submit',
            'currentMenu': '1',
            'execution': 'e2s1',
            'submit': 'One moment please...',
            'geolocation': '',
        }
        self.username = username
        self.password = password
        self.session.get(url_cas_login)
        self.session.headers.update(header_for_login)
        res_login = self.session.post(url_cas_login, data=data_for_login, headers=header_for_login)
        if (res_login.text.find('欢迎使用')) != -1:
            print('登陆成功！')
        else:
            print('登录失败！请检查「登录信息」一栏用户名及密码是否正确')
            if user_config.SC_switcher == 1:
                Pusher.sc_push_when_login_failed(self)
            exit()
    
    # 初始化当次填报信息
    def init_info(self):
        # 在 `/wx/ry/jrsb.jsp` 页面中，获取 `timeStamp` & `sign`。
        res_jrsb = self.session.get(url_jrsb)
        while (res_jrsb.url != "https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp"):
            res_jrsb = self.session.get(url_jrsb)
        
        self.timeStamp = re.findall(re.compile('(?<=&timeStamp=).*(?=\')'),
                                    res_jrsb.text)[0]
        self.sign = re.findall(re.compile('(?<=sign=).*(?=&)'),
                               res_jrsb.text)[0]
        # 在 `/wx/ry/jrsb.jsp` 页面中，获取 `param_data`。
        param_data_str = re.findall(re.compile('var paramData = (.*?);'),
                                    res_jrsb.text)[2]
        # 再在 `param_data` 中获取 `name`、`xymc`、`xssjhm` 三个信息。
        self.name = re.findall(re.compile('(?<=userName:\').*(?=\',szcsbm)'),
                               param_data_str)[0]
        self.xymc = re.findall(re.compile('(?<=xymc:\').*(?=\',)'),
                               param_data_str)[0]
        self.xssjhm = re.findall(re.compile('(?<=xssjhm:\').*(?=\')'),
                                 param_data_str)[0]
        
        
        # 在 `wx/xg/yz-mobile/rzxx_list.jsp` 中，获取 `szcsmc`，并查 `location.py` 得 `szcsbm`
        header_for_rzxx = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
            'Host': 'yqtb.nwpu.edu.cn',
            'cookie': 'showQuestionnaire=-1; JSESSIONID=' + str((self.session.cookies.values()[2])),
            'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'upgrade-insecure-requests': '1',
            'cache-control': 'no-cache'
        }
        rzxx_list = self.session.get(url_rzxx_list, headers=header_for_rzxx)
        rzxx_list_str = rzxx_list.text
        soup = BeautifulSoup(rzxx_list_str, 'html.parser')
        loc_name = soup.find("span", attrs={"class": "status"}).string
        self.szcsmc = loc_name
        loc_code = location.get_location(loc_name)
        if loc_name == "在西安":
            self.szcsbm = "2"
        elif loc_name == "在学校":
            self.szcsbm = "1"
        else:
            self.szcsbm = loc_code[0]
        if self.szcsbm == "" and loc_name != "在西安" and loc_name != "在学校":
            print(
                "获取上一次填报的信息时出现错误！"
                + "\n"
                + "请联系作者（通过 Github Issue 或邮箱：i@pm-z.tech）并附上信息填报网站「个人中心→我的打卡」页面的截图，便于定位问题！"
            )
            if user_config.SC_switcher == 1:
                Pusher.sc_push_when_wrong_info(self)
            exit()
        
        
        # self.hsjc = self.get_last_hsjc_status(data_for_init, header_for_init)
            
                
    
    def submit(self):
        # 伪造一次对 Form 页面的请求，获得 JSESSIONID
        self.session.get(url_jrsb)
        header_for_init = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
            'Host': 'yqtb.nwpu.edu.cn',
            'cookie': 'JSESSIONID=' + str((self.session.cookies.values()[2])),
            'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'upgrade-insecure-requests': '1',
            'cache-control': 'no-cache'
        }
        header_for_submit = {
            "Host": "yqtb.nwpu.edu.cn",
            "Referer": "https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "JSESSIONID=" + str((self.session.cookies.values()[2])),
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.4976.0 Safari/537.36",
            "Content-Length": "196",
        }
        self.data_for_submit = {
            'hsjc': '1',
            'xasymt': '1',
            'actionType': 'addRbxx',
            'userLoginId': self.username,
            'szcsbm': self.szcsbm,
            'bdzt': '1',
            'szcsmc': self.szcsmc,
            'sfyzz': '0',
            'sfqz': '0',
            'tbly': 'sso',
            'qtqksm': '',
            'ycqksm': '',
            'userType': '2',
            'userName': self.name,
        }
        
        # self.judge_last_report_is_today(self.get_last_report_time(data_for_init, header_for_init)) 的意义：
        # 判断系统当前日期是否与最后一次填报的日期一致。
        # 如条件为 False，则不一致，认为今日未填报，执行 POST；
        # 否则跳过 POST 步骤，不再重复填报。
        if not (self.judge_last_report_is_today(self.get_last_report_time(header_for_init))):
            url_ry_util_with_token = url_ry_util + '?sign=' + self.sign + '&timeStamp=' + self.timeStamp
            response_submit = self.session.post(url=url_ry_util_with_token,
                                                data=self.data_for_submit,
                                                headers=header_for_submit)
            self.submit_err_info = response_submit.text.replace('\n', '').replace('\r', '')
        else:
            print('今日已填报，无需重复填报！')
            return
        
        # 判断填报成功
        # 此处逻辑使用 POST 后的返回值来判断，相较于 v2.0.1，不再通过填报历史来判断。
        # 逻辑上只判断当次填报的成功性（为确定当次填报状态而服务），而不是当日填报的成功性（为避免重复填报而服务）。
        # 返回来的 err_code 如 -1 等不是正确的 json 格式，只能用弱智方法判断 err_code == 1 了🤗
        if self.submit_err_info.find('\"state\":\"1\"') != -1:
            print('申报成功！')
            if user_config.SC_switcher == 1:
                Pusher.sc_push_successful(self)
        else:
            print('申报失败，请重试！')
            if user_config.SC_switcher == 1:
                Pusher.sc_push_when_wrong_info(self)
    
    # 获取最近一次日报填写页
    def get_last_report(self, header):
        # GET 日报填写列表页
        rzxx_list_page = self.session.get(url_rzxx_list, headers=header)
        # 获取最近一次日报填写页的 URL
        url_last_detail = "https://yqtb.nwpu.edu.cn" + \
                          etree.HTML(rzxx_list_page.text).xpath('//*[@id="form1"]/div/a[1]/@href')[0]
        # 获取最近一次日报填写页
        detail_page = self.session.get(url_last_detail, headers=header)
        return detail_page.text
    

    # 判断上一次填报是否为今天
    def judge_last_report_is_today(self, report_time):
        # 获取本机时间并转为东 8 区，部分云函数主机上的时间是 UTC 时间，会导致判断有误。
        tz = timezone(timedelta(hours=+8))
        report_time = self.string_toDatetime(report_time)
        if report_time.date() == datetime.today().astimezone(tz).date():
            return True
        else:
            return False
    
    # 获取最近一次填报的时间，判断是否为今天
    def get_last_report_time(self, header):
        last_report_time = \
            etree.HTML(self.get_last_report(header)).xpath(
                '/html/body/div[1]/div[2]/div/div[2]/div[1]/div[2]/text()')[0]
        return last_report_time

    # 把字符串转成 datetime
    def string_toDatetime(self, st):
        return datetime.strptime(st, "%Y-%m-%d %H:%M:%S")