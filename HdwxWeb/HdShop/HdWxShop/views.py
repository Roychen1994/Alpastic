from django.shortcuts import render,redirect,render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from . import models, myforms, checkcode

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

import json
from io import BytesIO

# Create your views here.
def index(request):
    index_template = get_template('index.html')
    classes = models.commodityclass.objects.all()
    advinfo_table = models.advinfo.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username
    index_html = index_template.render(locals())
    return HttpResponse(index_html)


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
                User.objects.create(username = data_username,password = data_password)
                ths_userid = User.objects.get(username = data_username)
                models.webuser.objects.create(userid = ths_userid,Username = data_username)
                custom = models.userrole.objects.get(Rolename = '客户')
                ths_webuserid = models.webuser.objects.get(userid = ths_userid)
                models.userrule.objects.create(Userid = ths_webuserid,Roleid = custom,ReleaseAdv = custom.ReleaseAdv, \
                                               ReleaseNew = custom.ReleaseNew,ReleaseInfo = custom.ReleaseInfo,AddCommodity = custom.AddCommodity, \
                                               ModCommodity = custom.ModCommodity,AddOrder = custom.AddOrder, ModOrder = custom.ModOrder, ModOrderPrice = custom.ModOrderPrice, \
                                               AppOrder = custom.AppOrder, AckOrder = custom.AckOrder,PaidOrder = custom.PaidOrder,ShipOrder = custom.ShipOrder,RecOrder = custom.RecOrder, \
                                               TranInfo = custom.TranInfo, SalePer = custom.SalePer,ProSummary = custom.ProSummary, ModRule = custom.ModRule)
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
        users = User.objects.filter(username = username).count()
        print(users)
        if users > 0:
            return JsonResponse({'Msg':'hasuser'})
        else:
            return JsonResponse({'Msg':'nouser'})


def login(request):
    classes = models.commodityclass.objects.all()
    errors = checkcode_error = False
    login_forms = myforms.weblogin()

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
                        auth.login(request,login_user)
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
    classes = models.commodityclass.objects.all()
    login_forms = myforms.weblogin()
    auth.logout(request)
    return render(request, 'login.html', locals())



def hdshop(request):
    set_showmany = 5
    classes = models.commodityclass.objects.all()
    login_username = False
    if request.user.is_authenticated():
        login_username = request.user.username

    if request.method == 'GET':
        commodity_rdit = {}

        try:
            page = int(request.GET.get('page'))
        except:
            page = 1

        try:
            commditycls = request.GET.get('cls')
        except:
            commditycls = None

        # 分页
        # 没有选择商品类型
        if not commditycls:
            commditydetail_count = models.commditydetail.objects.all().count()
            max_page = int(commditydetail_count / set_showmany)
            if page <= 1 :
                commditydetail_frist_no = 0
                commditydetail_last_no = set_showmany - 1
            elif page >= max_page:
                commditydetail_frist_no = (max_page - 1) * set_showmany
                commditydetail_count = commditydetail_count
            else:
                commditydetail_frist_no = (page - 1) * set_showmany
                commditydetail_last_no  = (page * set_showmany) - 1

            # 统计共输出多少个元素
            commditydetail_num = 0
            for commcls in classes:
                commodity_rdit[commcls.CclassName] = {}
                commcls_infos = Commid = models.commodityinfo.objects.filter(Commclass = commcls.id)
                for clsinfo in commcls_infos:
                    commditydetail_this_count = models.commditydetail.objects.filter(Commid=clsinfo.id).count()
                    commditydetail_num += commditydetail_this_count
                    if commditydetail_num < commditydetail_frist_no: continue
                    if commditydetail_num < commditydetail_last_no :
                        commodity_rdit[commcls.CclassName][clsinfo.CommName] = models.commditydetail.objects.filter(
                            Commid = clsinfo.id)
                    else:
                        commodity_rdit[commcls.CclassName][clsinfo.CommName] = models.commditydetail.objects.filter(
                            Commid = clsinfo.id)[:commditydetail_num - commditydetail_last_no]
                        return render(request, 'shop.html', locals())
            # commodity_rdit[commcls] = models.commditydetail.objects.all\
            #     (Commid = models.commodityinfo.objects.all(Commclass = commcls.id))

    return render(request,'shop.html',locals())


# 商城用的分页功能
def shop_Pagination(page):
    set_showmany = 5



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


def testviews(request):

    for each in models.commodityclass.objects.all():
        print(each.id)
    return render(request, 'test.html', locals())

