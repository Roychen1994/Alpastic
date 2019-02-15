from django.contrib import admin
from .models import webuser, userbind ,userrule,userrole, custsalebind, commodityinfo,commodityendinfo,commditydetail,commodityclass, shoppingflow,\
    shoppingcart,newsinfo,newsclass, advinfo,shoppingflowproduct,custcommprice,indexshowcommodity,indexcommend,useraddress

# Register your models here.
admin.site.site_header = '厚徳木业源管理系统'
admin.site.site_title  = '厚徳木业后台管理'


# UserAdmin 关联 webuser-->userbind
class userbindtab(admin.TabularInline):
    model = userbind


# 用户表管理界面
@admin.register(webuser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['userid','Username','statuscolor',]
    list_per_page = 50
    #ordering = ('-CreateTime',)
    search_fields = ('Username',)
    inlines = [userbindtab,]


# 权限管理
# 角色
@admin.register(userrole)
class userrolrAdmin(admin.ModelAdmin):
    list_display = ['Rolename']

# 用户
@admin.register(userrule)
class userruleAdmin(admin.ModelAdmin):
    list_display = ['Userid','Roleid']

# 用户绑定
@admin.register(custsalebind)
class userbinddamin(admin.ModelAdmin):
    list_display = ['Customerid','Saleid']

# 商品类别添加
@admin.register(commodityclass)
class commdityclassAdmin(admin.ModelAdmin):
    list_display = ['CclassName']


# 商品表管理
class commditydetailtab(admin.TabularInline):
    model = commditydetail

@admin.register(commodityinfo)
class commdityinfoAdmin(admin.ModelAdmin):
    list_display = ['CommName','CommInfo','CreateTime']
    list_per_page = 50
    search_fields = ('Commname',)
    inlines = [commditydetailtab]

# 客户单价表
@admin.register(custcommprice)
class custcommpriceAdmin(admin.ModelAdmin):
    list_display = ['Cpuserid', 'Cpcommid', 'CpunPrice']
    list_per_page = 50
    search_fields = ('Cpuserid','Cpcommid')


# 历史信息表,仅供查看,此处测试用....
@admin.register(commodityendinfo)
class commodityendinfoAdmin(admin.ModelAdmin):
    list_display = ['Commid','CeiViewNum','CeiBuyNUm']


# 流程管理
@admin.register(shoppingcart)
class shoppingcartAdmin(admin.ModelAdmin):
    list_display = ['ScUserid','ScCollectid','ScNum','ScunPrice','ScSum','ScAddDate']
    list_per_page = 50
    search_fields = ('ScCollectid',)


class shoppingflowproducttab(admin.TabularInline):
    model = shoppingflowproduct


@admin.register(shoppingflow)
class shoppingflowAdmin(admin.ModelAdmin):
    list_display = ['SfUserid','Sfstatus','SfAddress','SfCreatetime']
    list_per_page = 50
    inlines = [shoppingflowproducttab]

# 广告管理
@admin.register(advinfo)
class AdvinfoAdmin(admin.ModelAdmin):
    list_display = ['Advcommid','Advtitle','Advimg']
    list_per_page = 50


# 新闻管理
# 新闻类型
@admin.register(newsclass)
class newsclassAdmin(admin.ModelAdmin):
    list_display = ['Nclassname']

# 新闻信息
@admin.register(newsinfo)
class newsinfoAdmin(admin.ModelAdmin):
    list_display = ['Newsclassid','Newstitle','Newsbody']
    list_per_page = 50
    search_fields = ('Newstitle',)


@admin.register(indexshowcommodity)
class indexshowcommodityAdmin(admin.ModelAdmin):
    list_display = ['indexclass','showmany']
    list_per_page = 50


@admin.register(indexcommend)
class indexshowcommend(admin.ModelAdmin):
    list_display = ['commendidx','commenddetail']
    list_per_page = 50

@admin.register(useraddress)
class useraddressAdmin(admin.ModelAdmin):
    list_display = ['userid', 'UserAddress']
    list_per_page = 50


