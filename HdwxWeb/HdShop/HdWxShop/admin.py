from django.contrib import admin
from .models import webuser, userbind ,userrule,userrole, custsalebind, commodityinfo ,commditydetail,commodityclass, shoppingflow,\
    shoppingcart,newsinfo,newsclass, advinfo

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


# 流程管理
class shoppingflowtab(admin.TabularInline):
    model = shoppingflow

@admin.register(shoppingcart)
class shoppingcartAdmin(admin.ModelAdmin):
    list_display = ['ScUserid','ScCollectid','ScNum','ScunPrice','ScSum','ScAddDate']
    list_per_page = 50
    search_fields = ('ScCollectid',)
    inlines = [shoppingflowtab]

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





