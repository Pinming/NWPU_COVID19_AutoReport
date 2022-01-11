import requests
import re
from bs4 import BeautifulSoup
import location
import user_config
from pusher import Pusher

# URL 常量
url_jrsb = 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp'  # 获取表格并进行操作
url_ry_util = 'http://yqtb.nwpu.edu.cn/wx/ry/ry_util.jsp'  # 用于 POST 申报的内容
url_cas_login = 'https://uis.nwpu.edu.cn/cas/login'  # 用于 Validate 登录状态
url_ry_jbxx = 'http://yqtb.nwpu.edu.cn/wx/ry/jbxx_v.jsp'  # yqtb 系统「基本信息」一栏
url_rzxx_list = 'http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/rzxx_list.jsp'  # 日报列表
url_sso_login = 'http://yqtb.nwpu.edu.cn//sso/login.jsp'


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
        self.sign = ""
        self.timeStamp = ""
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
        self.session.post(url_jrsb)
        header_for_init = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
            'Hsost': 'yqtb.nwpu.edu.cn',
            'cookie': 'JSESSIONID=' + str((self.session.cookies.values()[2])),
            'accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'upgrade-insecure-requests': '1',
            'cache-control': 'no-cache'
        }
        data_for_init = {
            'ticket':
                str((self.session.cookies.values()[1])),
            'targetUrl':
                'base64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A=',
        }
        res_jrsb = self.session.post(url_jrsb,
                                      data=data_for_init,
                                      headers=header_for_init)
        self.timeStamp = re.findall(re.compile('(?<=&timeStamp=).*(?=\')'),
                                    res_jrsb.text)[0]
        self.sign = re.findall(re.compile('(?<=sign=).*(?=&)'),
                               res_jrsb.text)[0]
        param_data_str = re.findall(re.compile('var paramData = (.*?);'),
                                    res_jrsb.text)[2]
        self.name = re.findall(re.compile('(?<=userName:\').*(?=\',szcsbm)'),
                                   param_data_str)[0]
        self.xymc = re.findall(re.compile('(?<=xymc:\').*(?=\',)'),
                               param_data_str)[0]
        self.xssjhm = re.findall(re.compile('(?<=xssjhm:\').*(?=\')'),
                                 param_data_str)[0]
        
        rzxx_list_str = self.session.post(url_rzxx_list, data=data_for_init, headers=header_for_init).text
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
    
    def submit(self):
        # 伪造一次对 Form 页面的请求，获得 JSESSIONID
        self.session.get(url_jrsb)
        header_for_submit = {
            "Host": "yqtb.nwpu.edu.cn",
            "Origin": "http://yqtb.nwpu.edu.cn",
            "Referer": "http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "JSESSIONID=" + str((self.session.cookies.values()[2])),
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36",
        }
        self.data_for_submit = {
            'actionType': 'addRbxx',
            'userLoginId': self.username,
            'sfjt': '0',
            'sfjcry': '0',
            'sfjcqz': '0',
            'sfjkqk': '0',
            'sfyzz': '0',
            'sfqz': '0',
            'glqk': '0',
            'tbly': 'sso',
            'userType': '2',
            'userName': self.name,
            'bdzt': '1',
            'xymc': self.xymc,
            'xssjhm': self.xssjhm,
            'szcsmc': self.szcsmc,
            'szcsbm': self.szcsbm,
            'hsjc': '1',  # TODO: 后续再加获取以前记录
        }
        self.data_for_submit
        url_ry_util_with_token = url_ry_util + '?sign=' + self.sign + '&timeStamp=' + self.timeStamp
        self.session.post(url=url_ry_util_with_token,
                          data=self.data_for_submit,
                          headers=header_for_submit)
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
        data_for_init = {
            'ticket':
                str((self.session.cookies.values()[1])),
            'targetUrl':
                'base64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A=',
        }
        res_submit_page_text = self.session.get(url_jrsb,
                                                data=data_for_init,
                                                headers=header_for_init).text
        if (res_submit_page_text.find('重新提交将覆盖上一次的信息')) != -1:
            print('申报成功！')
            if user_config.SC_switcher == 1:
                Pusher.scPush(self)
        else:
            print('申报失败，请重试！')
