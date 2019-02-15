"""HdShop URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from HdWxShop import views
from django.views.static import serve
from . import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^mainnews/(\d+)?$',views.mainnews),
    url(r'^news/(\d+)$',views.news),
    url(r'^login/$',views.login),
    url(r'^register/user/$',views.Registeruser),
    url(r'^register/user/usercheck/$',views.check_user),
    url(r'^resetpassword/$',views.resetpassword),
    url(r'^resetpassword/reset/$',views.resetpassword_commit),
    url(r'^create_code_img/$',views.create_code_img),
    url(r'logout/$',views.logout),
    url(r'^shop/$',views.shopv2),
    url(r'^shop/product/(\d+)?$',views.show_product),
    # -------------- settings -----------------
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    #-------------- 个人界面 -------------------
    url(r'^website/home/$',views.Website_home),
    url(r'^website/collect/$',views.Website_collect),
    url(r'^website/shoppingcart/$',views.Website_shoppingcart),
    url(r'^website/shoppingcart/submitshoppingcart/$',views.Website_submitshoppingcart),
    url(r'^website/shoppingflow/$',views.Website_shoppingflow),
    url(r'^website/shoppingflow/(\d+)$',views.Website_showmyflow),
    url(r'^website/userinfo/$',views.Website_userinfo),
    url(r'^website/userbindphone/$',views.Website_userbindphone),
    url(r'^website/history/$',views.Website_userhistory),
    #-------------- wechat相关 -------------------
    url(r'^login/wechatredirect_uri/$',views.wechatlogin.as_view()),
    # ------------ 管理界面  ----------------------
    url(r'^website/adminflow/$',views.Website_adminflow),
    url(r'^website/adminflow/(\d+)?$',views.Website_adminshowflow),
    url(r'^website/adminproduct/(\d+)?$',views.Website_adminproduct),
    url(r'^website/adminproduct/add$',views.Website_addproduct),
    url(r'^website/adminuser/(\d+)?$',views.Website_adminuser),
    url(r'^website/adminnews/(\d+)?$',views.Website_newsadmin),
    url(r'^website/adminnews/add$',views.Website_addnews),
    url(r'^website/admincommend/?$',views.Website_admincommend),
    # ------------ 销售人员管理界面 -----------------
    url(r'^website/saleadmin/(\d+)?$',views.Website_saleadmin),
    url(r'^salebindcust/$',views.ajax_salebindcust),
    # ------------ 数据导出 ------------------------
    url(r'^website/outputtrade/$',views.Website_outputtrade),
    url(r'^website/outputsaleach/$',views.Website_outputsaleach),
    url(r'^website/outputproductsale/$',views.Website_outputproductsale),
    url(r'^website/outputproducttotal/$',views.Website_outputproducttotal),
    # ---------------动态获取数据 ---------------------
    url(r'^freshen_businessleft/$',views.fresh_businessleft),
    url(r'^refresh_shopinfocache/$',views.getshopcache),
    url(r'^freshen_commend/$',views.fresh_commend),
    url(r'^freshen_taprice/$',views.freshen_taprice),
    url(r'^freshen_indexcominfo/$',views.freshen_indexcominfo),
    url(r'^freshen_shopinfo/$',views.freshen_shop),
    url(r'^fresh_newsinfo/$',views.fresh_newsinfo),
    url(r'^fresh_userflow/$',views.fresh_userflow),
    url(r'^fresh_amount/$',views.fresh_shoppingcartAmount),
    url(r'^freshen_myshowflow/$',views.refreshen_userflowproduct),
    url(r'^refreshen_tacollect/$',views.refreshen_tacollect),
    url(r'^freshen_myaddress/$',views.freshen_myaddress),
    # ---------------  接口  ---------------------
    url(r'^sendcheckcode/$',views.ajax_sendcheckcode),
    url(r'^ajax_cpassword/$',views.ajax_cpassword),
    url(r'^ajax_cwebusername/$',views.ajax_change_webusername),
    url(r'^rpwdsms/$',views.ajax_resetpassword_sendcode),
    url(r'^ajax_addcollect/$',views.ajax_addcollect),
    url(r'^ajax_addshoppingcart/$',views.ajax_addshoppingcart),
    url(r'^ajax_submitorder/$',views.ajax_submitorder),
    url(r'^ajax_adminflowoperate/$',views.ajax_adminflowoperate),
    url(r'^ajax_adminproduct/$',views.ajax_adminproduct),
    url(r'^ajax_adminuser/$',views.ajax_adminuser),
    url(r'^ajax_adminnews/$',views.ajax_adminnews),
    url(r'^ajax_setsale/$',views.ajax_setsale),
    url(r'^ajax_unbindcust/$',views.ajax_unbindcust),
    url(r'^ajax_adminaddress/$',views.ajax_adminaddress),
    url(r'^ajax_admincommend/$',views.ajax_admincommend),
    url(r'^upload/kindeditor/$',views.kindeditor_upload),
    # --------------- test ---------------------
    url(r'test/$',views.testviews),
]


