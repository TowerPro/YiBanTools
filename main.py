from __future__ import unicode_literals, print_function  # python2
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import requests
from bs4 import BeautifulSoup
import datetime
from urllib import parse
import json
import random
from urllib.parse import quote
import string
import time
import re
# 当前的session会话对象
session = requests.session()

# 登录操作

user_website = ""
user_id = ""
group_id = ""
puid = ""
channel_id = ""
actor_id = ""
nick = ""


def login(username, password):
    r = session.get("https://www.yiban.cn/login")
    soup = BeautifulSoup(r.text, "html.parser")
    ul = soup.find("ul", id="login-pr")
    # 从html当中获取私钥
    data_keys = ul['data-keys']
    # 从html当中获取时间
    data_keys_time = ul['data-keys-time']
    code = ""
    # 获取到验证码
    encrypt_password = get_crypt_password(data_keys, password)
    login_json = json.loads(login_request(
        username, encrypt_password, code, data_keys_time))
    # 获取到返回的json数据
    if(login_json['code'] == 200):
        start(login_json)
    else:
        if(login_json['code'] == '711'):
            code = wirte_code("/Users/hdy/Desktop/yanzhengma.jpg")
            login_json = json.loads(login_request(
                username, encrypt_password, code, data_keys_time))
            if(login_json['code'] == 200):
                start(login_json)
            else:
                print("错误码:"+login_json['code']+" 原因:"+login_json['message'])
        else:
            print("错误码:"+login_json['code']+" 原因:"+login_json['message'])
    # print(r.text)


def login_request(username, encrypt_password, code, data_keys_time):
    form_data = {
        'account': username,
        'password': encrypt_password,
        'captcha': code,
        'keysTime': data_keys_time
    }
    print(form_data)
    r = session.post("https://www.yiban.cn/login/doLoginAjax",
                     data=form_data, allow_redirects=False)
    return r.text

# 验证码保存


def wirte_code(saveUrl):
    r = session.get("https://www.yiban.cn/captcha/index?" +
                    (str(int(time.time()))))
    with open(saveUrl, 'wb') as f:
        f.write(r.content)
    code = input("请输入验证码")
    # code = quote(code, safe=string.printable)
    return code


def start(login_json):
    print("模拟登陆成功")
    print(login_json)
    user_website = login_json['data']['url']
    user_id = get_user_id()
    print("获取到的用户id为:"+user_id)

    global group_id
    global puid
    global channel_id
    global actor_id
    global nick

    info = getInfo()

    group_id = info['group_id']
    puid = info['puid']
    channel_id = info['channel_id']
    actor_id = info['actor_id']
    nick = info['nick']

    print(info)

    qiandao()
    # 循环四次.
    for i in range(4):
        addFeed()
        addTopic()
        addPersonWebsite()
        addblog()
        addYiMiaoMiao()
        add_vote()
        print("执行一轮完成.等待下一轮执行")
        time.sleep(5)


def get_user_id():
    r = session.get("http://www.yiban.cn/my/feed")
    soup = BeautifulSoup(r.text, "html.parser")
    span = soup.find_all("span", class_="user-account")[0]
    return str(span)[str(span).index("user_id/")+8:str(span).index("user_id/")+16]


# 获取通过加密的密码
def get_crypt_password(private_key, password):
    rsa = RSA.importKey(private_key)
    cipher = PKCS1_v1_5.new(rsa)
    ciphertext = encrypt(password, cipher)
    return ciphertext


def encrypt(msg, cipher):
    ciphertext = cipher.encrypt(msg.encode('utf8'))
    return base64.b64encode(ciphertext).decode('ascii')


def qiandao():
    form_data = {
        "optionid[]": 12182,
        "input": ""
    }
    r = session.post("http://www.yiban.cn/ajax/checkin/answer", data=form_data)
    result_json = json.loads(r.text)
    print(result_json["message"])

# 发布动态(完成)


def addFeed():
    randomstr = str(random.randint(100, 99999))
    form_data = {
        "content": randomstr,
        "privacy": "0",
        "dom": ".js-submit"
    }
    # 自动发表动态
    r = session.post("http://www.yiban.cn/feed/add", data=form_data)
    print(r.text)
    post_json = json.loads(r.text)
    if(post_json['code'] == 200):
        feedId = str(post_json['data']['feedId'])
        print("获取到的动态id为:"+feedId)
        # 自动点赞
        session.post("http://www.yiban.cn/feed/up", data={"id": feedId})
        # 自动同情
        session.post("http://www.yiban.cn/feed/down", data={"id": feedId})
        # 自动发表评论
        comment_random = str(random.randint(100, 99999))
        session.post("http://www.yiban.cn/feed/createComment",
                     data={"id": feedId, "content": comment_random})
        print("动态相关的网薪完成.")
    else:
        print("动态发表错误....")

# 博文添加


def addblog():
    r = session.get("http://www.yiban.cn"+user_website)
    randomstr = str(random.randint(100, 99999))
    r = session.post("http://www.yiban.cn/blog/blog/addblog", data={"title": randomstr, "content": randomstr,
                                                                    "ranges": "1", "type": "1", "token": "64d41ba3222a4c4614fc33f594a6df4d", "ymm": "1", "dom": ".js-submit"})
    post_result = json.loads(r.text)
    if(post_result['code'] == 200):
        global user_id
        r = session.get(
            "http://www.yiban.cn/blog/blog/getBlogList?page=1&size=10&uid="+user_id)
        m_json = json.loads(r.text)
        print(m_json)
        if(m_json['code'] == 200):
            try:
                if(m_json["data"]["count"] == 0):
                    # 判断数量是否为空
                    return

                m_json = m_json["data"]["list"][0]
                blog_id = m_json['id']
                Mount_id = m_json['Mount_id']
                # 博文点赞
                session.get("http://www.yiban.cn/blog/blog/addlike/uid/" +
                            user_id+"/blogid/"+blog_id)
                # 评论博文
                # blogid: 12300216 oid: 18884862 mid: 48893712 reply_user_id: 0 reply_comment_id: 0 content: 123123123
                session.post("http://www.yiban.cn/blog/blog/addcomment/", data={
                    "blogid": blog_id, "oid": user_id, "mid": Mount_id, "reply_user_id": "0", "reply_comment_id": "0", "content": randomstr})
                print("博文发表成功")
            except Exception:
                print("博文发表异常")
        else:
            print("获取请求的博文错误...")

        # print("获得blogid:"+blogid)
    else:
        # 需要注意如果请求评论的速度过快会导致弹出验证码.
        print("发表博文失败")

# 添加易喵喵


def addYiMiaoMiao():
    randomstr = str(random.randint(100, 99999))
    data_form = {"title": randomstr,
                 "content": randomstr, "kind": '8', "agree": 'true'}
    r = session.post("http://ymm.yiban.cn/article/index/add", json=data_form)
    print(r.text)


# 网站\客户端查看(个人/公共/机构账号)主页
def addPersonWebsite():
    # 查看个人
    session.get("http://www.yiban.cn/user/index/index/user_id/"+user_id)
    # 查看机构
    session.get("http://www.yiban.cn/school/index/id/5000090")
    # 查看公共
    session.get("http://www.yiban.cn/user/index/index/user_id/15977811")
    print("网站\客户端查看(个人/公共/机构账号)主页完成")

# 添加话题


def addTopic():
    randomstr = str(random.randint(100, 99999))
    payload = {
        'puid': puid,
        'pubArea': group_id,
        'title': randomstr,
        'content': randomstr,
        'isNotice': 'false',
        'dom': '.js-submit'
    }

    Add_Topic = session.post(
        'https://www.yiban.cn/forum/article/addAjax', data=payload, timeout=10)
    return Add_Topic.json()['message']


'''
获取群组信息
返回 JSON 字典
'''


def getInfo():

    Get_Group_Info = session.get(
        'https://www.yiban.cn/my/group/type/public', timeout=10)
    group_id = re.search(
        r'href="/newgroup/indexPub/group_id/(\d+)/puid/(\d+)"', Get_Group_Info.text).group(1)
    puid = re.search(
        r'href="/newgroup/indexPub/group_id/(\d+)/puid/(\d+)"', Get_Group_Info.text).group(2)

    payload = {
        'puid': puid,
        'group_id': group_id
    }

    Get_Channel_Info = session.post(
        'https://www.yiban.cn/forum/api/getListAjax', data=payload, timeout=10)
    channel_id = Get_Channel_Info.json()['data']['channel_id']

    Get_User_Info = session.post(
        'https://www.yiban.cn/ajax/my/getLogin', timeout=10)
    actor_id = Get_User_Info.json()['data']['user']['id']
    nick = Get_User_Info.json()['data']['user']['nick']

    info = {
        'group_id': group_id,
        'puid': puid,
        'channel_id': channel_id,
        'actor_id': actor_id,
        'nick': nick
    }

    return info


def add_vote():
    randomstr = str(random.randint(100, 99999))
    payload = {
        'puid': puid,
        'group_id': group_id,
        'scope_ids': group_id,
        'title': randomstr,
        'subjectTxt': randomstr,
        'subjectPic': None,
        'options_num': 2,
        'scopeMin': 1,
        'scopeMax': 1,
        'minimum': 1,
        'voteValue': time.strftime("%Y-%m-%d %H:%M", time.localtime(1893427200)),
        'voteKey': 2,
        'public_type': 0,
        'isAnonymous': 0,
        "voteIsCaptcha": 0,
        'istop': 1,
        'sysnotice': 2,
        'isshare': 1,
        'subjectTxt_1': randomstr,
        'subjectTxt_2': randomstr,
        'rsa': 1,
        'dom': '.js-submit'
    }

    session.post('https://www.yiban.cn/vote/vote/add',
                 data=payload, timeout=10)
    print("添加投票已经完成")


# try:
login('13216151732', 'h378759617')
# except Exception:
#     print("程序异常,登录失败.")
# addblog()
# str = """{"code":200,"message":"\u64cd\u4f5c\u6210\u529f","data":{"url":"\/user\/index\/index\/user_id\/18884862"}}"""
# m = json.loads(str)x
# print(m['code'])72c737918b586744d88347de2a58ee75
