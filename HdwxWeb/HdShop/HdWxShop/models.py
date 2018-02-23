import os
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User


# Create your models here.

# *********  用户表  *********
class webuser(models.Model):

    statuschoices = (
        (0,'异常'),
        (1,'正常'),
        (2,'冻结'),
    )

    userid = models.ForeignKey(User,on_delete = models.CASCADE)
    Username = models.CharField(max_length = 100,unique = True,verbose_name = '用户名')
    Userstatus = models.IntegerField(default = 1,choices = statuschoices,verbose_name = '状态')
    Createtime = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'
        indexes = [
                models.Index(fields = ['userid'])
            ]

    def statuscolor(self):
        if self.Userstatus == 0 :
            thiscolor = 'red'
            thisstatus = '异常'
        elif self.Userstatus == 2:
            thiscolor = 'red'
            thisstatus = '冻结'
        else:
            thiscolor = 'green'
            thisstatus = '正常'
        return format_html('<span style="color:{};">{}</span>',thiscolor,thisstatus)

    statuscolor.short_description = "状态"

    def __str__(self):
        return self.Username


# ********  用户绑定表  *********
class userbind(models.Model):
    userid = models.OneToOneField(webuser,on_delete = models.CASCADE)
    Userphone = models.CharField(max_length = 30,null = True,verbose_name = '手机号码')
    Userwx = models.CharField(max_length = 50,null = True,verbose_name = '微信号')
    UserAddress = models.CharField(max_length = 255,null = True,verbose_name = '地址')

    class Meta:
        indexes = [
            models.Index(fields = ['userid'])
        ]



# ********  角色权限表  **********
class userrole(models.Model):
    Rolename = models.CharField(max_length = 50)
    ReleaseAdv = models.BooleanField()
    ReleaseNew = models.BooleanField()
    ReleaseInfo = models.BooleanField()
    AddCommodity = models.BooleanField()
    ModCommodity = models.BooleanField()
    AddOrder = models.BooleanField()
    ModOrder = models.BooleanField()
    ModOrderPrice = models.BooleanField()
    AppOrder = models.BooleanField()
    AckOrder = models.BooleanField()
    PaidOrder = models.BooleanField()
    ShipOrder = models.BooleanField()
    RecOrder = models.BooleanField()
    TranInfo = models.BooleanField()
    SalePer =  models.BooleanField()
    ProSummary = models.BooleanField()
    ModRule = models.BooleanField()

    class Meta:
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'

    def __str__(self):
        return self.Rolename


# *********  用户权限表  **********
class userrule(models.Model):
    Userid = models.ForeignKey(webuser,on_delete = models.CASCADE)
    Roleid = models.ForeignKey(userrole)
    ReleaseAdv = models.BooleanField()
    ReleaseNew = models.BooleanField()
    ReleaseInfo = models.BooleanField()
    AddCommodity = models.BooleanField()
    ModCommodity = models.BooleanField()
    AddOrder = models.BooleanField()
    ModOrder = models.BooleanField()
    ModOrderPrice = models.BooleanField()
    AppOrder = models.BooleanField()
    AckOrder = models.BooleanField()
    PaidOrder = models.BooleanField()
    ShipOrder = models.BooleanField()
    RecOrder = models.BooleanField()
    TranInfo = models.BooleanField()
    SalePer =  models.BooleanField()
    ProSummary = models.BooleanField()
    ModRule = models.BooleanField()


    class Meta:
        indexes = [
            models.Index(fields = ['Userid','Roleid'])
        ]

        verbose_name = '用户权限'
        verbose_name_plural = '用户权限'


# **********  销售人员绑定表  ************
class custsalebind(models.Model):
    Customerid = models.ForeignKey(webuser,related_name = 'Customerid_Webuser')
    Saleid = models.ForeignKey(webuser,related_name = 'Saleid_Webuser')
    Binddate = models.DateTimeField(auto_now = True)

    class Meta:
        indexes = [
            models.Index(fields = ['Customerid'] )
        ]


# **********  商品类别表  *************
class commodityclass(models.Model):
    CclassName = models.CharField(max_length = 50,unique = True,verbose_name = '商品类别')

    class Meta:
        verbose_name = '商品类别'
        verbose_name_plural = '商品类别'

    def __str__(self):
        return self.CclassName

#商品信息静态页面上传用
#def upload_commdityinfo(instance,filename):
#    return 'HdShop/CommdityFile/%Y%m%d_{}'.format(filename)

def upload_commodityinfo(instance,filename):
    advimg_path = 'HdWxShop/static/commodityinfo'
    filenames = os.listdir(advimg_path)
    name = filename.split('.')[0]
    if  '.' in filename:
        filetype = filename.split('.')[1]
    else:
        filetype = None
    temp = 0
    while filename in filenames:
        name += "_" + str(temp)
        if  filetype :
            filename = name + "." + filetype
        temp += 1
    return os.path.join(advimg_path,filename)

def upload_commodityimg(instance,filename):
    advimg_path = 'HdWxShop/static/commodityimg'
    filenames = os.listdir(advimg_path)
    name = filename.split('.')[0]
    if  '.' in filename:
        filetype = filename.split('.')[1]
    else:
        filetype = None
    temp = 0
    while filename in filenames:
        name += "_" + str(temp)
        if  filetype :
            filename = name + "." + filetype
        temp += 1
    return os.path.join(advimg_path,filename)


# **********  商品信息表  ************
class commodityinfo(models.Model):
    Commclass = models.ForeignKey(commodityclass)
    CommName = models.CharField(max_length = 100,unique = True,verbose_name ='商品名称' )
    Commimg = models.ImageField(upload_to = upload_commodityimg,blank = True)
    CommInfo = models.ImageField(upload_to = upload_commodityinfo,blank = True)
    CreateTime = models.DateTimeField(auto_now = True)


    class Meta:
        verbose_name = '商品信息'
        verbose_name_plural = '商品信息'
        indexes = [
            models.Index(fields = ['Commclass'])
        ]

    def __str__(self):
        return self.CommName


# *********  商品历史信息  ************
class commodityendinfo(models.Model):
    Commid = models.ForeignKey(commodityinfo)
    CeiViewNum = models.BigIntegerField(default = 0)
    CeiBuyNUm = models.BigIntegerField(default = 0)

    class Meta:
        indexes = [
            models.Index(fields = ['Commid'])
        ]


# **********  商品规格表  *************
class commditydetail(models.Model):
    Commid = models.ForeignKey(commodityinfo)
    CodUnit = models.CharField(max_length = 50, null = True, blank = True , verbose_name = '单位')
    # CodSpec = models.CharField(max_length = 50, null = True, blank = True , verbose_name = '规格')
    Codthick = models.CharField(max_length = 15,null = True,blank = True,verbose_name='厚度' )
    CodSize = models.CharField(max_length = 30,null = True,blank = True, verbose_name = '尺寸')
    Cod_Protlevel = models.CharField(max_length = 5,null = True,blank = True, verbose_name = '环保等级')
    CodunPrice = models.FloatField(verbose_name = '单价')
    Codinventory = models.IntegerField(blank = True,default = 0,null = True,verbose_name = '库存')
    CodUnmun = models.IntegerField(blank = True, null = True,verbose_name = '每件数量')
    class Meta:
        indexes = [
            models.Index(fields = ['Commid'])
        ]

    def __str__(self):
        return str(self.Commid) + " | " + str(self.CodUnit) + " | " + str(self.Codthick) + "|" + \
               str(self.CodSize) +"|" + str(self.Cod_Protlevel)



# *********  客户单价表  ************
class custcommprice(models.Model):
    Cpuserid = models.ForeignKey(webuser,on_delete = models.CASCADE ,verbose_name = '用户名')
    Cpcommid = models.ForeignKey(commditydetail ,verbose_name = '商品及规格')
    CpunPrice = models.FloatField(verbose_name = '单价')

    class Meta:
        indexes = [
            models.Index(fields = ['Cpuserid','Cpcommid'])
        ]


# **********  商品收藏表  ************
class custcollect(models.Model):
    CcUserid = models.ForeignKey(webuser, on_delete = models.CASCADE)
    CcCommid = models.ForeignKey(commditydetail)
    CollectDate = models.DateTimeField(auto_now = True)

    class Meta:
        indexes = [
            models.Index(fields = ['CcUserid','CcCommid'])
        ]


# *********  购物车表  *************
class shoppingcart(models.Model):
    ScUserid = models.ForeignKey(webuser, on_delete = models.CASCADE)
    ScCollectid = models.ForeignKey(commditydetail)
    ScNum = models.IntegerField()
    ScunPrice = models.FloatField()
    ScSum = models.FloatField()
    ScAddDate = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'

        indexes = [
            models.Index(fields = ['ScUserid','ScCollectid'])
        ]


# *********  订单流程表  *************
class shoppingflow(models.Model):

    Sfstatus_choices = (
        (1,'有意向'),
        (2,'生成已订单'),
        (3,'价格待审核'),
        (4,'客户待确认'),
        (5,'待付款'),
        (6,'待出货'),
        (7,'待收货'),
    )

    Scid = models.OneToOneField(shoppingcart)
    Sfstatus = models.IntegerField(choices = Sfstatus_choices, verbose_name = '订单状态')
    SfCarryPrice = models.FloatField(default= 0)
    SfisCarryPrice = models.BooleanField(default = False)
    SfCreatetime = models.DateTimeField(auto_now_add = True)
    SfRemark = models.TextField(blank = True)
    SfModtime = models.DateTimeField(auto_now = True)

    class Meta:
        indexes = [
            models.Index(fields = ['Scid'])
        ]


# *********  订单流程完成表  **********
class shoppingendflow(models.Model):
    SefClass = models.CharField(max_length = 50)
    SefName = models.CharField(max_length = 100)
    SefUnit = models.CharField(max_length = 50)
    SefSpec = models.CharField(max_length = 50)
    SefCarryPrice = models.FloatField(default = 0)
    SefunPrice = models.FloatField()
    SefNum = models.IntegerField()
    SefPrice = models.FloatField()
    SefUnmun = models.IntegerField(null = True, blank=True,verbose_name='每件数量')
    SefCreate = models.DateTimeField()
    SefRemark = models.TextField(blank = True)
    SefFinishtime = models.DateTimeField(auto_now = True)

    class Meta:
        indexes = [
            models.Index(fields=['SefClass', 'SefName'])
        ]


# *********  新闻类别表  **********
class newsclass(models.Model):
    Nclassname = models.CharField(max_length = 50)

    class Meta:
        verbose_name = '新闻种类'
        verbose_name_plural = '新闻种类'

    def __str__(self):
        return self.Nclassname


# *********  新闻信息表  **********
class newsinfo(models.Model):
    Newsclassid = models.ForeignKey(newsclass)
    Newsbody = models.TextField(null = True)
    Newstitle = models.CharField(max_length = 255)
    NewsCreatetime = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = '新闻信息'
        verbose_name_plural = '新闻信息'
        indexes = [
            models.Index(fields = ['Newsclassid'])
        ]

    def __str__(self):
        return self.Newstitle


def upload_advimg(instance,filename):
    advimg_path = 'HdWxShop/static/advimg'
    filenames = os.listdir(advimg_path)
    name = filename.split('.')[0]
    if  '.' in filename:
        filetype = filename.split('.')[1]
    else:
        filetype = None
    temp = 0
    while filename in filenames:
        name += "_" + str(temp)
        if  filetype :
            filename = name + "." + filetype
        temp += 1
    return os.path.join(advimg_path,filename)


# *********  商品广告表  **********
class advinfo(models.Model):
    Advcommid = models.ForeignKey(commodityinfo)
    Advimg = models.ImageField(upload_to = upload_advimg)
    Advtitle = models.CharField(max_length = 255)
    AdvCreatetime = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = '广告信息'
        verbose_name_plural = '广告信息'

    def __str__(self):
        return self.Advtitle


# *********  网页日志表  **********
class webdata(models.Model):

    Datatime = models.DateTimeField(auto_now_add = True)
    DataClassid = models.IntegerField()
    DataText = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields = ['Datatime','DataClassid'])
        ]


