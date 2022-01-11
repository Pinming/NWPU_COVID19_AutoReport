import user_config
from report import NWPU_Yqtb_Site

def handler(event, context):
    username = user_config.username
    password = user_config.password
    yqtb = NWPU_Yqtb_Site()
    yqtb.login(username, password)
    yqtb.init_info()
    yqtb.submit()
    
# if __name__ == '__main__':
#     handler()