import requests
import re
from bs4 import BeautifulSoup
import location
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import datetime
import pytz

# 登录信息
# --------------------------
username = '2019******'  # 学号
password = '********'  # 翱翔门户密码
# --------------------------

# Email 设置
# 如果邮箱用户名密码有误会导致发不出邮件但仍然提示发送成功！【已知 Bug，后续将修正】
# 有引号的变量（字符串）请不要删去引号。
# --------------------------
# Email 开关，默认打开；如果不需要，将其赋值为 0 则关闭本功能。赋值为其他实数均为打开。
email_switcher = 1
# 发件方邮箱 SMTP 服务器，如果使用 163 邮箱则不必修改；其他邮箱请对应修改
mail_host = "smtp.163.com"  
# 发件方邮箱 SMTP 端口号，一般（163、126、QQ 等）为 465；其他邮箱请自行搜索并修改
mail_SMTPPort = 465  
# 发件邮箱用户名，格式为「*****@**.com」
mail_user = "*****@**.com"
# 一般此处填登录密码
mail_pass = "********"

### 收件人邮箱，填在单引号内；不要删去两侧中括号（使用 list 形式填入）
# 默认设置：如果不修改该项，则发送到发件人邮箱（我发给我自己）
# 如果要发给其他邮箱：
# ---- 单个接收邮箱：['*******@***.com']
# ---- 多个接收邮箱：['******1@***.com', '******2@***.com', ...]
receivers = []   

########## 以下部分一般不需要修改，除非你需要自己定制发送邮件的内容 ##########
# 获取公告 / 请勿删除，便于发送需要用户知悉的信息
url_notice = 'https://oss.pm-z.tech/notice_for_autoreport.txt'
session_notice = requests.session()
notice = session_notice.get(url_notice)
notice.encoding="UTF-8"
notice = notice.content.decode('UTF-8')

if notice != '':
    print(notice)

# 邮件标题
title = '【' + datetime.datetime.now(pytz.timezone('PRC')
                                    ).strftime("%Y/%m/%d") + '】' + '今日健康状况已成功申报！'
# 邮件内容
content = '今日健康状况已成功申报！申报时间：' + datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d %H:%M:%S") + '\n' + \
    '⚠️ 请确保您的身体状况良好再使用该软件，做到如实申报自身身体状况。若身体出现异常，应立即停止使用该软件并及时于学校系统更改每日申报情况。因使用该软件误报身体状况而引发的不良后果应由您自行承担。' + \
    '\n' + '本软件仅限于技术用途，切勿滥用！跟进本软件更新，详见 Github：https://github.com/Pinming/NWPU_COVID19_AutoReport' + '\n' + notice
########## 以上部分一般不需要修改，除非你需要自己定制发送邮件的内容 ##########

########## ·以下内容请不要随意修改· ########## 
# Debug 开关，非调试用途不必打开
debug_switcher = 0

# Email 发件人设置，不必修改
sender = mail_user
if receivers == []:
    receivers = [mail_user]

if debug_switcher == 1:
    print(f'receivers: {receivers}')

# 全局变量
url_Form = 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp' # 获取表格并进行操作
url_Submit = 'http://yqtb.nwpu.edu.cn/wx/ry/ry_util.jsp' # 用于 POST 申报的内容
url_for_id = 'https://uis.nwpu.edu.cn/cas/login' # 用于 Validate 登录状态
url_for_user_info = 'http://yqtb.nwpu.edu.cn/wx/ry/jbxx_v.jsp'  # 「个人信息」一栏
url_for_list = 'http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/rzxx_list.jsp'
url_for_yqtb_logon = 'http://yqtb.nwpu.edu.cn//sso/login.jsp'


# Email 实现 
def sendEmail():
    email_status = 0
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_SMTPPort)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
    except:
        email_status = -1
    return email_status


session = requests.Session() # 全局 session，便于后续函数调用
session.get(url_for_id) # 从 CAS 登录页作为登录过程起点

def login(username=username, password=password):
    header = {
        'referer': url_for_id,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
        'content-Type': 'application/x-www-form-urlencoded',
        'origin': 'https://uis.nwpu.edu.cn',
        'cookie': 'SESSION=' + str((session.cookies.values()[0])),
        'authority': 'uis.nwpu.edu.cn',
        'path': '/cas/login',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'upgrade-insecure-requests': '1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'cache-control': 'no-cache'
    }

    data = {
        'username': username,
        'password': password,
        '_eventId': 'submit',
        'currentMenu': '1',
        'execution': 'e2s1',
        'submit': 'One moment please...',
        'geolocation': '',
    }
    
    session.get(url_for_id)
    session.headers.update(header)
    rt = session.post(url_for_id, data=data, headers=header, timeout=5).text # rt 以 html 形式返回登录状态
    if rt.find('欢迎使用 统一身份认证 系统') != -1:
        print('登录成功！')
    else:
        print('登录失败！请检查「登录信息」一栏用户名及密码是否正确')
        exit()
    if debug_switcher == 1:
        print(session.cookies.values())
    # r2、r3 用于动态获取相关信息填入 Form // for POST
    # r2 操作
    r2 = session.post(url_Form) # 伪造一次对 Form 页面的请求，获得 JSESSIONID
    header3 = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
        'Host': 'yqtb.nwpu.edu.cn',
        'cookie': 'JSESSIONID=' + str((session.cookies.values()[2])),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'upgrade-insecure-requests': '1',
        'cache-control': 'no-cache'
    }
    data2 = {
        'ticket': str((session.cookies.values()[1])),
        'targetUrl': 'base64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A=',
    }

    r_log_on_yqtb2 = session.post(url_for_yqtb_logon, data=data2, headers=header3)
    r2 = r_log_on_yqtb2.text
    # 登录后跳转到主页 [//yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp]；r2 最终可以获取姓名和学院
    soup = BeautifulSoup(r2, 'html.parser')
    global RealCollege, RealName, PhoneNumber
    for k in soup.find('div', string=re.compile('姓名')):
        RealName = k.replace('姓名：', '')
    for l in soup.find('div', string=re.compile('学院')):
        RealCollege = l.replace('学院：', '')

    ## r3 操作
    # 在「基本信息」页面 / 此页面也可获得上述 k,l 信息，之前未发现
    r3 = session.post(url_for_user_info, data=data2, headers=header3).text
    soup2 = BeautifulSoup(r3, 'html.parser')
    m = soup2.find_all('span')
    PhoneNumber = m[6].string  # 提取出列表的 #6 值即为电话号码

    ## r5 操作：获得上一次填报的所在地
    r5 = session.post(url_for_list, data=data2, headers=header3).text
    soup3 = BeautifulSoup(r5, 'html.parser')
    v_loc = soup3.find("span", attrs={"class": "status"}).string
    global loc_name, loc_code_str
    loc_name = v_loc
    loc_code = location.GetLocation(loc_name)
    if loc_name == '在西安' or loc_name == '在学校':
        loc_code_str = ''
    else:
        loc_code_str = loc_code[0]
    if loc_code_str == '' and loc_name != '在西安' and loc_name != '在学校':
        print('获取上一次填报的信息时出现错误！' + '\n' + '请联系作者（通过 Github Issue 或邮箱：i@pm-z.tech）并附上信息填报网站「个人中心→我的打卡」页面的截图，便于定位问题！')
        exit()


    
def submit(loc_code_str, loc_name, RealName, RealCollege, PhoneNumber):
    HeadersForm = {
        'Host': 'yqtb.nwpu.edu.cn',
        'Origin': 'http://yqtb.nwpu.edu.cn',
        'Referer': 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'JSESSIONID=' + str((session.cookies.values()[2])),
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36'
    }
    tbDataForm = {
        'sfczbcqca': '', 
        'czbcqcasjd': '',
        'sfczbcfhyy': '',
        'czbcfhyysjd': '',
        'actionType': 'addRbxx',
        'userLoginId': username,
        'fxzt': '9',
        'userType': '2',
        'userName': RealName, # 真实姓名；实践表明可留空，以防万一填上，下同
        'szcsbm': loc_code_str, # 所在城市编码
        'szcsmc': str(loc_name), # 所在城市名称
        'sfjt': '0', # 是否经停
        'sfjtsm': '', # 是否经停说明
        'sfjcry': '0', # 是否接触人员
        'sfjcrysm': '', # 说明
        'sfjcqz': '0', # 是否接触确诊
        'sfyzz': '0', # 是否有症状
        'sfqz': '0', # 是否确诊
        'ycqksm': '', 
        'glqk': '0', # 隔离情况
        'glksrq': '', # 隔离开始日期
        'gljsrq': '', # 隔离结束日期
        'tbly': 'sso', # 填报来源：SSO 单点登录
        'glyy': '' , # 隔离原因
        'qtqksm': '', # 其他情况说明
        'sfjcqzsm': '',
        'sfjkqk': '0',
        'jkqksm': '', # 健康情况说明
        'sfmtbg': '',
        'qrlxzt': '',
        'xymc': RealCollege, # 学院名称；实践表明可留空
        'xssjhm': PhoneNumber, # 手机号码；实践表明可留空
    }
    header3 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4204.0',
        'Host': 'yqtb.nwpu.edu.cn',
        'cookie': 'JSESSIONID=' + str((session.cookies.values()[2])),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'upgrade-insecure-requests': '1',
        'cache-control': 'no-cache'
    }
    data2 = {
        'ticket': str((session.cookies.values()[1])),
        'targetUrl': 'base64aHR0cDovL3lxdGIubndwdS5lZHUuY24vL3d4L3hnL3l6LW1vYmlsZS9pbmRleC5qc3A=',
    }
    if debug_switcher == 1:
        print(f'最终填报的表格内容：{tbDataForm}')
    session.post(url=url_Submit, data=tbDataForm, headers=HeadersForm)
    r4 = session.get(url=url_Form, data=data2, headers=header3).text
    session.close()
    if (r4.find('重新提交将覆盖上一次的信息')) != -1:
        print('申报成功！')
        if email_switcher == 1:
            email_status = sendEmail()
            if debug_switcher == 1:
                print(f'Email Status: {email_status}')
            if email_status != -1:
                print('邮件已发送！')
            else:
                print('邮件发送失败！请检查 Email 的各项设置（用户名、密码、SMTP 服务器及端口、收件人）等设置填写是否正确！')
    else:
        print('申报失败，请重试！')

def execute(username, password):
    login(username, password)
    submit(loc_code_str, loc_name, RealName, RealCollege, PhoneNumber)

execute(username, password)
