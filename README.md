# NWPU_COVID19_AutoReport

当前版本 `v1.0.3` (200807-1519)

用于完成西工大每日健康申报的自动化程序。在进行自动填报的同时通过微信推送或 Email 提醒填报结果。    
本程序已经适配 2020/7/24 西工大翱翔门户升级，确认兼容。

想了解更多（或如果以下的图片加载不全），还可以阅读 https://www.pm-z.tech/2020/07/26/Auto_Reporter_For_COVID19

# ⚠️ 使用前请注意！
* 本软件设计之本意为技术学习，请在**遵循法律及学校各项规定**的前提下使用本软件。
* 如您需要使用该软件，请**确保您的身体状况良好**，**如实申报**自身身体状况。
* 若您的身体状况出现异常，应**立即停止**使用本软件、**关闭**云函数自动触发功能，并及时于学校系统更改每日申报情况。
* 因使用该软件误报身体状况而引发的不良后果**应由您自行承担**。
* 本软件原理是提取上一次的填报结果来提交，如果您的所在地发生改变，请**自行手动填报一次**，理论上程序会自动跟进后续的填报并与之同步。如出现异常烦请反馈！
* 该软件未必万能，请**时常检查填报结果**！

另：由于程序开发之初使用了国家现行最新的行政区划代码，故地理位置数据 `location.py` 可能与学校系统有部分出入，这有可能导致申报异常。如您在运行时发现提示：
```
获取上一次填报的信息时出现错误！可能是本程序地理位置数据库中的数据有误。
请联系作者（通过 Github Issue 或邮箱：i@pm-z.tech）并附上信息填报网站「个人中心→我的打卡」页面的截图，便于定位问题！
```
烦请带上所要申报的地理位置进行反馈，多谢！      
如发现这样的异常，程序会自动阻断申报过程，防止错误的数据被上传至学校。

# 基本配置方法
适用环境：Python 3.6 及以上版本。      
程序已经集成所有第三方库，不需要使用 pip 再次安装。

使该程序正确运行，需要编辑 `main.py` 中的部分变量，配置西工大翱翔门户账号、邮箱信息（可选）。其他文件无需改动。

`main.py` 需要设置的变量如下：

变量 | 说明
-- | --
`username` | 填入登录翱翔门户的用户名，通常为学工号
`password` | 填入对应用户的密码
`SC_switcher` |  ServerChan 微信推送服务开关，默认开启服务，赋值为 `1`；填 `0` 则关闭；<br>如果关闭了该服务则不需要配置 `SCKey`。
`SCKEY` |  ServerChan 微信推送服务对应的 Key，用于绑定自己的微信`。
`email_switcher` | Email 服务开关，默认开启服务，赋值为 `1`；填 `0` 则关闭。<br>如果关闭了 Email 服务则不需要配置以下变量。
`mail_host` | （可选）**发送方**的 SMTP 服务器，如果使用 163 邮箱则不必修改；其他邮箱请对应更改。
`mail_SMTPPort` | （可选）**发送方**的 SMTP 端口号，如果使用 163 邮箱则不必修改；其他邮箱请对应更改。
`mail_user` | （可选）发送方邮箱，格式为 `****@***.com`。
`mail_pass` | （可选）发送方邮箱对应的密码。
`receivers` | （可选）接收方邮箱；以 `列表 (list)` 形式存入。<br>如果留空，则默认发送至发件邮箱。

对于 `receivers` 参数，如果只有一个接收邮箱，按照以下形式填入:
```
['*******@***.com']
```

如果有多个接收邮箱，则按照以下形式填入：
```
['******1@***.com', '******2@***.com', '...']
```

# 云端部署方法
这里以阿里云函数计算为例。
1) 首先注册一个阿里云账号，然后在控制台中搜索并进入「函数计算」；
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/6.png)
2) 点击「立即创建函数」；
3) 选择「事件函数」；
4) 按照下图的设置配置函数。其中 `所在服务` 和 `服务函数` 可以任填；
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/7.png)
5) 出现弹窗，点击「同意授权」；
6) 找到新建的函数，选择「代码执行」→「代码包上传」，将你**已经配置好**的程序**打包为 zip**，然后上传。生成的压缩包文件结构应如图。上传后点击「保存」；
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/8.png)
7) 点击「保存并执行」，进行一次测试，观察输出的结果；
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/9.png)
8) 如果输出结果无问题，点击「触发器」→「创建触发器」，如图填入参数。`触发器名称`可任填，时间配置则在「时间间隔」中填入适当的时间间隔即可，然后点击「确定」；
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/10.png)

> 程序触发的时间点是：北京时间每日 0 时起的每个「时间间隔」后。

至此便可以实现定时间间隔的每日自动健康填报。

> 目前阿里云函数存在 bug，即每次函数执行可能重复。所以你可能会在同一时间收到两次邮件，这我暂时不知道怎么解决，可能是阿里云的锅吧。

收到的 Email 效果如下：
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/12.png)

如果需要关闭云端的自动填报，在「触发器」菜单中关闭即可。
![](https://oss.pm-z.tech/img/Auto_Reporter_For_COVID19/11.png)

> 在建立函数过程中，你可能会发现关于该功能的收费提示。<br>本函数的请求量、请求时间及耗费公网流量均极小，每天执行三四次水平的请求的花费根本，或者说近似是 0（考虑到公网流量，费用可能是 0 后小数点后两位以上的水平），请放心。<br>具体收费标准详见：https://help.aliyun.com/document_detail/54301.html

此外，你也可以通过 Windows 的「计划任务」或类似功能在本地计算机上定时执行该程序，方法不再赘述。    
设计初衷还是为了云函数考虑的，这样更方便一些，不需要本地计算机挂机运行。

期望全人类早日战胜 COVID-19，这个程序能早一天失去它的用武之地~
