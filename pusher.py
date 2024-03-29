import datetime
import requests
import pytz
import user_config
import __init__

########## 以下部分一般不需要修改，除非你需要自己定制发送邮件或微信推送的内容 ##########
# 获取公告 / 请勿删除，便于发送需要用户知悉的信息 
url_notice = 'https://oss.pm-z.tech/notice_for_autoreport.txt'
session_notice = requests.session()

url_for_sc = "https://sctapi.ftqq.com/" + user_config.SCKEY + ".send"


# ServerChan 推送
class Pusher(object):
    def sc_push_successful(site):
        notice = session_notice.get(url_notice)
        notice.encoding = "UTF-8"
        notice = notice.content.decode('UTF-8')
        # 邮件标题
        title = datetime.datetime.now(
            pytz.timezone('PRC')).strftime("%Y/%m/%d") + ' | ' + '今日健康状况已成功申报！'
        # 邮件内容
        content = f'''# 今日健康情况已申报
## 📚 申报内容

- 姓名：{site.name}
- 申报时间：{datetime.datetime.now(pytz.timezone("PRC")).strftime("%Y-%m-%d %H:%M:%S")}
- 当前位置：{site.szcsmc}

## ⚠ 注意事项

请确保您的身体状况良好再使用该软件，做到如实申报自身身体状况。

若身体出现异常，应立即停止使用该软件并及时于学校系统更改每日申报情况。

因使用该软件误报身体状况而引发的不良后果应由您自行承担。

## 📢 公告
本软件仅限于技术用途，切勿滥用！跟进本软件更新，详见 [Github](https://github.com/Pinming/NWPU_COVID19_AutoReport)。\n{notice}

当前脚本版本：`{__init__.__version__[0]}.{__init__.__version__[1]}.{__init__.__version__[2]}`
'''
        data_for_push = {
            "title": title,
            "desp": content,
            "channel": "9"
        }
        requests.post(url_for_sc, data=data_for_push)
        print('微信推送请求已发出 | 如果没有收到信息请检查 ServerChan 配置是否有误。')
    
    def sc_push_when_login_failed(self, error_text):
        data_for_push_failed = {
            "title":
                '今日疫情填报失败 | 翱翔门户登陆失败',
            "desp":
                f'''
❌ 登入翱翔门户过程失败！

出现该问题有两种可能原因：
- 您的翱翔门户用户名或密码填写有误；
- 学校对翱翔门户登陆系统做出了改动。

若原因为后者，请持续关注 https://github.com/Pinming/NWPU_COVID19_AutoReport ，等待软件更新再试。

脚本返回的错误信息：
```
{error_text}
```

当前脚本版本：`{__init__.__version__[0]}.{__init__.__version__[1]}.{__init__.__version__[2]}`
                '''
        }
        requests.post(url_for_sc, data=data_for_push_failed)
        print('登陆失败 | 错误提示已通过微信推送。')
    
    def sc_push_when_wrong_info(site, error_info):
        data_for_wrong_info = {
            "title":
                '今日疫情填报失败 | 初始化或上传填报信息时出现错误',
            "desp":
                '''
❌ 初始化或上传填报信息时出现错误！

出现该问题的可能原因：
- 学校对填报问卷的问题或对疫情填报系统后台做出了改动；
    该种情况，请持续关注 https://github.com/Pinming/NWPU_COVID19_AutoReport ，等待软件更新再试。
- 本软件获取您所填写的地理信息时出现了错误。
    该种情况，请联系作者（通过 Github Issue 或邮箱：i@pm-z.tech）并附上信息填报网站「个人中心→我的打卡」页面的截图，便于定位问题！
                ''' + '\n' + f'脚本返回的错误信息：\n```\n{error_info}\n```' + '\n' +
                f'填报的地理位置数据：{site.szcsbm}, {site.szcsmc}'
                f'当前脚本版本：`{__init__.__version__[0]}.{__init__.__version__[1]}.{__init__.__version__[2]}`'
        }
        requests.post(url_for_sc, data=data_for_wrong_info)
        print('初始化或上传填报信息时出现错误 | 错误提示已通过微信推送。')
    
    def sc_push_when_get_submit_page_error(site, error_info):
        data_for_get_submit_page_error = {
            "title":
                '今日疫情填报失败 | 获取信息填报页面时出现错误',
            "desp":
                '''
❌ 获取信息填报页面时出现错误！

出现该问题的可能原因：
- 学校对翱翔门户或疫情填报系统后台做出了改动；
    该种情况，请持续关注 https://github.com/Pinming/NWPU_COVID19_AutoReport ，等待软件更新再试。
''' + '\n' + f'脚本返回的错误信息：\n```\n{error_info}\n```' + '\n' +
                f'当前脚本版本：`{__init__.__version__[0]}.{__init__.__version__[1]}.{__init__.__version__[2]}`'
        }
        requests.post(url_for_sc, data=data_for_get_submit_page_error)
        print('初始化或上传填报信息时出现错误 | 错误提示已通过微信推送。')
