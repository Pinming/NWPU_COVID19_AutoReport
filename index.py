import user_config
from report import NWPU_Yqtb_Site

__version__ = [2, 1, 4, '220716-2049']


def handler(event, context):
    username = user_config.username
    password = user_config.password
    yqtb = NWPU_Yqtb_Site()
    yqtb.login(username, password)
    yqtb.init_info()
    yqtb.submit()


# 如需在本地使用或调试，请移除下列代码注释
# if __name__ == '__main__':
#     username = user_config.username
#     password = user_config.password
#     yqtb = NWPU_Yqtb_Site()
#     yqtb.login(username, password)
#     yqtb.init_info()
#     yqtb.submit()