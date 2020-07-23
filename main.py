import requests
import re
from bs4 import BeautifulSoup
import location
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import time

# 登录信息
# --------------------------
username = '2019******' # 学号
password = 'abcd123456' # 翱翔门户密码

# Email 设置
# 如果邮箱用户名密码有误会导致发不出邮件但仍然提示发送成功！【已知 Bug，后续将修正】
# 有引号的变量（字符串）请不要删去引号。
# --------------------------
# Email 开关，默认打开；如果不需要，将其赋值为 0 则关闭本功能。赋值为其他实数均为打开。
email_switcher = 1
# SMTP 服务器，如果使用 163 邮箱则不必修改；其他邮箱请参见说明
mail_host = "smtp.163.com"  
# SMTP 端口号，一般为 465；其他邮箱请参见说明
mail_SMTPPort = 465  
# 用户名，格式为「 *****@**.com」
mail_user = "******@163.com"
# 一般此处填登录密码；QQ 邮箱等特殊邮箱应填写「授权码」而非密码
mail_pass = "abcd12345" 
# 发件人邮箱，填在单引号内
sender = '******@163.com'
# 收件人邮箱，填在单引号内；不要删去两侧中括号（使用 list 形式填入）
# -- 单个接收邮箱：['*******@***.com']
# -- 多个接收邮箱：['******1@***.com', '******2@***.com', ...]
receivers = ['******@163.com']

####### 这一部分一般不需要修改，除非你需要自己定制 ####### 
# 邮件标题
title = '【' + time.strftime("%Y/%m/%d", time.localtime()) + '】' + '今日健康状况已成功申报！'
# 邮件内容
content = '今日健康状况已成功申报！申报时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n' + '⚠️ 请确保您的身体状况良好再使用该软件，做到如实申报自身身体状况。若身体出现异常，应立即停止使用该软件并及时于学校系统更改每日申报情况。因使用该软件误报身体状况而引发的不良后果应由您自行承担。' + '\n' + '本软件仅限于技术用途，切勿滥用！跟进本软件更新，详见 Github：https://github.com/Pinming/NWPU_COVID19_AutoReport'
####### 这一部分一般不需要修改，除非你需要自己定制 ####### 


########## ·以下内容请不要随意修改· ########## 
# Debug 开关，非调试用途不必打开
debug_switcher = 0

# 全局变量
url_Form = 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp' # 获取表格并进行操作
url_Submit = 'http://yqtb.nwpu.edu.cn/wx/ry/ry_util.jsp' # 用于 POST 申报的内容
url_for_id = 'https://uis.nwpu.edu.cn/cas/login' # 用于 Validate 登录状态
url_for_user_info = 'http://yqtb.nwpu.edu.cn/wx/ry/jbxx_v.jsp'  # 「个人信息」一栏
url_for_list = 'http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/rzxx_list.jsp'
email_status = 0
# Email 实现 
def sendEmail(email_status):
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
 
def send_email2(SMTP_host, from_account, from_passwd, to_account, subject, content):
    email_client = smtplib.SMTP(SMTP_host)
    email_client.login(from_account, from_passwd)
    # create msg
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = from_account
    msg['To'] = to_account
    email_client.sendmail(from_account, to_account, msg.as_string())
    email_client.quit()
# Email 实现结束

def getToken(url): # 动态获取 token 并传递 session
    session = requests.Session()
    res = session.get(url).text
    token = BeautifulSoup(res, 'html.parser').find(
        name='input',
        attrs={
            'name': 'lt'
        }
    ).get('value')
    return token, session

token, session = getToken(url_for_id)

def login(username=username,password=password):
    header = {
        'Referer': url_Form,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://uis.nwpu.edu.cn',
    }

    data = {
        'username': username,
        'password': password,
        'lt': token,
        '_eventId': 'submit',
    }

    r = session.post(url_for_id, data=data, headers=header, timeout=5)
    rt = r.text  # rt 以 html 形式返回登录状态
    
    if rt.find('登录成功') != -1:
        print('登录成功')
    else:
        if rt.find('密码错误') != -1:
            print('密码错误, 请检查「登录信息」一栏用户名及密码是否正确')
        else:
            print('【大概率已登陆成功】登录异常，请重新执行')
    # r2、r3 用于动态获取相关信息填入 Form // for POST
    # r2 操作
    r2 = session.post(url_Form).text
    # url 指向「今日填报」页面，但被跳转到主页 [//yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp]；r2 最终可以获取姓名和学院
    soup = BeautifulSoup(r2, 'html.parser')
    global RealCollege, RealName, PhoneNumber
    for k in soup.find('div', string=re.compile('姓名')):
        RealName = k.replace('姓名：', '')
    for l in soup.find('div', string=re.compile('学院')):
        RealCollege = l.replace('学院：', '')
    # r3 操作
    r3 = session.post(url_for_user_info).text # 在「基本信息」页面 / 此页面也可获得上述 k,l 信息，之前未发现
    soup2 = BeautifulSoup(r3, 'html.parser')
    m = soup2.find_all('span')
    PhoneNumber = m[6].string  # 提取出列表的 #6 值即为电话号码
    # r5 操作：获得上一次填报的所在地
    r5 = session.post(url_for_list).text
    soup3 = BeautifulSoup(r5, 'html.parser')
    v_loc = soup3.find("span", attrs={"class": "status"}).string
    global loc_name, loc_code_str
    loc_name = v_loc
    loc_code = location.GetLocation(loc_name)
    loc_code_str = loc_code[0]
    if loc_code_str == '':
        print('获取上一次填报的信息时出现错误！' + '\n' + '请联系作者（通过 Github Issue 或邮箱：i@pm-z.tech）并附上信息填报网站「个人中心→我的打卡」页面的截图，便于定位问题！')
        exit()


    
def submit(loc_code_str, loc_name, RealName, RealCollege, PhoneNumber):
    HeadersForm = {
        'Origin': 'http://yqtb.nwpu.edu.cn',
        'Referer': 'http://yqtb.nwpu.edu.cn/wx/ry/jrsb.jsp',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
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
        'sfyzz': '0', # 是否
        'sfqz': '0', # 是否确诊
        'ycqksm': '', 
        'glqk': '0',
        'glksrq': '',
        'gljsrq': '',
        'tbly': 'sso', # 填报来源：SSO 单点登录
        'glyy': '' ,
        'qtqksm': '',
        'sfjcqzsm': '',
        'sfjkqk': '0',
        'jkqksm': '',
        'sfmtbg': '',
        'qrlxzt': '',
        'xymc': RealCollege, # 学院名称；实践表明可留空
        'xssjhm': PhoneNumber, # 手机号码；实践表明可留空
    }
    if debug_switcher == 1:
        print(f'最终填报的表格内容：{tbDataForm}')
    session.post(url=url_Submit, data=tbDataForm, headers=HeadersForm)
    r4 = session.get(url_Form).text
    session.close()
    if (r4.find('重新提交将覆盖上一次的信息')) != -1:
        print('申报成功！')
        if email_switcher == 1:
            sendEmail(email_status)
            if email_status != -1:
                print('邮件已发送！')
            else:
                print('邮件发送失败！请检查 Email 的各项设置（用户名、密码、SMTP 服务器及端口）等设置是否正确！')
    else:
        print('申报失败，请重试！')

def execute(username, password):
    login(username, password)
    submit(loc_code_str, loc_name, RealName, RealCollege, PhoneNumber)

execute(username, password)