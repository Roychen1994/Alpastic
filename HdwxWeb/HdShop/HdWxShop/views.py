from django.shortcuts import render,redirect,render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.utils import timezone
from django.db.models import Count,Sum,Max
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.generic import View

from . import models, myforms, checkcode, outputexcel, wechat_api, mobileesp, cwhAlgorithm
from .dysms_python import demo_sms_send

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from django_redis import get_redis_connection
from django.core.cache import cache

import json
import re
import os
import datetime
import random
import uuid
from io import BytesIO
from PIL import Image

# 超级管理员用户名
static_superadmin_username = "superadmin"
# 短信验证模板CODE
ali_checkcode_templetcode = "SMS_139980402"
# 阿里云签名
ali_sign_name = "陈文灏"


# Create your views here.
def index(request):
    ismobile = is_mobilerequest(request)
    classes = models.commodityclass.objects.all()
    advinfo_table = models.advinfo.objects.all()
    news_table = models.newsinfo.objects.all().order_by('NewsCreatetime')[0:4]
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
    if ismobile:
        return render(request, 'mobileindex.html', {
            "classes": classes, "advinfo_table": advinfo_table, "news_table": news_table,
            "login_username": login_username
        })
    else:
        return render(request,'index2.html',{
        "classes":classes,"advinfo_table":advinfo_table,"news_table":news_table,"login_username":login_username
        })


def news(request,newsid):
    shownews_template = get_template('shownews.html')
    newscls_table = models.newsclass.objects.all()
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
    try:
        newsinfo_table = models.newsinfo.objects.get(id = newsid)
    except:
        newsinfo_table = {}
        newsinfo_table['Newstitle'] = '未找到该新闻'

    hot_list = []
    CeiBuyNUm_hot_datas = models.commodityendinfo.objects.order_by('CeiBuyNUm')[0:4]
    for CeiBuyNUm_hot_data in CeiBuyNUm_hot_datas:
        product_host_data = CeiBuyNUm_hot_data.Commid
        ths_detail = models.commditydetail.objects.filter(Commid=product_host_data.id)[0]
        hot_list.append({'info': product_host_data, 'detail': ths_detail})

    news_html = shownews_template.render(locals())

    return HttpResponse(news_html)


def mainnews(request,newsclsid):
    # show_many: 每页显示的数量
    show_many = 2
    news_template = get_template('news.html')
    newscls_table = models.newsclass.objects.all()
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
    try:
        newslist_table = models.newsinfo.objects.filter(Newsclassid = int(newsclsid))
        newslist_table_count = models.newsinfo.objects.filter(Newsclassid = int(newsclsid)).count()
    except:
        newslist_table = models.newsinfo.objects.all()
        newslist_table_count = models.newsinfo.objects.count()
    try:
        page = int(request.GET.get('page'))
    except:
        page = 1

#   分页传输, 内容newslist_table, 最大页数 max_page
    max_page = int(newslist_table_count / show_many)
    if newslist_table_count % show_many != 0:
        max_page += 1

    if page == 1:
        if show_many < newslist_table_count:
            newslist_table = newslist_table[:show_many]
    elif page >= max_page :
        newslist_table = newslist_table[(max_page - 1) * show_many:]
    else:
        newslist_table = newslist_table[(page - 1)* show_many:page * show_many]
#   <!----  分页  ---->
#    paginator = Paginator(newslist_table, 5)
#    page = request.GET.get('page')
#    try:
#        news_contacts = paginator.page(page)
#    except:
#        news_contacts = paginator.page(1)
#   page_no: 所有页码的列表  page_next:下一页页码  next_previous:上一个页码
    page_no = [pgn + 1 for pgn in range(max_page)]
    if page >= max_page:
        page_next = max_page
    else:
        page_next = page + 1

    if page <= 1:
        page_previous = 1
    else:
        page_previous = page - 1

    hot_list = []
    CeiBuyNUm_hot_datas = models.commodityendinfo.objects.order_by('CeiBuyNUm')[0:4]
    for CeiBuyNUm_hot_data in CeiBuyNUm_hot_datas:
        product_host_data = CeiBuyNUm_hot_data.Commid
        ths_detail = models.commditydetail.objects.filter(Commid=product_host_data.id)[0]
        hot_list.append({'info': product_host_data, 'detail': ths_detail})


    mainnews_html = news_template.render(locals())
    return HttpResponse(mainnews_html)


def Registeruser(request):
    classes = models.commodityclass.objects.all()
    errors = checkcode_error = False
    registeruser_forms = myforms.Registeruser()
    if request.method == 'GET':
        # registeruser_templet = get_template('Register.html')
        # registeruser_html = registeruser_templet.render(locals())
        return render(request,'Register.html',locals())

    if request.method == 'POST':
        registeruser_forms_data = myforms.Registeruser(request.POST)
        request_check_code = request.POST.get('check_code')
        session_check_code = request.session['check_code']
        print(registeruser_forms_data)

        # 校正验证码
        if request_check_code.upper() != session_check_code.upper():
            checkcode_error = "验证码错误,请您重新输入"
            return render(request,'Register.html',locals())

        if registeruser_forms_data.is_valid():
            data = registeruser_forms_data.cleaned_data
            data_username = data.get('username').strip()
            data_password = data.get('password')
            data_password2 = data.get('password_again')

            if data_password != data_password2:
                checkcode_error = "输入的两次密码不一致,请您重新输入"
                return render(request,'Register.html',locals())

            users = User.objects.filter(username = data_username).count()

            if users > 0:
                checkcode_error = "用户名已存在,请您重新输入"
                return render(request, 'Register.html', locals())

            # 把新用户数据插入到对应表
            try:
                User.objects.create_user(username = data_username,password = data_password).save
                ths_userid = User.objects.get(username = data_username)
                models.webuser.objects.create(userid = ths_userid,Username = data_username)
                custom = models.userrole.objects.get(Rolename = '客户')
                ths_webuserid = models.webuser.objects.get(userid = ths_userid)
                models.userbind.objects.create(userid=ths_webuserid,Userphone="",Userwx="",UserAddress="")
                models.userrule.objects.create(Userid = ths_webuserid,Roleid = custom,ReleaseAdv = custom.ReleaseAdv,
                                               ReleaseNew = custom.ReleaseNew,ReleaseInfo = custom.ReleaseInfo,AddCommodity = custom.AddCommodity,
                                               ModCommodity = custom.ModCommodity,AddOrder = custom.AddOrder, ModOrder = custom.ModOrder, ModOrderPrice = custom.ModOrderPrice,
                                               AppOrder = custom.AppOrder, AckOrder = custom.AckOrder,PaidOrder = custom.PaidOrder,ShipOrder = custom.ShipOrder,RecOrder = custom.RecOrder,
                                               TranInfo = custom.TranInfo, SalePer = custom.SalePer,ProSummary = custom.ProSummary, ModRule = custom.ModRule,
                                               setcustprice = custom.setcustprice)
            except Exception as e:
                checkcode_error = "注册失败,可能是网站内部问题"
                return render(request, 'Register.html', locals())
            return redirect('/')
        else:
            errors = registeruser_forms_data.errors
            print(errors)
            registeruser_forms = myforms.Registeruser()
            return render(request,'Register.html',locals())


# ajax确认用户名是否已存在
def check_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        re_username = r'^[A-Za-z0-9]{6,12}'
        checkusername = re.match(username,re_username)
        if checkusername:
            return JsonResponse({'code':99})
        users = User.objects.filter(username = username).count()
        if users > 0:
            return JsonResponse({'code':98})
        else:
            return JsonResponse({'code':1})



def login(request):
    classes = models.commodityclass.objects.all()
    errors = checkcode_error = False
    login_forms = myforms.weblogin()
    wechat_api_base = wechat_api.wechatapi_base(
        appid = settings.WETCHAT_APPID,
        appsecret = settings.WETCHAT_APPSECRET
     )
    wechatlogin_url = wechat_api_base.auth_url(redirect_uri="/login/wechatredirect_uri/")

    if request.method == 'GET':
        return render(request,'login.html',locals())

    if request.method == 'POST':
        login_forms_data = myforms.weblogin(request.POST)
        if login_forms_data.is_valid():
            data = login_forms_data.cleaned_data
            data_username = data.get('username').strip()
            data_password = data.get('password')
            login_user = authenticate(username = data_username,password = data_password)
            if login_user is not None:
                if login_user.is_active:
                    ths_webuserstatus = models.webuser.objects.get(userid=User.objects.get(username = data_username)).Userstatus
                    if ths_webuserstatus == 1:
                        data_rememberme = str2bool(data.get('remember_me'))
                        if not data_rememberme:
                            request.session.set_expiry(0)
                        # 查询跟用户有关的信息
                        auth.login(request, login_user)
                        login_username = request.user.username
                        webuser_query = outputwebuser(request)
                        ths_rolequery = models.userrule.objects.get(Userid=webuser_query.id)
                        ths_rolename = ths_rolequery.Roleid.Rolename
                        # 写入session中
                        # rolename : 职位名称
                        # request.session['rolename'] = ths_rolename
                        next_url = request.GET.get('next')
                        if next_url:
                            return HttpResponseRedirect(next_url)
                        else:
                            return HttpResponseRedirect('/index/')
                    elif ths_webuserstatus == 2 :
                        checkcode_error = '登录失败,该账户已被冻结'
                    else:
                        checkcode_error = '登录失败,该账户状态异常'
                else:
                    checkcode_error = '登录失败,该账户未启用'
            else:
                checkcode_error = '登录失败,用户名或密码错误'
        else:
            checkcode_error = '登录失败,输入数据不合法'
    return render(request,'login.html',locals())


def logout(request):
    request.session.delete("rolename")
    auth.logout(request)
    return HttpResponseRedirect('/index/')


class wechatviewbase(View):
    wechat_api_base = wechat_api.wechatapi_base(
        appid = settings.WETCHAT_APPID,
        appsecret = settings.WETCHAT_APPSECRET
    )


class wechatlogin(wechatviewbase):
    def get(self,request):
        redir_url = request.GET.get('path')
        code = request.GET.get('code')

        if redir_url and code:
            try:
                # 获取用户access_token 和 openid
                access_token_json = self.wechat_api_base.get_auth_access_token(code)
                print("access_token: %s"%access_token_json)
                user_access_token = access_token_json['access_token']
                user_openid = access_token_json['openid']
                # 判断openid是否存在
                wehchat_openid = models.userwechat.objects.filter(openid=user_openid)
                # 如果存在,直接登录
                if wehchat_openid:
                    auth.login(request=request,user=wehchat_openid[0].userid.userid,backend='django.contrib.auth.backends.ModelBackend')
                    return HttpResponseRedirect('/index/')
                # 获取用户信息
                userinfo_json = self.wechat_api_base.get_user_info(auth_access_token=user_access_token,openid=user_openid)
                print("userinfo: %s"%userinfo_json)
                user_nickname = userinfo_json['nickname']
                user_sex = userinfo_json['sex']
                user_province = userinfo_json['province']
                user_city = userinfo_json['city']
                user_country = userinfo_json['country']
                user_privilege = userinfo_json['privilege']
                user_unionid = userinfo_json['unionid']
            except:
                messagetitle = "登录失败"
                messageinfo = "对不起！请稍候再试或联系管理员."
                buttonurl = ""
                return render(request, 'oauthlogin_result.html', locals())

                # 创建用户
                User.objects.create_user(username="wxid_" + str(user_openid), password=uuid.uuid1()).save
                this_userid = User.objects.get(username="wxid_" + str(user_openid))
                models.webuser.objects.create(userid=ths_userid, Username=data_username)
                custom = models.userrole.objects.get(Rolename='客户')
                ths_webuserid = models.webuser.objects.get(userid=ths_userid)
                models.userbind.objects.create(userid=ths_webuserid, Userphone="", Userwx="", UserAddress="")
                models.userrule.objects.create(Userid=ths_webuserid, Roleid=custom, ReleaseAdv=custom.ReleaseAdv,
                                                ReleaseNew=custom.ReleaseNew, ReleaseInfo=custom.ReleaseInfo,
                                                AddCommodity=custom.AddCommodity,
                                                ModCommodity=custom.ModCommodity, AddOrder=custom.AddOrder,
                                                ModOrder=custom.ModOrder, ModOrderPrice=custom.ModOrderPrice,
                                                AppOrder=custom.AppOrder, AckOrder=custom.AckOrder,
                                                PaidOrder=custom.PaidOrder, ShipOrder=custom.ShipOrder,
                                                RecOrder=custom.RecOrder,
                                                TranInfo=custom.TranInfo, SalePer=custom.SalePer,
                                                ProSummary=custom.ProSummary, ModRule=custom.ModRule,
                                                setcustprice=custom.setcustprice)
                models.userwechat.objects.create(userid=ths_webuserid,openid=user_openid,unionid=user_unionid,
                                                 nickname=user_nickname,sex=int(user_sex),privilege="",
                                                 province=user_province,city=user_city,country=user_country
                                                 )
                auth.login(request=request, user=wehchat_openid[0].userid.userid,
                           backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect('/index/')

# 重置密码
def resetpassword(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    message = ""

    if request.method == "GET":
        return render(request,'findmyuser.html',locals())

    if request.method == "POST":
        session_key = "resetpassword##" + str(request.session.session_key)
        post_username = request.POST.get('username')
        post_phonenumber = request.POST.get('phonenumber')
        post_checkcode = request.POST.get('checkcode')

        if cache.has_key(session_key):
            session_value = cache.get(session_key)
            session_code = session_value['code']
            if session_code == post_checkcode:
                session_value['check'] = 1
                cache.set(session_key,session_value,60)
                return HttpResponseRedirect('/resetpassword/reset/')
            else:
                message = "验证码错误"
                return render(request, 'findmyuser.html', locals())
        # redis中找不到 resetpassword 的 session key
        else:
            message = "请先获取验证码"
            return render(request,'findmyuser.html',locals())



# 填写用户重置的密码
def resetpassword_commit(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    message = ""

    session_key = "resetpassword##" + str(request.session.session_key)
    if cache.has_key(session_key):
        session_value = cache.get(session_key)
        check = session_value['check']
        username = session_value['username']
        if check == 1:
            if request.method == "GET":
                return render(request,'findmyuser_commit.html',
                              {"classes":classes,"login_username":login_username,
                               "username":username,"message":message,
                               }
                            )

            if request.method == "POST":
                password1 = request.POST.get('newpassword1')
                password2 = request.POST.get('newpassword2')

                if password1 == password2:
                    userquery = User.objects.get(username=username)
                    userquery.password = make_password(password1)
                    return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'success', 'message': '密码重置成功'})

                # 密码两次输入的不一样
                else:
                    message = "两次密码输入不一致"
                return render(request, 'findmyuser_commit.html',
                              {"classes": classes, "login_username": login_username,
                               "message": message,
                               }
                              )
        # 验证码还没验证过
        else:
            return HttpResponseRedirect('/resetpassword/')
    # redis can't find the session_key
    else:
        return HttpResponseRedirect('/resetpassword/')



# 修改后的商城后台
def shopv2(request):
    set_showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    ismobile = is_mobilerequest(request)
    nocache = 1

    # Get 参数
    get_search = request.GET.get('search')

    # 高级搜索选项
    size_options = models.commditydetail.objects.values('CodSize').distinct()
    thick_options = models.commditydetail.objects.values('Codthick').distinct()
    protlevel_options = models.commditydetail.objects.values('Cod_Protlevel').distinct()
    brand_options = models.commditydetail.objects.values('Codbrand').distinct()
    function_options = models.commditydetail.objects.values('Codfunction').distinct()

    if request.user.is_authenticated():
        login_username = request.user.username
        webuserquery = outputwebuser(request)
        # 查找用户已收藏id
        # usercollect_list 登录用户已收藏detail id 列表
        thsuser_collects = models.custcollect.objects.filter(CcUserid = webuserquery)
        usercollect_list = [ collectquery.CcCommid.id for collectquery in thsuser_collects ]

    if ismobile:
        return render(request, 'mobileshop.html', locals())
    else:
        return render(request, 'shop.html', locals())


# 查看客户商店信息缓存
def getshopcache(request):
    session_key = "shopinfo#" + str(request.session.session_key)
    if cache.has_key(session_key):
        # take value in redis
        session_value = str(cache.get(session_key))
        print("get: %s"%session_value)
        # 提取参数
        re_page = re.search(re.compile(r"(?<=&page=).*?(?=&)"), session_value)
        page = re_page.group() if re_page else ""
        re_pcls = re.search(re.compile(r"(?<=&pcls=).*?(?=&)"), session_value)
        pcls = re_pcls.group() if re_pcls else ""
        if pcls != '':
            pcls = int(pcls)
        re_psize = re.search(re.compile(r"(?<=&psize=).*?(?=&)"), session_value)
        psize = re_psize.group() if re_psize else ""
        re_thick = re.search(re.compile(r"(?<=&thick=).*?(?=&)"), session_value)
        thick = re_thick.group() if re_thick else ""
        re_protlevel = re.search(re.compile(r"(?<=&protlevel=).*?(?=&)"), session_value)
        protlevel = re_protlevel.group() if re_protlevel else ""
        re_brand = re.search(re.compile(r"(?<=&brand=).*?(?=&)"), session_value)
        brand = re_brand.group() if re_brand else ""
        re_function_value = re.search(re.compile(r"(?<=&function_value=).*?(?=&)"), session_value)
        function_value = re_function_value.group() if re_function_value else ""
        re_get_search = re.search(re.compile(r"(?<=&search=).*?(?=&)"), session_value)
        get_search = re_get_search.group() if re_get_search else ""
        re_get_orderby = re.search(re.compile(r"(?<=&orderby=).*?(?=&)"), session_value)
        orderby = re_get_orderby.group() if re_get_orderby else ""
        re_get_orderasc = re.search(re.compile(r"(?<=&orderasc=).*?(?=&)"), session_value)
        orderasc = re_get_orderasc.group() if re_get_orderasc else ""

        print('get orderasc:%s'%orderasc)
        return JsonResponse({
            'code':1,
            'ipage':page,
            'pcls':pcls,
            'psize':psize,
            'thick':thick,
            'protlevel':protlevel,
            'brand':brand,
            'function_value':function_value,
            'get_search':get_search,
            'orderby':orderby,
            'orderasc':orderasc
        })
    else:
        return JsonResponse({'code':0})


def hdshop(request):
    set_showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    usercollect_list = []
    userprice_dit = {}
    # 判断是否登录,如果登录查询客户信息
    if request.user.is_authenticated():
        login_username = request.user.username
        webuserquery = outputwebuser(request)
        # 查找用户已收藏id
        # usercollect_list 登录用户已收藏detail id 列表
        thsuser_collects = models.custcollect.objects.filter(CcUserid = webuserquery)
        usercollect_list = [ collectquery.CcCommid.id for collectquery in thsuser_collects ]
        # 客户单价
        # userprice_dit { 规格id:单价 }
        userprice = models.custcommprice.objects.filter(Cpuserid = webuserquery)
        for each_userprice in userprice:
            userprice_dit[each_userprice.Cpcommid.id] = each_userprice.CpunPrice

    if request.method == 'GET':
        try:
            page = int(request.GET.get('page'))
        except:
            page = 1

        try:
            search_value = request.GET.get('search')
            if search_value == 'None':
                search_value = ""
        except:
            search_value = ""
        try:
            commditycls = int(request.GET.get('cls'))
            this_cls = commditycls
        except:
            commditycls = ""
            this_cls = None

        shop_Pagination_value = shop_Pagination(page = page,commditycls = commditycls,search_value = search_value)
        if shop_Pagination_value:
            commodity_list, page_list, max_page, page_next, page_previous  = shop_Pagination_value
            if shop_Pagination_value:
                commodity_list, page_list, max_page, page_next, page_previous = shop_Pagination_value
                for ths_commdity in commodity_list:
                    if ths_commdity['detail'].id in userprice_dit.keys():
                        ths_commdity['detail'].CodunPrice = userprice_dit[ths_commdity['detail'].id]
            return render(request, 'shop.html', locals())
            # commodity_rdit[commcls] = models.commditydetail.objects.all\
            #     (Commid = models.commodityinfo.objects.all(Commclass = commcls.id))

    # if request.method == 'POST':
    #     try:
    #         search_value = str(request.POST.get('search'))
    #     except:
    #         return render(request, 'shop.html', locals())
    #     shop_Pagination_value = shop_Pagination(page = 1,search_value = search_value)
    #     commodity_rdit, page_list, max_page, page_next, page_previous = shop_Pagination_value
    #     return render(request, 'shop.html', locals())

    return render(request,'shop.html',locals())


# 商城用的分页功能
def shop_Pagination(page,commditycls = "",search_value = ""):
    set_showmany = 5
    commditydetail_count = 0
    commodity_rdit = {}

    if commditycls:
        cls_queryset = models.commodityclass.objects.filter(id = commditycls)
    else:
        cls_queryset = models.commodityclass.objects.all()

    if search_value:
        info_querysest = models.commodityinfo.objects.filter(CommName__icontains = search_value,Commclass_id__in = cls_queryset)
    else:
        info_querysest = models.commodityinfo.objects.filter(Commclass_id__in = cls_queryset)

    detail_queryset = models.commditydetail.objects.filter(Commid_id__in = info_querysest)

    commditydetail_count = detail_queryset.count()

    # --------------   弃用该查询方式 原因:存在BUG + 速度慢 ------------
    # # 搜索需要输出的商品信息名
    # if commditycls:
    #     classes = models.commodityclass.objects.filter(id = commditycls)
    #     queryset_commdityinfos = models.commodityinfo.objects.filter(Commclass = commditycls)
    #     for queryset_commdityinfo in queryset_commdityinfos:
    #         commditydetail_count += models.commditydetail.objects.filter(
    #             Commid = queryset_commdityinfo).count()

    # elif search_value:
    #     classes = models.commodityclass.objects.all()
    #     queryset_commdityinfos = models.commodityinfo.objects.filter(CommName__icontains = search_value)
    #     for queryset_commdityinfo in queryset_commdityinfos:
    #         commditydetail_count += models.commditydetail.objects.filter(
    #             Commid = queryset_commdityinfo).count()

    # else:
    #     classes = models.commodityclass.objects.all()
    #     commditydetail_count = models.commditydetail.objects.all().count()

    max_page = int(commditydetail_count / set_showmany) + 1
    if page <= 1:
        page_previous = 1
        page_next = page + 1
        commditydetail_frist_no = 0
        commditydetail_last_no = set_showmany
    elif page >= max_page:
        page_previous = page - 1
        page_next = max_page
        commditydetail_frist_no = (max_page - 1) * set_showmany
        commditydetail_last_no = commditydetail_count
    else:
        page_previous = page - 1
        page_next = page + 1
        commditydetail_frist_no = (page - 1) * set_showmany
        commditydetail_last_no = (page * set_showmany) - 1
    # 统计共输出多少个元素
    page_list = [ x + 1 for x in range(max_page) ]
    commditydetail_num = 0
    commodity_list = []

    for adetail in detail_queryset[commditydetail_frist_no:commditydetail_last_no]:
        ths_info = models.commodityinfo.objects.get(id = adetail.Commid_id)
        ths_cls = ths_info.Commclass
        commodity_list.append({'detail':adetail,'info':ths_info,'cls':ths_cls})

    # --------------   弃用该查询方式 原因:存在BUG + 速度慢 ------------
    # for commcls in classes:
    #     commodity_rdit[commcls.CclassName] = {}
    #     # 无搜索
    #     if not search_value:
    #         commcls_infos = models.commodityinfo.objects.filter(Commclass = commcls.id)
    #     # 有搜索
    #     else:
    #         commcls_infos = models.commodityinfo.objects.filter(Commclass = commcls.id,CommName__icontains = search_value)
    #     print(commcls_infos)
    #     for clsinfo in commcls_infos:
    #         commditydetail_this_count = models.commditydetail.objects.filter(Commid=clsinfo.id).count()
    #         # commditydetail_this_count = models.commditydetail.objects.filter(Commid=clsinfo.id,CommName__contains=search_value).count()
    #         commditydetail_num += commditydetail_this_count
    #         if commditydetail_num < commditydetail_frist_no: continue
    #         if commditydetail_num < commditydetail_last_no:
    #             commodity_rdit[commcls.CclassName][clsinfo.CommName] = models.commditydetail.objects.filter(
    #                 Commid=clsinfo.id)
    #         else:
    #             commodity_rdit[commcls.CclassName][clsinfo.CommName] = models.commditydetail.objects.filter(
    #                 Commid=clsinfo.id)[:commditydetail_num - commditydetail_last_no]

    print(max_page)
    return commodity_list,page_list,max_page,page_next,page_previous


def show_product(request,product_id):
    classes = models.commodityclass.objects.all()
    login_username = False
    usercollect_list = []
    cust_price = None
    if request.user.is_authenticated():
        login_username = request.user.username
        webuserquery = outputwebuser(request)
        # 查找用户已收藏id
        # usercollect_list 登录用户已收藏detail id 列表
        thsuser_collects = models.custcollect.objects.filter(CcUserid = webuserquery)
        usercollect_list = [ collectquery.CcCommid.id for collectquery in thsuser_collects ]
        try:
            cust_price = models.custcommprice.objects.get(Cpuserid=webuserquery,Cpcommid=int(product_id)).CpunPrice
        except:
            cust_price = None

    if request.method == 'GET':
        # 展示商品信息
        product_detail_data = models.commditydetail.objects.get(id = product_id)
        product_info_data = product_detail_data.Commid
        # 增加浏览次数
        try:
            product_view = models.commodityendinfo.objects.get(Commid=product_info_data)
        except:
            product_view = models.commodityendinfo(Commid=product_info_data)
        product_view.CeiViewNum += 1
        product_view.save()
        # 热销产品信息
        hot_list = []
        CeiBuyNUm_hot_datas = models.commodityendinfo.objects.order_by('CeiBuyNUm')[0:4]
        for CeiBuyNUm_hot_data in CeiBuyNUm_hot_datas:
            product_host_data = CeiBuyNUm_hot_data.Commid
            ths_detail = models.commditydetail.objects.filter(Commid = product_host_data.id)[0]
            hot_list.append({'info':product_host_data,'detail':ths_detail})

    return render(request, 'showproduct.html', locals())



# 异步收藏操作
def ajax_addcollect(request):
    """
    :param request.POST.worktype:工作类型 ("add",添加) ("del",删除)
           request.POST.detail  : 规格id
    :return:
    """
    if request.method == 'POST':
        if request.user.is_authenticated():
            login_username = request.user.username
            webuser_query = outputwebuser(request)
            detail_id = request.POST.get('detailid')
            worktype = request.POST.get('worktype')
            detail_query = models.commditydetail.objects.get(id = int(detail_id))
            is_collectdetail = models.custcollect.objects.filter(CcUserid = webuser_query,CcCommid = detail_query)
            if is_collectdetail:
                if worktype == "add":
                    return JsonResponse({'Msg': 'iscollect'})
                elif worktype == "del":
                    models.custcollect.objects.filter(CcUserid=webuser_query, CcCommid = detail_query).delete()
                    return JsonResponse({'Msg': 'sudelete'})
                else:
                    return JsonResponse({'Msg','errworktype'})
            else:
                models.custcollect.objects.create(CcUserid = webuser_query,CcCommid = detail_query)
                return JsonResponse({'Msg': 'sucollect'})
        else:
            return JsonResponse({'Msg': 'nologin'})


# 异步购物车添加
def ajax_addshoppingcart(request):
    if request.method == 'POST':
        if request.user.is_authenticated():
            webuser_query = outputwebuser(request)
            detail_id = request.POST.get('detailid')
            worktype = request.POST.get('worktype')
            buynum = request.POST.get('buynum')
            if worktype == "buy":
                userphone = models.userbind.objects.get(userid=webuser_query).Userphone
                if not userphone:
                    return JsonResponse({'Msg': 'nophone'})
                detail_query = models.commditydetail.objects.get(id=int(detail_id))
                if int(buynum) <= 0 :
                    return JsonResponse({'Msg': 'uperr'})
                # 查看是否已经存在购物车
                this_shoppingcartdetail = models.shoppingcart.objects.filter(ScUserid=webuser_query,ScCollectid=detail_query)
                if this_shoppingcartdetail:
                    this_shoppingcartdetail = this_shoppingcartdetail[0]
                    this_shoppingcartdetail.ScNum += int(buynum)
                    this_shoppingcartdetail.ScSum = this_shoppingcartdetail.ScNum * this_shoppingcartdetail.ScunPrice
                    this_shoppingcartdetail.save()
                    return JsonResponse({'Msg': 'buysucc'})

                # 查看客户单价表里面是否有该商品的单价
                try:
                    ths_unprice = models.custcommprice.objects.get(Cpuserid=webuser_query,Cpcommid=int(detail_id)).CpunPrice
                except:
                    ths_unprice = detail_query.CodunPrice
                sum_price = ths_unprice*int(buynum)

                # 加入购物车操作
                models.shoppingcart.objects.create(ScUserid=webuser_query,ScCollectid=detail_query,ScNum=int(buynum),
                                                   ScunPrice=ths_unprice,ScSum=sum_price)
                return JsonResponse({'Msg':'buysucc'})
            elif worktype == "del":
                try:
                    # 这里回传的detailid其实是shoppingcart表的id
                    # 为了前端写起来方便
                    models.shoppingcart.objects.filter(id = int(detail_id),ScUserid=webuser_query).delete()
                    return JsonResponse({'Msg': 'delsucc'})
                except:
                    return JsonResponse({'Msg': 'delerror'})
        else:
            return JsonResponse({'Msg':'nologin'})


# 提交订单
# datadit {购物车id : 数量} 里面的数据类型都是string
def ajax_submitorder(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            datastr = request.POST.get('tr_list')
            datadit = {}
            datastr = re.sub(r'\{|\}|\"',"",datastr)
            for adatastr in datastr.split(","):
                if adatastr:
                    adatastr_split = adatastr.split(":")
                    datadit[adatastr_split[0]] = adatastr_split[1]
            try:
                for scid in datadit.keys():
                    ths_sc = models.shoppingcart.objects.get(id = int(scid))
                    if int(datadit[scid]) <= 0:
                        return JsonResponse({'Msg': 'uperr'})
                    ths_sc.ScNum = int(datadit[scid])
                    ths_sc.ScSum = int(datadit[scid]) * ths_sc.ScunPrice
                    ths_sc.save()
                return JsonResponse({'Msg': 'submitsucc'})
            except:
                return JsonResponse({'Msg': 'submiterror'})
        else:
            return JsonResponse({'Msg': 'nologin'})


# 异步对订单商品进行处理
# 功能用在订单管理页面
def ajax_adminflowoperate(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            webuser_query = outputwebuser(request)
            ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
            worktype = request.POST.get('worktype')
            ths_userule = models.userrule.objects.get(Userid=webuser_query)
            cancgunprice = ths_userule.ModOrderPrice
            cancgorder = ths_userule.ModOrder

            #  查找所有商品名词
            if worktype == 'query-fp':
                plist = [ [apinfo.CommName,apinfo.id] for apinfo in  models.commodityinfo.objects.all() ]
                return JsonResponse({'Msg':'succ','plist':plist})

            # 查找请求中productid 的商品图片,及其规格
            if worktype == 'query-pd':
                productid = request.POST.get('productid')
                custid = request.POST.get('custid')
                product_query = models.commodityinfo.objects.get(id=int(productid))
                dlist = [ [str(dinfo),dinfo.id] for dinfo in  models.commditydetail.objects.filter(Commid=product_query) ]
                d1_id = dlist[0][1]
                d1_detail = models.commditydetail.objects.get(id=d1_id)
                try:
                    unprice = models.custcommprice.objects.get(Cpuserid=int(custid),Cpcommid=d1_id).CpunPrice
                except:
                    unprice = d1_detail.CodunPrice

                return JsonResponse({'Msg': 'succ', 'dlist': dlist, 'imgurl':str(product_query.Commimg).replace('HdWxShop',''),
                                    'unprice': unprice,'thick':d1_detail.Codthick,'psize':d1_detail.CodSize,'protlevel':d1_detail.Cod_Protlevel,
                                     'nmun':d1_detail.CodUnmun})


            # 根据detailid 查询规格信息
            if worktype == 'query-detail':
                detailid = request.POST.get('detailid')
                custid = request.POST.get('custid')
                detailquery = models.commditydetail.objects.get(id=int(detailid))
                try:
                    unprice = models.custcommprice.objects.get(Cpuserid=int(custid),Cpcommid=int(detailid)).CpunPrice
                except:
                    unprice = detailquery.CodunPrice
                return JsonResponse({'Msg':'succ','unprice':unprice,'thick':detailquery.Codthick,'psize':detailquery.CodSize,
                                     'protlevel':detailquery.Cod_Protlevel,'nmun':detailquery.CodUnmun})


            #  保存订单商品信息
            if worktype == 'save-fp':
                fpid = int(request.POST.get('fpid'))
                flowid = models.shoppingflowproduct.objects.get(id=int(fpid)).shoppingflowid
                isrole = isflowadmin(flowid=flowid,webuser_query=webuser_query,rolename=ths_rolename)
                ths_flow = models.shoppingflowproduct.objects.get(id=int(fpid))
                # 查看用户是否有修改单价权限,没有则查询数据库中原单价
                if cancgunprice:
                    unprice = float(request.POST.get('unprice'))
                else:
                    unprice =ths_flow.sfpunPrice
                # 查看用户是否有修改订单的权限
                if cancgorder:
                    ths_flow.shoppinginfoid = models.commodityinfo.objects.get(id=int(request.POST.get('productid')))
                    ths_flow.shoppingdetailid = models.commditydetail.objects.get(id=int(request.POST.get('detailid')))
                    buynum = int(request.POST.get('productnum'))
                    ths_flow.sfpthick = request.POST.get('thick')
                    ths_flow.sfpSize = request.POST.get('psize')
                    ths_flow.sfp_Protlevel = request.POST.get('protlevel')
                    ths_flow.sfpUnmun = int(request.POST.get('nmun'))
                else:
                    buynum = ths_flow.sfpnum

                if isrole:
                    ths_flow.sfpunPrice = unprice
                    ths_flow.sfpnum = buynum
                    ths_flow.sfpsumprice = unprice * buynum
                    ths_flow.save()
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg':'error','errmsg':'没有足够的权限修改'})


            # 添加订单信息
            if worktype == "add-fp":
                flowid = request.POST.get('flowid')
                isrole = isflowadmin(flowid=flowid, webuser_query=webuser_query, rolename=ths_rolename)
                if isrole and cancgorder :
                    detail_query = models.commditydetail.objects.get(id=int(request.POST.get('detailid')))
                    custid = request.POST.get('custid')
                    product_query = models.commodityinfo.objects.get(id=int(request.POST.get('productid')))
                    unprice = request.POST.get('unprice')
                    thick = request.POST.get('thick')
                    psize = request.POST.get('psize')
                    protlevel = request.POST.get('protlevel')
                    nmun = request.POST.get('nmun')
                    productnum = request.POST.get('productnum')
                    flow_query = models.shoppingflow.objects.get(id=int(flowid))
                    models.shoppingflowproduct.objects.create(shoppingflowid=flow_query,shoppinginfoid=product_query,shoppingdetailid=detail_query,
                                                              sfpUnmun=nmun,sfpsumprice=float(unprice) * int(productnum),sfpUnit=detail_query.CodUnit,sfpthick=thick,
                                                              sfpSize=psize,sfp_Protlevel=protlevel,sfpunPrice=float(unprice),sfpnum=productnum)
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'error', 'errmsg': '没有足够的权限添加'})


            # 删除订单商品信息
            if worktype == "del-fp":
                fpid = request.POST.get("fpid")
                flowid = models.shoppingflowproduct.objects.get(id=int(fpid)).shoppingflowid
                isrole = isflowadmin(flowid=flowid, webuser_query=webuser_query, rolename=ths_rolename)
                if isrole and cancgorder:
                    models.shoppingflowproduct.objects.get(id=int(fpid)).delete()
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'error', 'errmsg': '没有足够的权限删除'})


            # 审核不通过
            if worktype == "aud-fp":
                thsflow = models.shoppingflow.objects.get(id=int(request.POST.get("flowid")))
                isrole = isflowadmin(flowid=thsflow, webuser_query=webuser_query, rolename=ths_rolename)
                canaudit = ths_userule.AppOrder
                if canaudit and isrole and thsflow.Sfstatus == 2:
                    thsflow.Sfstatus -= 1
                    thsflow.save()
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'error', 'errmsg': '没有足够的权限'})

            # 更改邮费
            if worktype == "save-cp":
                if ths_userule.ModOrder or ths_userule.ModOrderPrice:
                    flowid = request.POST.get('flowid')
                    iscarryprice = request.POST.get('iscarryprice')
                    carryprice = request.POST.get('carryprice')
                    thsflow = models.shoppingflow.objects.get(id=int(flowid))
                    thsflow.SfCarryPrice = float(carryprice)
                    if iscarryprice:
                        thsflow.SfisCarryPrice = True
                    else:
                        thsflow.SfisCarryPrice = False
                    thsflow.save()
                    return JsonResponse({'code':1})
                else:
                    return JsonResponse({'code':99})


# 商品管理接口
def ajax_adminproduct(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            webuser_query = outputwebuser(request)
            ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
            worktype = request.POST.get('worktype')
            ths_userule = models.userrule.objects.get(Userid=webuser_query)

            # 修改规格
            if worktype == "mod-detail":
                thsrule = ths_userule.ModCommodity
                if thsrule:
                    iscover = request.POST.get('iscover')
                    detailid = request.POST.get('detailid')
                    ths_detail = models.commditydetail.objects.get(id=int(detailid))
                    ths_detail.Codbrand = request.POST.get('brand')
                    ths_detail.Codfunction = request.POST.get('func')
                    ths_detail.CodUnit = request.POST.get('dunit')
                    ths_detail.Codthick = request.POST.get('dthick')
                    ths_detail.CodSize = request.POST.get('dsize')
                    ths_detail.Cod_Protlevel = request.POST.get('protlevel')
                    ths_detail.Codinventory = request.POST.get('inventory')
                    ths_detail.CodUnmun = request.POST.get('dnmun')
                    ths_detail.CodunPrice = request.POST.get('unprice')
                    ths_detail.save()
                    if iscover.upper() == "TRUE":
                        models.custcommprice.objects.filter(Cpcommid=int(detailid)).delete()
                    return JsonResponse({'Msg':'succ'})
                else:
                    return JsonResponse({'Msg': 'norule'})

            # 添加规格
            if worktype == "add-detail":
                thsrule = ths_userule.ModCommodity
                if thsrule:
                    productid = request.POST.get('productid')
                    ths_product = models.commodityinfo.objects.get(id=int(productid))
                    brand = request.POST.get('brand')
                    func = request.POST.get('func')
                    dunit = request.POST.get('dunit')
                    dthick = request.POST.get('dthick')
                    dsize = request.POST.get('dsize')
                    protlevel = request.POST.get('protlevel')
                    inventory =request.POST.get('inventory')
                    dnmun = request.POST.get('dnmun')
                    unprice = request.POST.get('unprice')
                    models.commditydetail.objects.create(Commid=ths_product,Codbrand=brand,Codfunction=func,CodUnit=dunit,Codthick=dthick,CodSize=dsize,
                                                         Cod_Protlevel=protlevel,CodunPrice=unprice,Codinventory=inventory,
                                                         CodUnmun=dnmun)
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'norule'})

            # 删除商品
            if worktype == 'del-product':
                thsrule = ths_userule.ModCommodity
                if thsrule:
                    delete_liststring = request.POST.get('deletelist')
                    delete_liststring = delete_liststring.replace("[","").replace("]","").replace("\"","")
                    delete_list = delete_liststring.split(",")
                    for product in delete_list:
                        del_product = models.commodityinfo.objects.get(id=int(product))

                        # 在删除完数据后,顺便把图片也删掉
                        oldimg = str(del_product.Commimg)
                        oldinfo = str(del_product.CommInfo)
                        del_product.delete()
                        os.remove(oldimg)
                        os.remove(oldinfo)
                        return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'norule'})

            # 删除detail列表
            if worktype == "del-detail":
                thsrule = ths_userule.ModCommodity
                if thsrule:
                    delete_liststring = request.POST.get('deletelist')
                    delete_liststring = delete_liststring.replace("[","").replace("]","").replace("\"","")
                    delete_list = delete_liststring.split(",")
                    for detail in delete_list:
                        models.commditydetail.objects.get(id=int(detail)).delete()
                    return JsonResponse({'Msg': 'succ'})
                else:
                    return JsonResponse({'Msg': 'norule'})

            # 添加商品类型
            if worktype == "add-pcls":
                thsrule = ths_userule.AddCommodity
                if thsrule:
                    pclsname = request.POST.get('clsname')
                    models.commodityclass.objects.create(CclassName=pclsname)
                    pclsinfo = models.commodityclass.objects.get(CclassName=pclsname)
                    return JsonResponse({'Msg': 'succ','clsid':pclsinfo.id})
                else:
                    return JsonResponse({'Msg': 'norule'})
        else:
            return JsonResponse({'Msg': 'nologin'})


# 首页推荐商品管理接口
def ajax_admincommend(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        my_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        if my_rolename == "客户":
            return JsonResponse({'rcode':'98'})

        worktype = request.POST.get('worktype')

        # 获取主页推荐商品json
        if worktype == "get":
            commendlist = []
            allcommend = models.indexcommend.objects.all().order_by('commendidx')
            for acommend in allcommend:
                commendlist.append({
                    'cid':acommend.id,
                    'cindex':acommend.commendidx,
                    'pid':acommend.commenddetail.id,
                    'pname':acommend.commenddetail.Commid.CommName,
                    'prcls':acommend.commenddetail.Commid.Commclass.CclassName,
                    'brand':acommend.commenddetail.Codbrand,
                    'pfunction':acommend.commenddetail.Codfunction,
                    'punit':acommend.commenddetail.CodUnit,
                    'thick':acommend.commenddetail.Codthick,
                    'psize':acommend.commenddetail.CodSize,
                    'protlevel':acommend.commenddetail.Cod_Protlevel,
                    'inventory':acommend.commenddetail.Codinventory,
                    'dnum':acommend.commenddetail.CodUnmun,
                })
            return JsonResponse({'rcode':'1','commendlist':commendlist})

        # 删除某项推荐商品
        if worktype == "del":
            commendid = int(request.POST.get('commendid'))
            try:
                models.indexcommend.objects.get(id=commendid).delete()
                return JsonResponse({'rcode': '1'})
            except:
                return JsonResponse({'rcode': '97'})

        # 用户添加时查询商品规格
        if worktype == "detail":
            detaillist = []
            productid = int(request.POST.get('productid'))
            details = models.commditydetail.objects.filter(Commid=models.commodityinfo.objects.get(id=productid))
            for adetail in details:
                detaillist.append({
                    'name':str(adetail),
                    'id':adetail.id
                })
            return JsonResponse({'rcode': '1','details':detaillist})

        # 添加推荐商品
        if worktype == "add":
            detailid = int(request.POST.get('detailid'))
            maxidx = models.indexcommend.objects.all().aggregate(Max('commendidx'))
            if maxidx['commendidx__max']:
                newidx = int(maxidx['commendidx__max']) + 1
            else:
                newidx = 1
            try:
                models.indexcommend.objects.create(commendidx=newidx,commenddetail=models.commditydetail.objects.get(id=detailid))
                return JsonResponse({'rcode': '1'})
            except:
                return JsonResponse({'rcode':'96'})

        # 保存顺序
        if worktype == "save":
            commendlist = request.POST.getlist('commendlist')
            print(commendlist)
            models.indexcommend.objects.all().delete()
            for commend in commendlist:
                idx,detailid = commend.split('&')
                models.indexcommend.objects.create(commendidx=int(idx),commenddetail=models.commditydetail.objects.get(id=(detailid)))
            return JsonResponse({'rcode': '1'})
    else:
        return JsonResponse({'rcode':'99'})


# 用户管理接口
def ajax_adminuser(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        my_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        worktype = request.POST.get('worktype')
        my_userule = models.userrule.objects.get(Userid=webuser_query)

        # 修改权限
        if worktype == "modrule":
            # 没有用户修改权限
            if not my_userule.ModRule:
                return JsonResponse({'Msg': 'norule'})

            userid = request.POST.get('userid')
            ths_user = models.webuser.objects.get(id=int(userid))
            ths_userrule = models.userrule.objects.get(Userid=ths_user)

            # 从获取到的数据来修改权限
            ths_userrule.ReleaseAdv = str2bool(request.POST.get('isadv'))
            ths_userrule.ReleaseNew = str2bool(request.POST.get('isnews'))
            ths_userrule.ReleaseInfo = str2bool(request.POST.get('isinfo'))
            ths_userrule.AddCommodity = str2bool(request.POST.get('isaddp'))
            ths_userrule.ModCommodity = str2bool(request.POST.get('ismodp'))
            ths_userrule.AddOrder = str2bool(request.POST.get('isaddo'))
            ths_userrule.ModOrder = str2bool(request.POST.get('ismodo'))
            ths_userrule.ModOrderPrice = str2bool(request.POST.get('ismodop'))
            ths_userrule.AppOrder = str2bool(request.POST.get('isappo'))
            ths_userrule.AckOrder = str2bool(request.POST.get('isacko'))
            ths_userrule.PaidOrder = str2bool(request.POST.get('ispado'))
            ths_userrule.ShipOrder = str2bool(request.POST.get('isshpo'))
            ths_userrule.RecOrder = str2bool(request.POST.get('isreco'))
            ths_userrule.TranInfo = str2bool(request.POST.get('istrif'))
            ths_userrule.SalePer = str2bool(request.POST.get('issalp'))
            ths_userrule.ProSummary = str2bool(request.POST.get('isprsm'))
            ths_userrule.ModRule = str2bool(request.POST.get('ismodu'))
            ths_userrule.setcustprice = str2bool(request.POST.get('isstcp'))
            try:
                ths_userrule.save()
                return JsonResponse({'Msg': 'succ'})
            except:
                return JsonResponse({'Msg': 'error'})


        # 添加客户价格
        if worktype == "setcp":
            # 没有设置客户价格权限
            if not my_userule.setcustprice:
                return JsonResponse({'Msg': 'norule'})

            userid = request.POST.get('userid')
            detailid = request.POST.get('detailid')
            unprice = request.POST.get('unprice')
            ths_user = models.webuser.objects.get(id=int(userid))
            ths_detail = models.commditydetail.objects.get(id=int(detailid))

            # 判断单价库中是否存在
            is_custprice = models.custcommprice.objects.filter(Cpuserid=ths_user,Cpcommid=ths_detail).count()
            if is_custprice >0:
                return JsonResponse({'Msg': 'hascp'})

            models.custcommprice.objects.create(Cpuserid=ths_user,Cpcommid=ths_detail,CpunPrice=unprice)
            return JsonResponse({'Msg': 'succ'})

        # 删除客户价格
        if worktype == "delcp":

            if not my_userule.setcustprice:
                return JsonResponse({'Msg': 'norule'})

            userid = request.POST.get('userid')
            delete_liststring = request.POST.get('deletelist')
            delete_liststring = delete_liststring.replace("[", "").replace("]", "").replace("\"", "")
            delete_list = delete_liststring.split(",")
            for cpid in delete_list:
                models.custcommprice.objects.get(id=int(cpid)).delete()
            return JsonResponse({'Msg': 'succ'})

    else:
        return JsonResponse({'Msg': 'nologin'})


# 管理用户地址
@login_required(login_url = '/login/')
def ajax_adminaddress(request):
    webuser_query = outputwebuser(request)
    if request.method == "POST":
        worktype = request.POST.get('type')
        # 编辑地址操作
        if worktype == "edit":
            addressid = request.POST.get('addressid')
            address = request.POST.get('address')
            try:
                address_query = models.useraddress.objects.get(userid=webuser_query,id=int(addressid))
                address_query.UserAddress = address
                address_query.save()
                return JsonResponse({'code':'1'})
            except:
                return JsonResponse({'code':'500'})
        # 删除地址
        if worktype == 'del':
            addressid = request.POST.get('addressid')
            try:
                address_query = models.useraddress.objects.get(userid=webuser_query, id=int(addressid))
                address_query.delete()
                return JsonResponse({'code': '1'})
            except:
                return JsonResponse({'code': '500'})
        # 添加地址
        if worktype == 'add':
            address = request.POST.get('address')
            # 用户地址数量不能大于10个
            useraddress_count = models.useraddress.objects.filter(userid=webuser_query).count()
            if useraddress_count >= 10 :
                return JsonResponse({'code': '501'})
            try:
                models.useraddress.objects.create(userid=webuser_query,UserAddress=address)
                return JsonResponse({'code': '1'})
            except:
                return JsonResponse({'code': '500'})
        # 获取信息
        if worktype == 'get':
            addresslist = [ address.UserAddress for address in  models.useraddress.objects.filter(userid=webuser_query)]
            return JsonResponse(
                {'code':'1',
                 'addresslist':addresslist}
            )


# 新闻信息管理
def ajax_adminnews(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        userule = models.userrule.objects.get(Userid=webuser_query)

        isadminnews = userule.ReleaseNew
        if isadminnews:
            worktype = request.POST.get('worktype')
            # 添加新闻类型
            if worktype == "addcls":
                newscls = request.POST.get('newscls')
                models.newsclass.objects.create(Nclassname=newscls)
                return JsonResponse({'rcode': 1})
            # 删除新闻信息
            if worktype == "delnews":
                delnews_string = request.POST.get('deletelist')
                delnews_string = delnews_string.replace("[", "").replace("]", "").replace("\"", "")
                delnews_list = delnews_string.split(",")
                for anews in delnews_list:
                    models.newsinfo.objects.get(id=int(anews)).delete()
                return JsonResponse({'rcode':1})
        # 没有权限
        else:
            return JsonResponse({'rcode': 0})
    # 没登录
    else:
        return JsonResponse({'rcode': 99})



# 销售人员绑定客户
def ajax_salebindcust(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        my_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename

        if my_rolename == "销售人员":
            customer = models.webuser.objects.get(id=int(request.POST.get('custid')))
            has_bind = models.custsalebind.objects.filter(Customerid=customer,Saleid=webuser_query)
            if has_bind:
                return JsonResponse({'Msg': 'err'})
            else:
                models.custsalebind.objects.create(Customerid=customer,Saleid=webuser_query)
                return JsonResponse({'Msg': 'succ'})


# 解邦客户
def ajax_unbindcust(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        my_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename

        if my_rolename == "销售人员":
            customer = models.webuser.objects.get(id=int(request.POST.get('custid')))
            has_bind = models.custsalebind.objects.filter(Customerid=customer, Saleid=webuser_query)
            if has_bind:
                models.custsalebind.objects.get(Customerid=customer, Saleid=webuser_query).delete()
                return JsonResponse({'rcode': 1})
            else:
                return JsonResponse({'rcode': 0})
        else:
            return JsonResponse({'rcode': 99})
    else:
        return JsonResponse({'rcode': 99})


# 客户设置销售人员
def ajax_setsale(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        saleid = request.POST.get('saleid')
        salequery = models.webuser.objects.get(id=int(saleid))
        # 查看用户是否已绑定销售人员
        isbind = models.custsalebind.objects.filter(Customerid=webuser_query).Count()
        if isbind >= 0:
            return JsonResponse({'rcode': 0})
        else:
            models.custsalebind.objects.create(Customerid=webuser_query,Saleid=salequery)
        return JsonResponse({'rcode': 1})
    else:
        return JsonResponse({'rcode': 99})


# 修改密码接口
def ajax_cpassword(request):
    if request.user.is_authenticated():
        username = request.user.username
        oldpassword = request.POST.get('oldpassword')
        newpassword1 = request.POST.get('newpassword1')
        newpassword2 = request.POST.get('newpassword2')
        # 检验两次密码是否一样和密码长度是否大于6位
        if newpassword1 != newpassword2 or len(newpassword1) < 6:
            return JsonResponse({'rcode': 0})
        user = authenticate(username=username, password=oldpassword)
        if user is not None and user.is_active:
            user.set_password(newpassword1)
            user.save()
            return JsonResponse({'rcode': 1})
        else:
            return JsonResponse({'rcode': 2})


# 手机发送验证码
def ajax_sendcheckcode(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        username = request.user.username
        worktype = request.POST.get('worktype')
        phone_number = request.POST.get('phonenum')
        if worktype == "bindphone":
            this_checkcode = createrandomcode(6)
            redis_key = worktype + "&&" + str(username) + "##" + phone_number
            if cache.keys(worktype + "&&" + str(username) + "##*"):
                return JsonResponse({'rcode': 0})
            else:
                cache.set(redis_key,this_checkcode,60)
                business_id = uuid.uuid1()
                # params = "{\"code\":" + this_checkcode + "}"
                # ali_request = demo_sms_send.send_sms(
                #                          business_id=business_id,
                #                          phone_numbers=phone_number,
                #                          sign_name=ali_sign_name,
                #                          template_code=ali_checkcode_templetcode,
                #                          template_param=params
                #                          )
                # print(ali_request)
                return JsonResponse({'rcode': 1})
    # 还没登录
    else:
        return JsonResponse({'rcode': 99})


# 重置密码发送验证码
def ajax_resetpassword_sendcode(request):
    username = request.POST.get('username')
    phonenumber = request.POST.get('phonenumber')
    imgcheckcode = request.POST.get('checkcode')
    session_imgcheckcode = request.session['check_code']
    if imgcheckcode.upper() != str(session_imgcheckcode).upper() or not imgcheckcode:
        # 验证码错误,清空checkcode
        request.session['check_code'] = ""
        return JsonResponse({'rcode':98})
    try:
        findusername = User.objects.get(username=username)
        finduserphone = models.userbind.objects.get(userid__userid=findusername).Userphone
    except:
        return JsonResponse({'rcode': 99})

    if phonenumber == finduserphone:
        session_key = "resetpassword##" + str(request.session.session_key)
        if cache.has_key(session_key):
            return JsonResponse({'rcode': 2})
        else:
            this_checkcode = createrandomcode(6)
            # 为了省短信前,测试用,记得删掉
            print(this_checkcode)
            session_value = {
                "username":username,
                "phone":phonenumber,
                "code":this_checkcode,
                "check":0
            }
            cache.set(session_key,session_value,60)
            business_id = uuid.uuid1()
            # params = "{\"code\":" + this_checkcode + "}"
            # ali_request = demo_sms_send.send_sms(
            #                          business_id=business_id,
            #                          phone_numbers=phonenumber,
            #                          sign_name=ali_sign_name,
            #                          template_code=ali_checkcode_templetcode,
            #                          template_param=params
            #                          )
            # print(ali_request)
            return JsonResponse({'rcode':1})
    else:
        request.session['check_code'] = ""
        return JsonResponse({'rcode': 99})


# 用户修改昵称接口
def ajax_change_webusername(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        request_webusername = str(request.POST.get('webusername'))
        if re.fullmatch("[a-zA-Z0-9_\u4e00-\u9fa5]{1,18}",request_webusername):
            try:
                webuser_query.Username = request_webusername
                webuser_query.save()
                return JsonResponse({'rcode': 1})
            except:
                # 不知道什么情况,反正就是异常了
                return JsonResponse({'rcode': 98})
        # 昵称格式有误
        else:
            return JsonResponse({'rcode':0})
    # 没登录
    else:
        return JsonResponse({'rcode':99})



@login_required(login_url = '/login/')
def Website_home(request):
    title = '个人主页'
    classes = models.commodityclass.objects.all()
    login_username = False
    shoppingcart_Count = 0
    ismobile = is_mobilerequest(request)
    webuser_query = outputwebuser(request)
    userinfo = models.userbind.objects.get(userid=webuser_query)
    shoppingcart_Count = models.shoppingcart.objects.filter(ScUserid=webuser_query).count()
    userrule = models.userrule.objects.get(Userid=webuser_query)
    if request.user.is_authenticated():
        login_username = request.user.username
    if ismobile:
        return render(request,'mobilepersonal.html',locals())
    else:
        return render(request,'sitehome.html',locals())


# 绑定手机界面
@login_required(login_url = '/login/')
def Website_userbindphone(request):
    classes = models.commodityclass.objects.all()
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    message = ""
    phone_number = ""

    if request.method == 'GET':
        return render(request,'userbindphone.html',locals())

    if request.method == 'POST':
        phone_number = request.POST.get('phonenumber')
        ths_checkcode = request.POST.get('phonecheckcode')
        worktype = "bindphone"
        checkcode_key = worktype + "&&" + str(login_username) + "##" + phone_number
        if cache.has_key(checkcode_key):
            redis_checkcode = cache.get(checkcode_key)
            if redis_checkcode == ths_checkcode:
                ths_userbind = models.userbind.objects.get(userid=webuser_query)
                ths_userbind.Userphone = phone_number
                ths_userbind.save()
                return HttpResponseRedirect('/website/userinfo')
            # 验证码错误
            else:
                message = "验证码错误"
                return render(request, 'userbindphone.html', locals())
        # 缓存中没有验证码
        else:
            message = "请先获取验证码"
            return render(request, 'userbindphone.html', locals())


# 我的收藏
@login_required(login_url = '/login/')
def Website_collect(request):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    title = "收藏夹"
    is_mobile = is_mobilerequest(request)
    if request.user.is_authenticated():
        login_username = request.user.username
        login_userid = request.user.id
        webuserid = models.webuser.objects.get(userid = login_userid).id
        collects = []
        collect_tables = models.custcollect.objects.filter(CcUserid = webuserid).order_by('CollectDate')
        for acollect in collect_tables:
            userunprice = models.custcommprice.objects.filter(Cpuserid=webuserid,Cpcommid=acollect.CcCommid)
            if userunprice.count() >  0:
                userunprice = userunprice[0].CpunPrice
            else:
                userunprice = acollect.CcCommid.CodunPrice
            collects.append({'collectinfo':acollect,'unprice':userunprice})

        paginator = Paginator(collects,showmany)
        try:
            page = int(request.GET.get('page'))
        except:
            page = 1
        collects = paginator.page(page)
        pagelist = [i for i in paginator.page_range]

        if is_mobile:
            return render(
                request, 'mobilecollect.html',
                {'classes': classes, 'login_username': login_username,
                 'collects': collects,'title':title,'page':page,'pagelist':pagelist}
                )
        else:
            return render(
                request,'websitecollect.html',
                {'classes':classes,'login_username':login_username,
                 'collects':collects,'title':title,'page':page,'pagelist':pagelist}
                )


# 我的购物车
@login_required(login_url = '/login/')
def Website_shoppingcart(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    title = "购物车"
    is_mobile = is_mobilerequest(request)
    if request.user.is_authenticated():
        login_username = request.user.username
        login_userid = request.user.id
        webuserid = models.webuser.objects.get(userid = login_userid).id
        shoppingcart_tables = models.shoppingcart.objects.filter(ScUserid = webuserid)
        shoppingcart = []

        for ths_product in shoppingcart_tables:
            product_detail = ths_product.ScCollectid
            product_info = product_detail.Commid
            shoppingcart.append({'cart':ths_product,'detail':product_detail,'info':product_info})

        if is_mobile:
            return render(request, 'mobileshoppingcart.html',
                          {'classes': classes, 'login_username': login_username, 'shoppingcart': shoppingcart,'title':title}
                          )
        else:
            return render(request,'shoppingcart.html',
                          {'classes':classes,'login_username':login_username,'shoppingcart':shoppingcart,'title':title}
                          )


# 确认购物车
@login_required(login_url = '/login/')
def Website_submitshoppingcart(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    title = "确认订单"
    is_mobile = is_mobilerequest(request)
    if request.user.is_authenticated():
        login_username = request.user.username
        login_userid = request.user.id
        webuserquery = models.webuser.objects.get(userid=login_userid)
        webuserid = webuserquery.id
        webuseraddress = models.userbind.objects.get(userid=webuserid).UserAddress
        # 用户的购物车信息
        shoppingcart_tables = models.shoppingcart.objects.filter(ScUserid=webuserid)
        if request.method == 'GET':
            if len(shoppingcart_tables) == 0 :
                return HttpResponseRedirect('/website/shoppingcart/')

            shoppingcart_total = sum([ scinfo.ScSum for scinfo in shoppingcart_tables ])
            shoppingcart = []
            for ths_product in shoppingcart_tables:
                product_detail = ths_product.ScCollectid
                product_info = product_detail.Commid
                shoppingcart.append({'cart': ths_product, 'detail': product_detail, 'info': product_info})

            if is_mobile:
                return render(request, 'mobilesubmit.html',
                              {'classes': classes, 'login_username': login_username, 'useraddress': webuseraddress, 'title':title,
                               'shoppingcart': shoppingcart, 'sctotal': shoppingcart_total}
                              )
            else:
                return render(request,'submitshoppingcart.html',
                          {'classes':classes,'login_username':login_username,'useraddress':webuseraddress,
                           'shoppingcart':shoppingcart,'sctotal':shoppingcart_total}
                          )

        # 客户确认提交订单
        if request.method == 'POST':
            request_address = request.POST.get('address')
            request_remark = request.POST.get('remark')
            # 判断购物车中是否有商品
            if shoppingcart_tables:
            # 判断地址是否有填写,地址必填
                if request_address:
                    flowid = createflowid()
                    # 创建订单流程表
                    shoppingflow_obj = models.shoppingflow(
                        flowid = flowid,
                        SfUserid=webuserquery,Sfstatus=1,SfCarryPrice=0,SfisCarryPrice=False,
                        SfRemark=request_remark,SfAddress=request_address)
                    shoppingflow_obj.save()
                    try:
                        for ths_product in shoppingcart_tables:
                            product_detail = ths_product.ScCollectid
                            product_info = product_detail.Commid
                            models.shoppingflowproduct.objects.create(
                                shoppingflowid=shoppingflow_obj,shoppinginfoid=product_info,shoppingdetailid=product_detail,
                                sfpnum=ths_product.ScNum,sfpsumprice=ths_product.ScSum,sfpUnit=product_detail.CodUnit,
                                sfpthick=product_detail.Codthick,sfpSize=product_detail.CodSize,sfp_Protlevel=product_detail.Cod_Protlevel,
                                sfpunPrice=ths_product.ScunPrice,sfpUnmun=product_detail.CodUnmun
                            )
                            # 处理完毕后把购物车中的内容删掉
                            models.shoppingcart.objects.filter(ScUserid=webuserid).delete()
                        return HttpResponseRedirect('/website/shoppingflow')
                    except:
                        shoppingflow_obj.delete()
                        return render(request,'sitemessage.html',
                                  {'classes':classes,'login_username':login_username,
                                   'messagetype':'danger','message':'提交订单失败,网站内部出现问题.'})
                # 没有填写地址
                else:
                    return render(request, 'sitemessage.html',
                                  {'classes': classes, 'login_username': login_username,
                                   'messagetype': 'danger', 'message': '没有填写地址.请填写后再试'})

            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '提交订单失败,购物车为空.'})


# 订单流程表
@login_required(login_url = '/login/')
def Website_shoppingflow(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    title = "我的订单"
    is_mobile = is_mobilerequest(request)
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)

        if request.method == 'GET':
            myshoppingflow_tables = []
            myshoppingflow = models.shoppingflow.objects.filter(SfUserid=webuser_query)
            for ths_shoppingflow in myshoppingflow:
                myshoppingflowproducts = models.shoppingflowproduct.objects.filter(shoppingflowid=ths_shoppingflow)
                # 运费
                shoppingcarryp = ths_shoppingflow.SfCarryPrice
                # 订单总费用
                myshoppingflowproducts_total = sum([aproduct.sfpsumprice for aproduct in myshoppingflowproducts]) + shoppingcarryp
                myshoppingflow_tables.append({'flowinfo':ths_shoppingflow,'productinfos':myshoppingflowproducts,
                                          'total':myshoppingflowproducts_total})
            if is_mobile:
                return render(request, 'mobilemyflow.html',
                              {'classes': classes, 'login_username': login_username,'title':title,
                               'myshoppingflow': myshoppingflow, 'myshoppingflow_tables': myshoppingflow_tables})
            else:
                return render(request,'shoppingflow.html',
                      {'classes': classes, 'login_username': login_username,'title':title,
                       'myshoppingflow':myshoppingflow,'myshoppingflow_tables':myshoppingflow_tables})


        if request.method == 'POST':
            myflow = models.shoppingflow.objects.get(id=int(request.POST.get('hipflowid')))
            flowuser = myflow.SfUserid
            if flowuser == webuser_query:

                # 客户点击确认订单
                if myflow.Sfstatus == 3:
                    myflow.Sfstatus += 1
                    myflow.save()
                    return HttpResponseRedirect('/wesbite/shoppingflow/')

                # 客户点击确认订单
                elif myflow.Sfstatus == 6:
                    myflow.Sfstatus += 1
                    fpquerys = models.shoppingflowproduct.objects.filter(shoppingflowid=myflow)
                    #查询销售人员
                    try:
                        salequery = models.custsalebind.objects.get(Customerid=webuser_query).Saleid
                    except:
                        salequery = None

                    # 创建订单流程完成表
                    endobj = models.shoppingendflow(
                        sefuserid=webuser_query,sefsaleid=salequery,Sefflowid=myflow.flowid,sefusername=webuser_query.Username,
                        sefcarryprice=myflow.SfCarryPrice,sefmark=myflow.SfRemark,sefcreatetime=myflow.SfCreatetime,
                        sefsubmitname=myflow.sfsubmitname,sefsubmittime=myflow.sfsubmittime,sefpayname=myflow.sfpayname,
                        sefpaytime = myflow.sfpaytime,sefsmname=myflow.sfsmname,sefsmtime=myflow.sfsmtime,
                        sefaddress=myflow.SfAddress
                    )
                    endobj.save()
                    # 创建订单流程商品
                    try:
                        if len(fpquerys) > 0:
                            for fpquery in fpquerys:
                                models.shoppingendflowproduct.objects.create(
                                    shoppingendflowid = endobj,
                                    sefproductid=fpquery.shoppinginfoid,sefdetailid=fpquery.shoppingdetailid,
                                    SefClass=fpquery.shoppinginfoid.Commclass.CclassName,SefName=fpquery.shoppinginfoid.CommName,
                                    SefunPrice=fpquery.sfpunPrice,SefNum=fpquery.sfpnum,SefPrice=fpquery.sfpsumprice,
                                    sefUnit=fpquery.sfpUnit,sefthick=fpquery.sfpthick,sefSize=fpquery.sfpSize,sef_Protlevel=fpquery.sfp_Protlevel,
                                    SefUnmun=fpquery.sfpUnmun
                                )
                                # 删掉订单商品表中的信息,添加到完成表中
                    except:
                        return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '确认失败!'})

                    myflow.delete()
                    return HttpResponseRedirect('/wesbite/shoppingflow/')

            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '提交失败!'})


# 个人历史信息
@login_required(login_url = '/login/')
def Website_userhistory(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    is_mobile = is_mobilerequest(request)
    title = "历史订单"
    login_username = request.user.username
    webuser_query = outputwebuser(request)

    starttime = request.GET.get('cstime')
    endtime = request.GET.get('cetime')
    selecttime = str(request.GET.get('selecttime'))

    if selecttime == '1':
        default_days = 90
    elif selecttime == '2':
        default_days = 180
    elif selecttime == '3':
        default_days = 360
    else:
        default_days = 30

    historyflow_list = []

    if starttime:
        cstime_datetime = datetime.datetime.strptime(starttime, "%Y-%m-%d %H:%M")
    else:
        cstime_datetime = datetime.date.today() - datetime.timedelta(days=default_days)
    if endtime:
        cetime_datetime = datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M")
    else:
        cetime_datetime = datetime.date.today() + datetime.timedelta(days=1)

    if selecttime == 'all':
        history_list = models.shoppingendflow.objects.filter(sefuserid=webuser_query)
    else:
        history_list = models.shoppingendflow.objects.filter(sefcreatetime__range=(cstime_datetime,cetime_datetime),sefuserid=webuser_query)

    for aendflow in history_list:
        history_product = models.shoppingendflowproduct.objects.filter(shoppingendflowid=aendflow)
        historyflow_list.append({'flowinfo':aendflow,
                             'productinfo':history_product})
    if is_mobile:
        return render(request, 'mobilehistory.html',
                  {'classes': classes, 'login_username': login_username, 'title': title,'cstime':starttime,'cetime':endtime,'selecttime':selecttime,
                    'historyflow_list':historyflow_list,
                   })
    else:
        return render(request, 'historyflow.html',
                      {'classes': classes, 'login_username': login_username, 'title': title, 'cstime': starttime,'selecttime':selecttime,
                       'cetime': endtime,
                       'historyflow_list': historyflow_list,
                       })



# 个人用户信息
@login_required(login_url = '/login/')
def Website_userinfo(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    is_mobile = is_mobilerequest(request)
    title = "个人信息"
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        # 获取用户表中的个人信息
        userinfo_query = models.userbind.objects.get(userid=webuser_query)
        # 获取销售人员列表
        sale_options = models.userrule.objects.filter(Roleid__Rolename='销售人员')
        try:
            userbind_query = models.custsalebind.objects.get(Customerid=webuser_query.id)
        except:
            userbind_query = False

        if is_mobile:
            return render(request, 'mobileuserinfo.html',
                          {'classes': classes, 'login_username': login_username,'title':title,
                           'sale_options': sale_options,
                           'webuser_query': webuser_query, 'userinfo_query': userinfo_query,
                           'userbind_query': userbind_query})
        else:
            return render(request,'userinfo.html',
                      {'classes': classes, 'login_username': login_username,'title':title,
                       'sale_options':sale_options,
                       'webuser_query' : webuser_query,'userinfo_query':userinfo_query,'userbind_query':userbind_query})


# 个人页面展示订单
@login_required(login_url = '/login/')
def Website_showmyflow(request,flowid):
    classes = models.commodityclass.objects.all()
    login_username = request.user.username
    flowinfo = models.shoppingflow.objects.get(id=int(flowid))
    is_mobile = is_mobilerequest(request)
    webuser_query = outputwebuser(request)
    title = flowinfo.flowid

    if is_mobile:
        render_template = 'mobileshowmyflow.html'
    else :
        render_template ='showmyflow.html'

    return render(request,render_template,
                  {'classes': classes, 'login_username': login_username, 'title': title,
                   'webuser_query': webuser_query,
                   'flowinfo':flowinfo,
                   })


# 订单管理
@login_required(login_url = '/login/')
def Website_adminflow(request):
    showmany = 3
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename


        # 需要返回的订单列表
        if ths_rolename == "客户":
            return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

        myflowlist = []
        if request.method == 'GET':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1


            search_username = request.GET.get('search-username')
            allflow = models.shoppingflow.objects.all()
            if search_username and search_username != "None":
                allflow = allflow.filter(SfUserid__Username__contains=search_username)

            if ths_rolename == "销售人员":
                # 找出与自己绑定的客户
                mycusts = models.custsalebind.objects.filter(Saleid=webuser_query)
                # 所有在绑定表中的客户,用来查找哪些用户还没有绑定销售人员
                allcusts = models.custsalebind.objects.all()

                mycustslist = [ cust.Customerid.id for cust in mycusts ]
                allcustset = [ cust.Customerid.id for cust in allcusts ]

                for thsflow in allflow:
                    thsflow_userid = thsflow.SfUserid.id
                    # 跟自己绑定的客户
                    if thsflow_userid in mycustslist:
                        thsflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=thsflow)
                        thssumprice = sum([ aproduct.sfpsumprice for aproduct in thsflowproduct]) + thsflow.SfCarryPrice
                        myflowlist.append({'userinfo':thsflow.SfUserid,'flowinfo':thsflow,'sumprice':thssumprice,'isbind':True})
                    elif thsflow_userid in allcustset:
                        continue
                    # 未绑定的客户
                    else:
                        thsflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=thsflow)
                        thssumprice = sum([ aproduct.sfpsumprice for aproduct in thsflowproduct]) + thsflow.SfCarryPrice
                        myflowlist.append({'userinfo':thsflow.SfUserid,'flowinfo':thsflow,'sumprice':thssumprice,'isbind':False})

            if ths_rolename == "财务人员":
                for thsflow in allflow:
                    if thsflow.Sfstatus == 4:
                        thsflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=thsflow)
                        thssumprice = sum([ aproduct.sfpsumprice for aproduct in thsflowproduct]) + thsflow.SfCarryPrice
                        myflowlist.append({'userinfo':thsflow.SfUserid,'flowinfo':thsflow,'sumprice':thssumprice,'isbind':True})

            if ths_rolename == "出货人员":
                for thsflow in allflow:
                    if thsflow.Sfstatus == 5:
                        thsflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=thsflow)
                        thssumprice = sum([ aproduct.sfpsumprice for aproduct in thsflowproduct]) + thsflow.SfCarryPrice
                        myflowlist.append({'userinfo':thsflow.SfUserid,'flowinfo':thsflow,'sumprice':thssumprice,'isbind':True})

            if ths_rolename == "管理员" or ths_rolename == "管理人员":
                for thsflow in allflow:
                    thsflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=thsflow)
                    thssumprice = sum([aproduct.sfpsumprice for aproduct in thsflowproduct]) + thsflow.SfCarryPrice
                    myflowlist.append({'userinfo': thsflow.SfUserid,'flowinfo': thsflow,'sumprice':thssumprice,'isbind': True})

            paginator = Paginator(myflowlist,showmany)
            try:
                pagflowlist = paginator.page(page)
            except PageNotAnInteger:
                pagflowlist = paginator.page(1)
            except EmptyPage:
                pagflowlist = paginator.page(1)
            pagelist = [ i for i in paginator.page_range ]

            return render(request,'adminshoppingflow.html',
                          {'classes': classes, 'login_username': login_username,'search_username':search_username,
                              'flowlist':pagflowlist,'pagelist':pagelist,'rolename':ths_rolename,})


# 单个订单管理的展示页面
@login_required(login_url = '/login/')
def Website_adminshowflow(request,flowid):
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolequery = models.userrule.objects.get(Userid=webuser_query.id)
        ths_rolename = ths_rolequery.Roleid.Rolename
        ths_flow = models.shoppingflow.objects.get(id=int(flowid))
        # 查询该订单的顾客
        isrole = isflowadmin(flowid=ths_flow,webuser_query=webuser_query,rolename=ths_rolename)

        # 权限
        userrule = models.userrule.objects.get(Userid=webuser_query)
        ths_flowstatus = ths_flow.Sfstatus
        isrule = False

        # 生成订单
        if ths_flowstatus == 1:
            isrule = userrule.AddOrder
        # 审核价格
        if ths_flowstatus == 2:
            isrule = userrule.AppOrder
        # 付款
        if ths_flowstatus == 4:
            isrule = userrule.PaidOrder
        # 出货
        if ths_flowstatus == 5:
            isrule = userrule.ShipOrder

        # 需要返回的订单列表
        if not isrole:
            return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

        if request.method == 'GET':
            try:
                ths_flowinfo = models.shoppingflow.objects.get(id=int(flowid))
            except:
                return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,找不到该订单信息.'})

            # 是否有权限修改价格和信息
            cancgunprice = userrule.ModOrderPrice
            cancgorder = userrule.ModOrder
            ths_flowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=ths_flowinfo)
            ths_total = sum([aproduct.sfpsumprice for aproduct in ths_flowproduct])
            iscarryprice = ths_flowinfo.SfisCarryPrice
            if not iscarryprice:
                ths_total += ths_flow.SfCarryPrice

            return render(request,'showflow.html',
                          {'classes': classes, 'login_username': login_username,
                           'flowinfo':ths_flowinfo,'productlist':ths_flowproduct,'total':ths_total,'isrule':isrule,
                           'cgunprie':cancgunprice,'cgorder':cancgorder,'iscarryprice':iscarryprice
                           })


        if request.method == 'POST':

            if isrule:
                # 记录操作人员及时间
                flowstatus = ths_flow.Sfstatus
                if flowstatus == 1:
                    ths_flow.sfsubmitname = webuser_query.Username
                    ths_flow.sfsubmittime = timezone.now()
                if flowstatus == 4:
                    ths_flow.sfpayname = webuser_query.Username
                    ths_flow.sfpaytime = timezone.now()
                if flowstatus == 5:
                    ths_flow.sfsmname = webuser_query.Username
                    ths_flow.sfsmtime = timezone.now()
                    # 出货后 库存-1
                    thsflow_products = models.shoppingflowproduct.objects.filter(shoppingflowid=ths_flow)
                    for aflowproduct in thsflow_products:
                        adetail = aflowproduct.shoppingdetailid
                        detailinventory = int(adetail.Codinventory)
                        detailinventory = detailinventory - int(aflowproduct.sfpnum)
                        # 库存最小值为0
                        if detailinventory < 0:
                            detailinventory = 0
                        adetail.Codinventory = detailinventory
                        adetail.save()

                ths_flow.Sfstatus += 1
                ths_flow.save()
                return HttpResponseRedirect(request.path)
            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,您没有足够的权限.'})


# 导出历史交易信息
@login_required(login_url = '/login/')
def Website_outputtrade(request):
    showmany = 10
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        # 几个templet里面的参数,初始化
        saleid = custid = cstime = cetime = ""
        trade_list = []
        pagelist = None

        # 从权限表中查询是否有权限
        canoutputtrade = models.userrule.objects.get(Userid=webuser_query).TranInfo
        if not canoutputtrade:
            return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

        if ths_rolename == '客户':
            return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

        if ths_rolename == '销售人员':
            custoptions = set([ sef.sefuserid for sef in models.shoppingendflow.objects.filter(sefsaleid=webuser_query)])
            saleoptions = set([ sef.sefsaleid for sef in models.shoppingendflow.objects.filter(sefsaleid=webuser_query)])

        else:
            custoptions = set([ sef.sefuserid for sef in models.shoppingendflow.objects.all()])
            saleoptions = set([ sef.sefsaleid for sef in models.shoppingendflow.objects.all()])


        if request.method == 'GET':
            # 返回执行的工作类型,有两种,1. 查询 2.导出
            worktype =request.GET.get('worktype')
            saleid = request.GET.get('salename')
            custid = request.GET.get('custname')
            cstime = request.GET.get('cstime')
            cetime = request.GET.get('cetime')

            if  cstime:
                cstime_datetime = datetime.datetime.strptime(cstime,"%Y-%m-%d %H:%M")
            else:
                cstime_datetime = datetime.date(2000,1,1)

            if cetime:
                cetime_datetime = datetime.datetime.strptime(cetime,"%Y-%m-%d %H:%M")
            else:
                cetime_datetime = datetime.date(2099,1,1)

            # 根据GET返回值进行查询,filter_str 为filter 查询中执行的语句
            filter_str  = "sefcreatetime__range=(cstime_datetime,cetime_datetime),"
            if saleid:
                filter_str += "sefsaleid=models.webuser.objects.get(id=int(saleid)),"
            if custid:
                filter_str += "sefuserid=models.webuser.objects.get(id=int(custid)),"
            if ths_rolename == '销售人员':
                ths_shoppingendflow = eval("models.shoppingendflow.objects.filter(sefsaleid=webuser_query,%s)"%filter_str)
            else:
                ths_shoppingendflow = eval("models.shoppingendflow.objects.filter(%s)"%filter_str)

            if worktype == '查询':
                try:
                    page = int(request.GET.get('page'))
                except:
                    page = 1
                paginator = Paginator(ths_shoppingendflow, showmany)
                try:
                    trade_list = paginator.page(page)
                except :
                    trade_list = paginator.page(1)

                pagelist = [i for i in paginator.page_range]


                return render(request, 'websiteoutputRade.html',
                              {'classes': classes, 'login_username': login_username, 'custoptions': custoptions,'saleoptions': saleoptions,
                               'trade_list': trade_list,'pagelist':pagelist,
                               'saleid':saleid,'custid':custid,'cstime':cstime,'cetime':cetime,
                               })

            if worktype == '导出':
                xlsname = webuser_query.Username + '.xls'
                xlstitle = ['订单ID','销售人员姓名','订单生成时间','客户姓名','订单确认时间','财务人员','确认付款时间','发货人',
                            '出货时间','收货时间']
                ths_excel = outputexcel.outputexcel(filename=xlsname,title=xlstitle)
                for sef in ths_shoppingendflow:
                    linelist = [
                                str(sef.Sefflowid) , sef.sefsaleid.Username , datetimetostr(sef.sefcreatetime) , sef.sefuserid.Username,
                                datetimetostr(sef.sefsubmittime) , sef.sefpayname, datetimetostr(sef.sefpaytime), sef.sefsmname,
                                datetimetostr(sef.sefsmtime),datetimetostr(sef.SefFinishtime)
                                ]
                    ths_excel.writeline(linelist)

                xlsfile = ths_excel.Opworkbook()
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment;filename=%s'%xlsname
                bio = BytesIO()
                xlsfile.save(bio)
                bio.seek(0)
                response.write(bio.getvalue())
                return response


        return render(request, 'websiteoutputRade.html',
                  {'classes': classes, 'login_username': login_username,'custoptions':custoptions,'saleoptions':saleoptions,
                   'trade_list':trade_list,'pagelist':pagelist,
                   'saleid': saleid, 'custid': custid, 'cstime': cstime, 'cetime': cetime,
                   })



# 导出销售人员业绩
@login_required(login_url = '/login/')
def Website_outputsaleach(request):
    showmany = 10
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        ach_list = []
        pagelist = []

        if request.method == 'GET':
            if ths_rolename in ('管理员','管理人员','财务人员'):
                saleoptions = set([ sef.sefsaleid for sef in models.shoppingendflow.objects.all()])
            elif ths_rolename == '销售人员':
                saleoptions = set([ sef.sefsaleid for sef in models.shoppingendflow.objects.filter(sefsaleid=webuser_query)])
            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

            productoptions = set([ sfp.sefproductid for sfp in models.shoppingendflowproduct.objects.order_by('SefName') ])

            # 返回执行的工作类型,有两种,1. 查询 2.导出
            worktype =request.GET.get('worktype')
            saleid = request.GET.get('salename')
            productid = request.GET.get('product')
            cstime = request.GET.get('cstime')
            cetime = request.GET.get('cetime')

            try:
                page = int(request.GET.get('page'))
            except:
                page = 1

            if worktype:
                if ths_rolename == '销售人员':
                    saleid = webuser_query.id

                if cstime:
                    cstime_datetime = datetime.datetime.strptime(cstime, "%Y-%m-%d %H:%M")
                else:
                    cstime_datetime = datetime.date(2000, 1, 1)

                if cetime:
                    cetime_datetime = datetime.datetime.strptime(cetime, "%Y-%m-%d %H:%M")
                else:
                    cetime_datetime = datetime.date(2099, 1, 1)
                # 根据GET返回值进行查询,filter_str 为filter 查询中执行的语句
                filter_str = "shoppingendflowid__sefcreatetime__range=(cstime_datetime,cetime_datetime),"
                if saleid:
                    filter_str += "shoppingendflowid__sefsaleid=models.webuser.objects.get(id=int(saleid)),"
                if productid:
                    filter_str += "sefproductid=models.commodityinfo.objects.get(id=int(productid)),"

                ths_shoppingendflow = eval("models.shoppingendflowproduct.objects.filter(%s)"%filter_str)

                if worktype == "查询":
                    paginator = Paginator(ths_shoppingendflow, showmany)
                    try:
                        ach_list = paginator.page(page)
                    except :
                        ach_list = paginator.page(1)

                    pagelist = [i for i in paginator.page_range]

                if worktype == "导出":
                    xlsname = webuser_query.Username + '.xls'
                    xlstitle = ['订单ID', '销售人员姓名', '商品名称','单价','数量','总金额','订单生成时间', '收货时间']
                    ths_excel = outputexcel.outputexcel(filename=xlsname, title=xlstitle)
                    for sfp in ths_shoppingendflow:
                        linelist = [
                            str(sfp.shoppingendflowid.Sefflowid),sfp.shoppingendflowid.sefsaleid.Username,sfp.sefproductid.CommName,
                            sfp.SefunPrice,sfp.SefNum,sfp.SefunPrice * sfp.SefNum,
                            datetimetostr(sfp.shoppingendflowid.sefcreatetime),datetimetostr(sfp.shoppingendflowid.SefFinishtime)
                        ]
                        ths_excel.writeline(linelist)

                    xlsfile = ths_excel.Opworkbook()
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment;filename=%s' % xlsname
                    bio = BytesIO()
                    xlsfile.save(bio)
                    bio.seek(0)
                    response.write(bio.getvalue())
                    return response

            return render(request, 'websiteoutputsaleach.html',
                          {'classes': classes, 'login_username': login_username, 'productoptions': productoptions,'saleoptions': saleoptions,
                           'ach_list': ach_list,'pagelist':pagelist,
                           'saleid':saleid,'productid':productid,'cstime':cstime,'cetime':cetime,
                           })



# 导出销售产品流水表
@login_required(login_url = '/login/')
def Website_outputproductsale(request):
    showmany = 10
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        pagelist = []
        product_list = []

        if request.method == 'GET':
            if ths_rolename in ('管理员','管理人员','财务人员'):
                # 返回执行的工作类型,有两种,1. 查询 2.导出
                worktype = request.GET.get('worktype')
                productid = request.GET.get('product')
                cstime = request.GET.get('cstime')
                cetime = request.GET.get('cetime')

                try:
                    page = int(request.GET.get('page'))
                except:
                    page = 1

                productoptions = set([sfp.sefproductid for sfp in models.shoppingendflowproduct.objects.order_by('SefName')])

                if not worktype:
                    return render(request, 'websiteoutputproduct.html',
                              {'classes': classes, 'login_username': login_username, 'productoptions': productoptions,
                               'product_list': product_list, 'pagelist': pagelist,
                                'productid': productid, 'cstime': cstime, 'cetime': cetime,
                               })

                if cstime:
                    cstime_datetime = datetime.datetime.strptime(cstime, "%Y-%m-%d %H:%M")
                else:
                    cstime_datetime = datetime.date(2000, 1, 1)

                if cetime:
                    cetime_datetime = datetime.datetime.strptime(cetime, "%Y-%m-%d %H:%M")
                else:
                    cetime_datetime = datetime.date(2099, 1, 1)

                # 根据GET返回值进行查询,filter_str 为filter 查询中执行的语句
                filter_str = "shoppingendflowid__sefcreatetime__range=(cstime_datetime,cetime_datetime),"
                if productid:
                    filter_str += "sefproductid=models.commodityinfo.objects.get(id=int(productid)),"
                ths_sefproduct = eval("models.shoppingendflowproduct.objects.filter(%s)"%filter_str)

                if worktype == '查询':
                    paginator = Paginator(ths_sefproduct, showmany)
                    try:
                        product_list = paginator.page(page)
                    except :
                        product_list = paginator.page(1)

                    pagelist = [i for i in paginator.page_range]

                if worktype == "导出":
                    xlsname = webuser_query.Username + '.xls'
                    xlstitle = ['订单ID', '商品名称', '规格ID','单位','厚度','尺寸','环保等级', '每件数量','单价','数量','总金额',
                                '订单生成时间','收货时间']
                    ths_excel = outputexcel.outputexcel(filename=xlsname, title=xlstitle)
                    for sfp in ths_sefproduct:
                        linelist = [
                            str(sfp.shoppingendflowid.Sefflowid),sfp.sefproductid.CommName,sfp.sefdetailid.id,sfp.sefUnit,sfp.sefthick,
                            sfp.sefSize,sfp.sef_Protlevel,sfp.SefUnmun,
                            sfp.SefunPrice,sfp.SefNum,sfp.SefunPrice * sfp.SefNum,
                            datetimetostr(sfp.shoppingendflowid.sefcreatetime),datetimetostr(sfp.shoppingendflowid.SefFinishtime)
                        ]
                        ths_excel.writeline(linelist)

                    xlsfile = ths_excel.Opworkbook()
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment;filename=%s' % xlsname
                    bio = BytesIO()
                    xlsfile.save(bio)
                    bio.seek(0)
                    response.write(bio.getvalue())
                    return response


                return render(request, 'websiteoutputproduct.html',
                              {'classes': classes, 'login_username': login_username, 'productoptions': productoptions,
                               'product_list': product_list, 'pagelist': pagelist,
                                'productid': productid, 'cstime': cstime, 'cetime': cetime,
                               })

            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})


@login_required(login_url = '/login/')
def Website_outputproducttotal(request):
    showmany = 10
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        pagelist = []
        product_list = []

        if request.method == 'GET':
            if ths_rolename in ('管理员','管理人员','财务人员',"出货人员","销售人员"):
                # 返回执行的工作类型,有两种,1. 查询 2.导出
                worktype = request.GET.get('worktype')
                product_name = request.GET.get('product')
                cstime = request.GET.get('cstime')
                cetime = request.GET.get('cetime')
                if not worktype:
                    return render(request, 'websiteoutputptotal.html',
                              {'classes': classes, 'login_username': login_username,
                               'product_list': product_list, 'pagelist': pagelist,
                                'product_name':product_name,'cstime': cstime, 'cetime': cetime,
                               })

                try:
                    page = int(request.GET.get('page'))
                except:
                    page = 1

                if cstime:
                    cstime_datetime = datetime.datetime.strptime(cstime, "%Y-%m-%d %H:%M")
                else:
                    cstime_datetime = datetime.date(2000, 1, 1)

                if cetime:
                    cetime_datetime = datetime.datetime.strptime(cetime, "%Y-%m-%d %H:%M")
                else:
                    cetime_datetime = datetime.date(2099, 1, 1)

                filter_str = "shoppingendflowid__sefcreatetime__range=(cstime_datetime,cetime_datetime),"
                if product_name:
                    filter_str += "SefName__icontains=product_name"
                ths_ptotal = eval("models.shoppingendflowproduct.objects.filter(%s)"%filter_str)

                ptotal_group = ths_ptotal.values('SefName','sefdetailid','sefUnit','sefthick','sefSize','sef_Protlevel','SefUnmun').annotate(
                    total_price=Sum('SefPrice'),total_num=Sum('SefNum'))

                if worktype == "查询":
                    paginator = Paginator(ptotal_group, showmany)

                    try:
                        product_list = paginator.page(page)
                    except:
                        product_list = paginator.page(1)

                    pagelist = [i for i in paginator.page_range]
                    return render(request, 'websiteoutputptotal.html',
                          {'classes': classes, 'login_username': login_username,
                           'product_list': product_list, 'pagelist': pagelist,
                           'product_name': product_name, 'cstime': cstime, 'cetime': cetime,
                           })


                if worktype == '导出':
                    xlsname = webuser_query.Username + '.xls'
                    xlstitle = ['商品名称', '规格ID','单位','厚度','尺寸','环保等级', '每件数量',
                                '总销量','总收入']
                    ths_excel = outputexcel.outputexcel(filename=xlsname, title=xlstitle)
                    for pg in ptotal_group:
                        linelist = [
                            pg['SefName'],pg['sefdetailid'],pg['sefUnit'],pg['sefthick'],pg['sefSize'],pg['sef_Protlevel'],pg['SefUnmun'],
                            pg['total_num'],pg['total_price']
                        ]
                        ths_excel.writeline(linelist)

                    xlsfile = ths_excel.Opworkbook()
                    response = HttpResponse(content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = 'attachment;filename=%s' % xlsname
                    bio = BytesIO()
                    xlsfile.save(bio)
                    bio.seek(0)
                    response.write(bio.getvalue())
                    return response

            else:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})


# 商品管理页面
@login_required(login_url = '/login/')
def Website_adminproduct(request,productid):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    productclassid = productname = message = ""

    if ths_rolename == "客户":
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

    # 有Productid ,单个商品管理
    if productid:
        pclass_options = models.commodityclass.objects.all()
        pinfo = models.commodityinfo.objects.get(id=int(productid))
        pdetails = models.commditydetail.objects.filter(Commid=pinfo)
        isrule = models.userrule.objects.get(Userid=webuser_query).ModCommodity

        if not isrule:
            return render(request, 'sitemessage.html',
                          {'classes': classes, 'login_username': login_username,
                           'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

        # 获取页面
        if request.method == 'GET':
            return render(request, 'websiteshowproduct.html',
                      {'classes': classes, 'login_username': login_username,
                       'productid':productid,'pclass_options':pclass_options,'pinfo':pinfo,'pdetails':pdetails
                       })

        # 保存商品信息
        if request.method == 'POST':
            postpclass = request.POST.get('productclass')
            postpname = request.POST.get('pname')
            postpimg = request.FILES.get('pimg')
            postpinfo = request.FILES.get('pinfo')
            postlogistics = request.FILES.get('logistics')
            postreport = request.FILES.get('report')

            oldfile = []

            if postpclass:
                pinfo.Commclass = models.commodityclass.objects.get(id=int(postpclass))

            if postpname:
                pinfo.CommName = postpname

            if postpimg:
                # 把旧文件路径记录下来,等数据库更新后删掉
                oldimg = str(pinfo.Commimg)
                img_uploadpath = "HdWxShop/static/commodityimg/"
                img_path = uploadfile(postpimg,img_uploadpath)
                pinfo.Commimg = img_path
                oldfile.append(oldimg)

            if postpinfo:
                oldinfo = str(pinfo.CommInfo)
                info_uploadpath = "HdWxShop/static/commodityinfo/"
                img_info = uploadfile(postpinfo,info_uploadpath)
                pinfo.CommInfo = img_info
                oldfile.append(oldinfo)

            if postlogistics:
                oldlogistics = str(pinfo.logisticsimg)
                logistics_uploadpath = "HdWxShop/static/commodityinfo/"
                img_logistics = uploadfile(postlogistics,logistics_uploadpath)
                pinfo.logisticsimg = img_logistics
                oldfile.append(oldlogistics)

            if postreport:
                oldreport = str(pinfo.reportimg)
                report_uploadpath = "HdWxShop/static/commodityinfo/"
                img_report = uploadfile(postreport,report_uploadpath)
                pinfo.reportimg = img_report
                oldfile.append(oldreport)

            pinfo.save()
            # 删除旧文件
            for file in oldfile:
                try:
                    os.remove(file)
                except:
                    continue

            message = "商品信息已修改成功"
            return render(request, 'websiteshowproduct.html',
                      {'classes': classes, 'login_username': login_username,
                       'productid':productid,'pclass_options':pclass_options,'pinfo':pinfo,'pdetails':pdetails,
                       'message':message
                       })

    # 没有productid , 商品管理展示列表
    else:
        product_list = []
        productclassid = request.GET.get('productclass')
        productname = request.GET.get('productname')
        try:
            page = int(request.GET.get('page'))
        except:
            page = 1

        if productclassid or productname:
            filterstr = ""
            if productclassid and productclassid != "None":
                filterstr += "Commclass=models.commodityclass.objects.get(id=int(productclassid)),"
            if productname and productname != "None" :
                filterstr += "CommName__icontains=productname,"
            product_list = eval("models.commodityinfo.objects.filter(%s)"%filterstr)
        else:
            product_list = models.commodityinfo.objects.all()

        paginator = Paginator(product_list, showmany)
        try:
            product_list = paginator.page(page)
        except:
            product_list = paginator.page(1)
        pagelist = [ i for i in paginator.page_range ]
        return render(request, 'websiteadminproduct.html',
                      {'classes': classes, 'login_username': login_username,
                       'product_list':product_list,'pagelist':pagelist,
                        'productclassid':productclassid,'productname':productname,
                       'message':message
                       })


# 添加商品界面
@login_required(login_url = '/login/')
def Website_addproduct(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    ths_userule = models.userrule.objects.get(Userid=webuser_query)
    addproduct_rule = ths_userule.AddCommodity
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    message = ""

    if ths_rolename == "客户" or not addproduct_rule:
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

    if request.method == "GET":
        return render(request, 'websiteaddproduct.html',
                      {'classes': classes, 'login_username': login_username,
                       'message':message
                       })


    if request.method == "POST":
        postpclass = request.POST.get('productclass')
        postpname = request.POST.get('pname')
        postpimg = request.FILES.get('pimg')
        postpinfo = request.FILES.get('pinfo')

        ths_class = models.commodityclass.objects.get(id=int(postpclass))

        img_uploadpath = "HdWxShop/static/commodityimg/"
        img_path = uploadfile(postpimg, img_uploadpath)

        info_uploadpath = "HdWxShop/static/commodityinfo/"
        img_info = uploadfile(postpinfo, info_uploadpath)

        ths_product = models.commodityinfo(Commclass=ths_class,CommName=postpname,Commimg=img_path,CommInfo=img_info)
        ths_product.save()

        return HttpResponseRedirect('website/adminproduct/' + str(ths_product.id))


# 管理主页推荐商品
@login_required(login_url = '/login/')
def Website_admincommend(request):
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    ths_userule = models.userrule.objects.get(Userid=webuser_query)
    # addproduct_rule = ths_userule.AddCommodity
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    allproduct = models.commodityinfo.objects.all()


    if ths_rolename == "客户":
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})

    return render(request,'admincommend.html',locals())


# 用户管理界面
@login_required(login_url = '/login/')
def Website_adminuser(request,userid):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    message = ""
    userlist = []

    if ths_rolename == "管理员" or ths_rolename == "管理人员":
        # 判断是否是超级管理员
        if webuser_query == static_superadmin_username:
            issuperadmin = True
        else:
            issuperadmin = False
        # 角色选项
        role_options = models.userrole.objects.all()
        modrule = userule.ModRule
        if userid:
            ths_user = models.webuser.objects.get(id=int(userid))
            sale_options = models.userrule.objects.filter(Roleid=models.userrole.objects.get(Rolename="销售人员"))
            commodity_options = models.commodityinfo.objects.all()
            if not modrule:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,您没有权限修改.'})

            ths_userbind = models.userbind.objects.get(userid=ths_user)
            ths_userrule = models.userrule.objects.get(Userid=ths_user)
            ths_commprice = models.custcommprice.objects.filter(Cpuserid=ths_user)
            ths_usercommprice = models.custcommprice.objects.filter(Cpuserid=ths_user)
            ths_userrulename = ths_userrule.Roleid.Rolename


            if ths_userrulename == "客户":
                ths_iscust = True
                try:
                    ths_usersale = models.custsalebind.objects.get(Customerid=ths_user)
                except:
                    ths_usersale = False
            else:
                ths_iscust = False
                ths_usersale = False

            if request.method == "GET":
                    return render(request, 'websiteshowuser.html',
                              {'classes': classes, 'login_username': login_username,
                               'ths_user':ths_user,'sale_options':sale_options,'ths_usercommprice':ths_usercommprice,'commodity_options':commodity_options,
                               'role_options': role_options,'ths_userbind':ths_userbind,'ths_userrule':ths_userrule,'ths_commprice':ths_commprice,
                               'issuperadmin': issuperadmin,
                               'message': message,'ths_iscust':ths_iscust,'ths_usersale':ths_usersale,
                               })

            # 保存用户信息
            if request.method == "POST":
                if modrule:
                    post_userrule = request.POST.get('userrule')
                    post_userstatus = request.POST.get('userstatus')
                    post_userphone = request.POST.get('userphone')
                    post_useraddress = request.POST.get('useraddress')
                    post_usercust = request.POST.get('usercust')

                    if post_userrule and post_userrule != "None":
                        ths_userrule.Roleid = models.userrole.objects.get(id=int(post_userrule))
                    if post_userstatus and post_userstatus != "None":
                        ths_user.Userstatus = int(post_userstatus)
                    if post_userphone and post_userphone != "None":
                        ths_userbind.Userphone = post_userphone
                    else:
                        ths_userbind.Userphone = ""
                    if post_useraddress and post_useraddress != "None":
                        ths_userbind.UserAddress = post_useraddress
                    else:
                        ths_userbind.UserAddress = ""
                    if post_usercust and post_usercust != "None":
                        try:
                            ths_usercust = models.custsalebind.objects.get(Customerid=ths_user)
                            ths_usercust.Saleid = models.webuser.objects.get(id=int(post_usercust))
                        except:
                            ths_usercust = models.custsalebind(
                                Customerid=ths_user,Saleid=models.webuser.objects.get(id=int(post_usercust)))

                        ths_usercust.save()
                    ths_userbind.save()
                    ths_userrule.save()
                    ths_user.save()

                    return render(request, 'websiteshowuser.html',
                              {'classes': classes, 'login_username': login_username,
                               'ths_user':ths_user,'sale_options':sale_options,'ths_usercommprice':ths_usercommprice,'commodity_options':commodity_options,
                               'role_options': role_options,'ths_userbind':ths_userbind,'ths_userrule':ths_userrule,'ths_commprice':ths_commprice,
                               'issuperadmin': issuperadmin,
                               'message': message,'ths_iscust':ths_iscust,'ths_usersale':ths_usersale,
                               })

                else:
                    return render(request, 'sitemessage.html',
                                  {'classes': classes, 'login_username': login_username,
                                   'messagetype': 'danger', 'message': '对不起,您没有权限修改.'})


        else:
            if request.method == "GET":
                Get_ruleid = request.GET.get('rulename')
                Get_username = request.GET.get('username')
                rulelist = models.userrule.objects.all()
                filterstr = ''
                try:
                    page = int(request.GET.get('page'))
                except:
                    page = 1
                if Get_ruleid and Get_ruleid != 'None':
                    filterstr += "Roleid=models.userrole.objects.get(id=int(Get_ruleid)),"
                if Get_username and Get_username != 'None':
                    filterstr += "Userid__Username__icontains=Get_username,"
                rulelist = eval("rulelist.filter(%s)"%filterstr)

                paginator = Paginator(rulelist, showmany)
                try:
                    rule_list = paginator.page(page)
                except:
                    rule_list = paginator.page(1)

                pagelist = [i for i in paginator.page_range]
                return render(request, 'websiteadminuser.html',
                              {'classes': classes, 'login_username': login_username,
                               'role_options': role_options, 'rule_list':rule_list,'pagelist':pagelist,
                               'message': message,'ruleid':Get_ruleid,'username':Get_username,
                               })
    # 非管理员无法访问
    else:
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})


# 新闻信息管理展示
@login_required(login_url='/login/')
def Website_newsadmin(request,newsid):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)
    message = ""

    isadminnews = userule.ReleaseNew
    newsclass_options = models.newsclass.objects.all()
    if isadminnews:
        if request.method == "GET":
            if not newsid:
                return render(request,'websiteadminnews.html',
                               {'classes': classes, 'login_username': login_username,
                                'message':message,
                                'newsclass_options':newsclass_options
                                }
                               )
            else:
                newsinfo = models.newsinfo.objects.get(id=int(newsid))
                return render(request,'websiteshowadminnews.html',{'classes': classes, 'login_username': login_username,
                                                              'newsclass_options': newsclass_options,
                                                              'newsinfo':newsinfo
                                                              }
                              )
        if request.method == "POST":
            if newsid:
                newstitle = request.POST.get('newstitle')
                newsclass = request.POST.get('newsclass')
                newsbody  = request.POST.get('newsbody')
                newsabstract = request.POST.get('newsabstract')
                newsimage = request.FILES.get('newsimage')
                newsinfo_query = models.newsinfo.objects.get(id=int(newsid))

                if newsimage:
                    old_newsimage = str(newsinfo_query.Newsabstract)
                    image_suffix = newsimage.name.split('.')[1]
                    image = Image.open(newsimage)
                    # 转换图片大小
                    image.thumbnail((220, 150), Image.ANTIALIAS)
                    uploadpath = 'media/newsimage/'
                    newimagename = str(uuid.uuid1())
                    savepath = settings.MEDIA_ROOT + '/newsimage/' + newimagename + "." + image_suffix
                    image.name = newimagename + "." + image_suffix
                    newsimage_path = os.path.join(uploadpath,newimagename) + "." + image_suffix
                    image.save(savepath, "jpeg")
                    # newsimage_path = uploadfile(newsimage,uploadpath)
                    newsinfo_query.Newsimage = newsimage_path
                    try:
                        os.remove(old_newsimage)
                    except:
                        pass

                newsinfo_query.Newsclassid = models.newsclass.objects.get(id=int(newsclass))
                newsinfo_query.Newstitle = newstitle
                newsinfo_query.Newsabstract = newsabstract
                newsinfo_query.Newsbody = newsbody
                newsinfo_query.save()
                message = "<div id='myAlert' class='alert alert-success'><a href='#' class='close' data-dismiss='alert'>&times;</a><p><strong>修改成功!</strong></p></div>"
                return render(request, 'websiteadminnews.html',
                              {'classes': classes, 'login_username': login_username,
                               'message': message,
                               'newsclass_options': newsclass_options
                               }
                              )
    else:
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})


# 添加新闻信息
@login_required(login_url = '/login/')
def Website_addnews(request):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)
    message = ""

    isadminnews = userule.ReleaseNew
    newsclass_options = models.newsclass.objects.all()
    if isadminnews:
        if request.method == "GET":
            return render(request, 'websiteshowadminnews.html', {'classes': classes, 'login_username': login_username,
                                                                 'newsclass_options': newsclass_options,
                                                                 'newsinfo': ""
                                                                 })
        if request.method == "POST":
            newstitle = request.POST.get('newstitle')
            newsclass = request.POST.get('newsclass')
            newsabstract = request.POST.get('newsabstract')
            newsimage = request.FILES.get('newsimage')
            newsbody = request.POST.get('newsbody')

            if newsimage:
                image_suffix = newsimage.name.split('.')[1]
                image = Image.open(newsimage)
                # 转换图片大小
                image.thumbnail((220, 150), Image.ANTIALIAS)
                uploadpath = 'media/newsimage/'
                newimagename = str(uuid.uuid1())
                savepath = settings.MEDIA_ROOT + '/newsimage/' + newimagename + "." + image_suffix
                image.name = newimagename + "." + image_suffix
                newsimage_path = os.path.join(uploadpath, newimagename) + "." + image_suffix
                image.save(savepath, "jpeg")
            else:
                newsimage_path = ""

            models.newsinfo.objects.create(
                Newsclassid=models.newsclass.objects.get(id=int(newsclass)),
                Newstitle=newstitle,
                Newsbody=newsbody,
                Newsabstract = newsabstract,
                Newsimage = newsimage_path,
            )
            message = "<div id='myAlert' class='alert alert-success'><a href='#' class='close' data-dismiss='alert'>&times;</a><p><strong>保存成功!</strong></p></div>"
            return render(request, 'websiteadminnews.html',
                          {'classes': classes, 'login_username': login_username,
                           'message': message,
                           'newsclass_options': newsclass_options
                           }
                          )
    else:
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})


# 销售人员管理界面
@login_required(login_url = '/login/')
def Website_saleadmin(request,custid):
    showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    login_username = request.user.username
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    message = ""

    if ths_rolename == "销售人员":
        if custid:
            ths_webuser = models.webuser.objects.get(id=int(custid))
            # 用来检测是不是登录用户的客户
            ismycust = models.custsalebind.objects.filter(Customerid=ths_webuser,Saleid=webuser_query)
            commodity_options = models.commodityinfo.objects.all()

            if not ismycust:
                return render(request, 'sitemessage.html',
                              {'classes': classes, 'login_username': login_username,
                               'messagetype': 'danger', 'message': '对不起,这不是您的客户.'})

            ths_userinfo = models.userbind.objects.get(userid=ths_webuser)
            ths_userprice = models.custcommprice.objects.filter(Cpuserid=ths_webuser)

            return render(request, 'websiteshowsaleadmin.html',
                          {'classes': classes, 'login_username': login_username,'custid':custid,
                           'ths_webuser':ths_webuser,'ths_userinfo':ths_userinfo,'ths_userprice':ths_userprice,
                           'commodity_options':commodity_options,
                           'message': message,
                           })

        else:
            custoptions = models.userrule.objects.filter(Userid__in=
                          models.webuser.objects.exclude(id__in=
                          models.custsalebind.objects.all().values_list('Customerid')).values_list('id'),
                                                         Roleid__Rolename="客户")

            username = request.GET.get('username')
            if username and username != "None":
                mycust_list = models.custsalebind.objects.filter(Saleid=webuser_query,
                                                                 Customerid__Username__contains = username)
            else:
                mycust_list = models.custsalebind.objects.filter(Saleid=webuser_query)
            paginator = Paginator(mycust_list, showmany)
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            try:
                cust_list = paginator.page(page)
            except:
                cust_list = paginator.page(1)
            pagelist = [ i for i in paginator.page_range ]

            return render(request, 'websitesaleadmin.html',
                          {'classes': classes, 'login_username': login_username,
                           'cust_list':cust_list,'custoptions':custoptions,
                           'custid':custid,'username':username,
                           'pagelist':pagelist,'message': message,
                           })

    else:
        return render(request, 'sitemessage.html',
                      {'classes': classes, 'login_username': login_username,
                       'messagetype': 'danger', 'message': '对不起,您没有权限访问.'})



# 获取主页商品信息
def freshen_indexcominfo(request):
    # 主页商品信息dict
    returndict = {}
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
    else:
        webuser_query = False
    indexcommodity = models.indexshowcommodity.objects.all()
    for aclass in indexcommodity:
        returndict[aclass.indexclass.CclassName] = []
        showtotal = int(aclass.showmany)
        products = models.commodityinfo.objects.filter(Commclass=aclass.indexclass)
        for product in products:
            details = models.commditydetail.objects.filter(Commid=product)
            for detail in details:
                if webuser_query:
                    try:
                        unprice = models.custcommprice.objects.get(Cpuserid=webuser_query,Cpcommid=detail).CpunPrice
                    except:
                        unprice = detail.CodunPrice
                    collectcount = models.custcollect.objects.filter(CcUserid=webuser_query,CcCommid=detail).count()
                    if collectcount > 0 :
                        iscollect = 1
                    else:
                        iscollect = 0
                else:
                    iscollect = 0
                    unprice = detail.CodunPrice
                returndict[aclass.indexclass.CclassName].append({
                    'product': product.CommName,
                    'detailid': detail.id,
                    'dunit':detail.CodUnit,
                    'thick':detail.Codthick,
                    'disize':detail.CodSize,
                    'protlevel':detail.Cod_Protlevel,
                    'unprice':unprice,
                    'inventory':detail.Codinventory,
                    'unmun':detail.CodUnmun,
                    'brand':detail.Codbrand,
                    'pimg':str(product.Commimg).replace("HdWxShop",""),
                    'iscollect':iscollect
                })
        # 根据规定数量截取大小
        returndict[aclass.indexclass.CclassName] = returndict[aclass.indexclass.CclassName][:showtotal]
    return JsonResponse(returndict)


# 刷新推荐商品
def fresh_commend(request):
    commendlist = []
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
    else:
        webuser_query = False
    commendquery = models.indexcommend.objects.all().order_by('commendidx')
    for acommend in commendquery:
        acommend_detail = acommend.commenddetail
        acommend_product = acommend_detail.Commid
        acommend_classes = acommend_product.Commclass
        # 有登录情况下
        if webuser_query:
            try:
                userprice = models.custcommprice.objects.get(Cpuserid=webuser_query,Cpcommid=acommend_detail).CpunPrice
            except:
                userprice = acommend_detail.CodunPrice
            collectcount = models.custcollect.objects.filter(CcUserid=webuser_query, CcCommid=acommend_detail).count()
            if collectcount > 0:
                iscollect = 1
            else:
                iscollect = 0
        # 没登录
        else:
            userprice = acommend_detail.CodunPrice
            iscollect = 0

        commendlist.append({
                    'classes': acommend_classes.CclassName,
                    'product': acommend_product.CommName,
                    'func':acommend_detail.Codfunction,
                    'detailid': acommend_detail.id,
                    'dunit':acommend_detail.CodUnit,
                    'thick':acommend_detail.Codthick,
                    'disize':acommend_detail.CodSize,
                    'protlevel':acommend_detail.Cod_Protlevel,
                    'unprice':userprice,
                    'inventory':acommend_detail.Codinventory,
                    'unmun':acommend_detail.CodUnmun,
                    'brand':acommend_detail.Codbrand,
                    'pimg':str(acommend_product.Commimg).replace("HdWxShop",""),
                    'iscollect':iscollect
        })

    if len(commendlist) > 0:
        code = 1
    else:
        code = 0
    return render(request,"freshen_commend.html",{
        'code':code,
        'commend':commendlist,
    })


# 动态获取商品信息
def freshen_shop(request):
    showmany = 5

    return_list = []
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
    else:
        webuser_query = False

    # 前端返回信息
    page = request.POST.get('page')
    search = request.POST.get('search')
    pcls = request.POST.get('pcls')
    psize = request.POST.get('psize')
    thick = request.POST.get('thick')
    protlevel = request.POST.get('protlevel')
    brand = request.POST.get('brand')
    function_value = request.POST.get('function')
    orderby = request.POST.get('orderby')
    orderasc = request.POST.get('asc')

    session_key = "shopinfo#" + str(request.session.session_key)
    session_value = "&page=%s&search=%s&pcls=%s&psize=%s&thick=%s&protlevel=%s&brand=%s&function_value=%s&orderby=%s&orderasc=%s&"%(page,search,pcls,psize,thick,protlevel,brand,function_value,orderby,orderasc)
    print("set:%s"%session_value)
    session_value = session_value.replace("None","")
    cache.set(session_key,session_value,3600)

    filterstr = ""
    # 一些筛选条件
    if search and search != 'None':
        filterstr += "Commid__CommName__icontains=search,"
    if pcls and pcls != "None":
        filterstr += "Commid__Commclass=models.commodityclass.objects.get(id=int(pcls)),"
    if psize and psize != "None":
        filterstr += "CodSize=psize,"
    if thick and thick != "None":
        filterstr += "Codthick=thick,"
    if protlevel and protlevel != "None":
        filterstr += "Cod_Protlevel=protlevel,"
    if brand and brand != "None":
        filterstr += "Codbrand=brand,"
    if function_value and function_value != "None":
        filterstr += "Codfunction=function_value,"

    details = eval("models.commditydetail.objects.filter(%s)"%filterstr)

    for detail in details:
        product = detail.Commid
        if webuser_query:
            try:
                unprice = models.custcommprice.objects.get(Cpuserid=webuser_query, Cpcommid=detail).CpunPrice
            except:
                unprice = detail.CodunPrice
            collectcount = models.custcollect.objects.filter(CcUserid=webuser_query, CcCommid=detail).count()
            if collectcount > 0:
                iscollect = 1
            else:
                iscollect = 0
        else:
            unprice = detail.CodunPrice
            iscollect = 0

        return_list.append({
            'clsname':product.Commclass.CclassName,
            'product': product.CommName,
            'detailid': detail.id,
            'dunit': detail.CodUnit,
            'thick': detail.Codthick,
            'dsize': detail.CodSize,
            'protlevel': detail.Cod_Protlevel,
            'unprice': unprice,
            'inventory': detail.Codinventory,
            'unmun': detail.CodUnmun,
            'brank':detail.Codbrand,
            'pimg': str(product.Commimg).replace("HdWxShop", ""),
            'iscollect': iscollect
        })

    if orderby == "unprice":
        if orderasc == "2":
            return_list = cwhAlgorithm.json_quicksort(return_list, "unprice","2")
        else:
            return_list = cwhAlgorithm.json_quicksort(return_list, "unprice")

    return_list = Paginator(return_list, showmany)
    try:
        page = int(page)
    except:
        page = 1
    details_Paginator = return_list.page(page)
    pagelist = [i for i in return_list.page_range]

    return render(request,"shopinfo2.html",{"return_list":details_Paginator,
                                           "page":page,
                                           "search":search,
                                           "pcls":pcls,
                                           "psize":psize,
                                           "thick":thick,
                                           "protlevel":protlevel,
                                            "orderby":orderby,
                                            "orderasc":orderasc,
                                            "details":details,'pagelist':pagelist,'details_Paginator':details_Paginator,
                                    })


# 销售人员界面获取客户单价
@login_required(login_url = '/login/')
def freshen_taprice(request):
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)
    ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
    dict_custprice = []
    custprice = []

    custid = request.POST.get('custid')
    ths_webuser = models.webuser.objects.get(id=int(custid))
    # 如果是销售人员,先检测下是不是
    if ths_rolename == "销售人员":
        # 用来检测是不是登录用户的客户
        ismycust = models.custsalebind.objects.filter(Customerid=ths_webuser, Saleid=webuser_query)
        if ismycust:
            custprice = models.custcommprice.objects.filter(Cpuserid=ths_webuser)

    elif ths_rolename == "管理员" or ths_rolename == "管理人员":
        custprice = models.custcommprice.objects.filter(Cpuserid=ths_webuser)

    for acustprice in custprice:
        dict_custprice.append({
            'cpid':acustprice.id,                                      # 客户价格表id
            'pname':acustprice.Cpcommid.Commid.CommName,               # 商品名称
            'custprice':acustprice.CpunPrice,                          # 客户单价
            'unit':acustprice.Cpcommid.CodUnit,                        # 规格
            'thick':acustprice.Cpcommid.Codthick,
            'psize':acustprice.Cpcommid.CodSize,
            'protlevel':acustprice.Cpcommid.Cod_Protlevel,
            'unprice':acustprice.Cpcommid.CodunPrice,
            'inventory':acustprice.Cpcommid.Codinventory,
            'unmun':acustprice.Cpcommid.CodUnmun,
            })
    return JsonResponse({'Msg':'succ','data':dict_custprice})



# 新闻信息管理展示
@login_required(login_url='/login/')
def fresh_newsinfo(request):
    showmany = 5
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)

    isadminnews = userule.ReleaseNew
    if isadminnews:
        if request.method == "POST":
            try:
                page = int(request.POST.get('page'))
            except:
                page = 1
            newscls = request.POST.get('newscls')
            search_value = request.POST.get('search_value')
            filter_str = ""

            if search_value and search_value != 'None':
                filter_str += "Newstitle__icontains=search_value,"
            if newscls and newscls != "None":
                filter_str += "Newsclassid=models.newsclass.objects.get(id=int(newscls)),"

            news_list = eval("models.newsinfo.objects.filter(%s)"%filter_str)
            paginator = Paginator(news_list, showmany)
            try:
                newslist = paginator.page(page)
            except:
                newslist = paginator.page(1)

            pagelist = [i for i in paginator.page_range]

            return render(request,'freshen_newsadmin.html',{
                'newslist':newslist,
                'pagelist':pagelist
            })


# 刷新客户需要处理的订单
def fresh_userflow(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        flowlist = []
        usershoppingflow = models.shoppingflow.objects.filter(SfUserid=webuser_query,Sfstatus__in=[3,4,6])
        for aflow in usershoppingflow:
            totalprice = sum([ afp.sfpsumprice for afp in models.shoppingflowproduct.objects.filter(shoppingflowid=aflow) ])
            flowlist.append({
                'flowinfo':aflow,
                 'total':totalprice,
            })
        return render(request,'refresh_userflow.html',{
            'flowlist':flowlist,
        })


# 用户点开订单详情时,刷新商品使用的页面
def refreshen_userflowproduct(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        flowid = request.POST.get('flowid')
        try:
            myflow = models.shoppingflow.objects.get(id=int(flowid),SfUserid=webuser_query)
        except:
            return
        myflowproduct = models.shoppingflowproduct.objects.filter(shoppingflowid=myflow)
        return render(request,'refreshen_myflowproduct.html',{
            'myflowproduct':myflowproduct,
        })


# 查看客户收藏信息
def refreshen_tacollect(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        ths_rolename = models.userrule.objects.get(Userid=webuser_query).Roleid.Rolename
        custid = int(request.POST.get('custid'))
        cust_query = models.webuser.objects.get(id=custid)
        # 销售人员判断到不是自己的客户,返回 0
        if ths_rolename == "销售人员":
            if models.custsalebind.objects.filter(Customerid=cust_query,Saleid=webuser_query).count() < 1:
                return JsonResponse({'rcode':0})
        # 判断不是管理员,返回0
        elif ths_rolename != "管理员" and ths_rolename != "管理人员":
            return JsonResponse({'rcode': 0})

        custcollect_list = []
        custcollects = models.custcollect.objects.filter(CcUserid=cust_query)
        for acollect in custcollects:
            custcollect_list.append({
                'pid':acollect.CcCommid.id,
                'pname':acollect.CcCommid.Commid.CommName,
                'detail':str(acollect.CcCommid),
                'cdate':str(acollect.CollectDate)
            })

        return JsonResponse({'rcode':1,'collectlist':custcollect_list})
    else:
        return JsonResponse({'rcode':99})


# 刷新订单管理左边
def fresh_businessleft(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        ths_rule = models.userrule.objects.get(Userid=webuser_query)
        ths_rolename = ths_rule.Roleid.Rolename
        businesslist = []
        searchlist = []
        # 客户不能访问,直接返回0
        if ths_rolename == "客户":
            return JsonResponse({'rcode':0})

        searchlist.append({
            'name':'<span class="glyphicon glyphicon-paste"></span>&nbsp&nbsp历史交易信息',
            'link':'/website/outputtrade/'
        })

        if ths_rolename == "销售人员":
            businesslist.append({'name':'<span class="glyphicon glyphicon glyphicon-link"></span>&nbsp&nbsp我的客户',
                             'link':'/website/saleadmin/'
                             })
        if ths_rolename == "管理员" or ths_rolename == "管理人员":
            businesslist.append({
                'name':'<span class="glyphicon glyphicon-user"></span>&nbsp&nbsp用户管理</a>',
                'link':'/website/adminuser/'
            })
        if ths_rolename != "出货人员":
            searchlist.append({
                'name':'<span class="glyphicon glyphicon-paste"></span>&nbsp&nbsp销售人员业绩',
                'link':'/website/outputsaleach/'
            })
        searchlist.append({
            'name':'<span class="glyphicon glyphicon-paste"></span>&nbsp&nbsp产品汇总',
            'link':'/website/outputproducttotal'
        })
        businesslist.append({
            'name':'<span class="glyphicon glyphicon-list-alt"></span>&nbsp&nbsp订单管理',
            'link':'/website/adminflow/'
        })
        if ths_rule.AddCommodity or ths_rule.ModCommodity:
            businesslist.append({
                'name':'<span class="glyphicon glyphicon-briefcase"></span>&nbsp&nbsp商品管理</a>',
                'link':'/website/adminproduct/'
            })
        if ths_rule.ReleaseAdv or ths_rule.ReleaseNew:
            businesslist.append({
                'name':'<span class="glyphicon glyphicon-calendar"></span>&nbsp&nbsp新闻管理',
                'link':'/website/adminnews/'
            })
        businesslist.append({
            'name':'<span class="glyphicon glyphicon-inbox"></span>&nbsp&nbsp主页商品',
            'link':'/website/admincommend/'
        })
        if ths_rolename == "管理员" or ths_rolename == "管理人员" or ths_rolename == "财务人员":
            searchlist.append({
                'name':'<span class="glyphicon glyphicon-paste"></span>&nbsp&nbsp产品流水',
                'link':'/website/outputproductsale'
            })
        return JsonResponse({'rcode':1,'businesslist':businesslist,'searchlist':searchlist})
    else:
        return JsonResponse({'rcode':99})


# 刷新购物车数量
def fresh_shoppingcartAmount(request):
    amount = 0
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        myshoppingcart = models.shoppingcart.objects.filter(ScUserid=webuser_query)
        amount = myshoppingcart.count()
    return JsonResponse({'amount':amount})


# 刷新我的地址
def freshen_myaddress(request):
    if request.user.is_authenticated():
        webuser_query = outputwebuser(request)
        address_list = models.useraddress.objects.filter(userid=webuser_query)
        return render(request, 'freshen_myaddress.html', {
            'address_list':address_list
        })


@csrf_exempt
def kindeditor_upload(request):
    result = {'error': 1, 'message': '上传出错'}
    webuser_query = outputwebuser(request)
    userule = models.userrule.objects.get(Userid=webuser_query)

    isadminnews = userule.ReleaseNew
    if isadminnews:
        files = request.FILES.get('imgFile', None)
        if files:
            allow_suffix = ['jpg', 'png', 'jpeg', 'git', 'bmp']
            files_suffix = files.name.split('.')[1]
            if files_suffix in allow_suffix:
                today = datetime.datetime.today()
                kindeditor_uploadpath = "HdWxShop/static/kindeditorimage/"
                dir_path = kindeditor_uploadpath + '%d/%d/' % (today.year, today.month)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                filename = str(uuid.uuid1()) + '.' + files_suffix
                file_url = os.path.join(dir_path,filename)
                return_file_url = settings.MEDIA_URL + file_url.replace('HdWxShop/','')
                open(file_url,'wb').write(files.file.read())
                result =  {'error':0,'url':return_file_url}
    return JsonResponse(result)


def create_code_img(request):
    # 直接在内存开辟一点空间存放临时生成的图片
    f = BytesIO()
    # 调用check_code生成照片和验证码
    img, code = checkcode.create_validate_code()
    # 将验证码存在服务器的session中，用于校验
    request.session['check_code'] = code
    # 生成的图片放置于开辟的内存中
    img.save(f,'PNG')
    # 将内存的数据读取出来，并以HttpResponse返回
    return HttpResponse(f.getvalue())


def datetimetostr(mydate):
    if mydate:
        return mydate.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return ""


# 用于判断订单处理时的权限
def isflowadmin(flowid,webuser_query,rolename):
    """
    :param flowid:  object.shoppingflow 其实是flow的query,这里名字懒得改而已
    :param webuser_query: object.webuser 操作此订单的用户webuser query
    :param rolename: string 用户的角色名,在登录的时候会写在session里面

    :return: Boolean 用户是否有权限操作改订单
    """
    if rolename == "管理员" or rolename == "管理人员":
        return True
    if rolename == "客户":
        return False
    if rolename == "销售人员":
        mycusts = models.custsalebind.objects.filter(Saleid=webuser_query)
        allcusts = models.custsalebind.objects.all().values_list('Customerid',flat=True)
        notbinduser = models.webuser.objects.exclude(id__in=allcusts)
        cust_userid = flowid.SfUserid.id
        mycustlist = []
        for eachcust in mycusts:
            mycustlist.append(eachcust.Customerid.id)
        for eachnbuser in notbinduser:
            mycustlist.append(eachnbuser.id)
        if cust_userid in mycustlist:
            return True


    try:
        ths_flowstatus = flowid.Sfstatus
    except:
        return False

    if rolename == "财务人员":
        if ths_flowstatus == 4:
            return True

    if rolename == "出货人员":
        if ths_flowstatus == 5:
            return True

    return False


# 简单的string转bool
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1","on")


# 用于上传文件
def uploadfile(filerequest,serverpath):
    i = 0
    # 是否重名
    filepath = os.path.join(serverpath,filerequest.name)
    while os.path.exists(filepath):
        filepath = serverpath + filerequest.name.split('.')[0] + '_' + str(i) + '.' + filerequest.name.split('.')[1]
        i += 1

    f = open(filepath,'wb')
    for line in filerequest.chunks():
        f.write(line)
    f.close()

    return filepath


# 生存订单ID
def createflowid():
    """
    :return: 14位时间 + 4位随机数
    """
    datetimenow = datetime.datetime.now()
    datetimenow_str = datetimenow.strftime('%Y%m%d%H%M%S')
    randomcode = createrandomcode(4)
    returnflowid = str(datetimenow_str) + str(randomcode)
    # 判但shoppingflow 是否有重复id
    flowid_count = models.shoppingflow.objects.filter(flowid=int(returnflowid)).count()
    if flowid_count > 0:
        return createflowid()
    else:
        return returnflowid



# 随机生成数字验证码
def createrandomcode(digit):
    """
    :param digit:  多少位数的验证码
    :return:
    """
    randomcode = ""
    for thiscode in range(digit):
        randomcode += str(random.randint(0,9))
    return randomcode


# 返回request.user 对应的webuser表 queryset
def outputwebuser(request):
    login_userid = request.user.id
    webuser_query = models.webuser.objects.get(userid=login_userid)
    return webuser_query


# 判断设备
def is_mobilerequest(request):
    is_mobile = False
    is_tablet = False
    is_phone = False
    user_agent = request.META.get("HTTP_USER_AGENT")
    http_accept = request.META.get("HTTP_ACCEPT")
    if user_agent and http_accept:
        agent = mobileesp.UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
        is_tablet = agent.detectTierTablet()
        is_phone = agent.detectTierIphone()
        is_mobile = is_tablet or is_phone or agent.detectMobileQuick()
        if is_mobile:
            return True
        else:
            return False

# 测试用
def testviews(request):
    is_mobile = False
    is_tablet = False
    is_phone = False
    title ='test'
    user_agent = request.META.get("HTTP_USER_AGENT")
    http_accept = request.META.get("HTTP_ACCEPT")
    if user_agent and http_accept:
        agent = mobileesp.UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
        is_tablet = agent.detectTierTablet()
        is_phone = agent.detectTierIphone()
        is_mobile = is_tablet or is_phone or agent.detectMobileQuick()
        if is_mobile:
            testinfo = "移动设备"
        else:
            testinfo = "电脑设备"
    return render(request, 'test.html', locals())




