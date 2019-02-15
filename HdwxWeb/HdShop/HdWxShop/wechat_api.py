from django.core.cache import cache

import requests
import urllib.parse

#  微信API父类
class wechatapi_base(object):

    API_PREFIX = u'https://sz.api.weixin.qq.com/cgi-bin/'

    def __init__(self,appid,appsecret):
        self.appid = appid
        self.appsecret = appsecret
        self._access_token = None

    @property
    def get_access_token(self):
        """
        获取公众号access_token
        :return:
        """
        params = {'grant_type': 'client_credential', 'appid': self.appid, 'secret': self.appsecret}
        if not self._access_token:
            pass
        return self._access_token


    # 返回用户授权url
    def auth_url(self, redirect_uri, scope='snsapi_userinfo', state=None):
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' % \
              (self.appid, urllib.parse.quote(redirect_uri), scope, state if state else '')
        return url


    # 根据用户code去获取access_token
    def get_auth_access_token(self, code):
        """
        :param code:  用户授权后返回的code
        :return:
          {
            "access_token":"ACCESS_TOKEN",
            "expires_in":7200,
            "refresh_token":"REFRESH_TOKEN",
            "openid":"OPENID",
            "scope":"SCOPE"
            }
        """
        url = u'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': self.appid,
            'secret': self.appsecret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        return requests.get(url, params=params)


    # 获取用户信息
    def get_user_info(self, auth_access_token, openid):
        """
        :param auth_access_token:
        :param openid:
        :return:
        {
            "openid":" OPENID",
            "nickname": NICKNAME,
            "sex":"1",
            "province":"PROVINCE"
            "city":"CITY",
            "country":"COUNTRY",
            "headimgurl": "http://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46",
            "privilege":[ "PRIVILEGE1" "PRIVILEGE2"     ],
            "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        }
        """
        url = u'https://api.weixin.qq.com/sns/userinfo?'
        params = {
            'access_token': auth_access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        return requests.get(url, params=params)

