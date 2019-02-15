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


# ********  用户消息表 ***********
class usermessage(models.Model):
    userid = models.ForeignKey(webuser,on_delete=models.CASCADE,verbose_name='用户名')
    title = models.CharField(max_length = 50,verbose_name = '标题')
    message = models.TextField(blank=True,verbose_name='消息内容')
    isread = models.BooleanField(verbose_name='是否已读')

    class Meta:
        indexes = [
            models.Index(fields = ['userid','isread'])
        ]

    verbose_name = '用户消息'
    verbose_name_plural = '用户消息'

    def __str__(self):
        return self.title


# ********* 用户地址列表 **********
class useraddress(models.Model):
    userid = models.ForeignKey(webuser, on_delete=models.CASCADE, verbose_name='用户名')
    UserAddress = models.CharField(max_length=255, null=True, verbose_name='地址')

    class Meta:
        indexes = [
            models.Index(fields=['userid'])
        ]


# **********  用户绑定表  ************
class userbind(models.Model):
    userid = models.OneToOneField(webuser,on_delete = models.CASCADE)
    Userphone = models.CharField(max_length = 30,null = True,verbose_name = '手机号码')
    Userwx = models.CharField(max_length = 50,null = True,verbose_name = '微信名')
    UserAddress = models.CharField(max_length = 255,null = True,verbose_name = '地址')

    class Meta:
        indexes = [
            models.Index(fields = ['userid'])
        ]


# ********** 用户wechat信息表 ***********
class userwechat(models.Model):
    userid = models.OneToOneField(webuser, on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    unionid = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50)
    sex = models.IntegerField()
    province = models.CharField(max_length=25,blank=True,verbose_name="省份")
    city = models.CharField(max_length=25,blank=True,verbose_name="地区")
    country = models.CharField(max_length=25,blank=True,verbose_name="国家")
    privilege = models.CharField(max_length=255,blank=True,verbose_name="用户特权信息")


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
    setcustprice = models.BooleanField(verbose_name='设置客户价格', default=False)

    class Meta:
        verbose_name = '角色权限'
        verbose_name_plural = '角色权限'

    def __str__(self):
        return self.Rolename


# *********  用户权限表  **********
class userrule(models.Model):
    Userid = models.ForeignKey(webuser,on_delete = models.CASCADE)
    Roleid = models.ForeignKey(userrole)
    ReleaseAdv = models.BooleanField(verbose_name='发布广告')
    ReleaseNew = models.BooleanField(verbose_name='发布新闻')
    ReleaseInfo = models.BooleanField(verbose_name='重要信息发布')
    AddCommodity = models.BooleanField(verbose_name='添加商品')
    ModCommodity = models.BooleanField(verbose_name='修改商品')
    AddOrder = models.BooleanField(verbose_name='添加订单')
    ModOrder = models.BooleanField(verbose_name='修改订单信息')
    ModOrderPrice = models.BooleanField(verbose_name='修改订单价格')
    AppOrder = models.BooleanField(verbose_name='订单审批')
    AckOrder = models.BooleanField(verbose_name='订单确认')
    PaidOrder = models.BooleanField(verbose_name='订单已付款')
    ShipOrder = models.BooleanField(verbose_name='订单出货')
    RecOrder = models.BooleanField(verbose_name='确认收货')
    TranInfo = models.BooleanField(verbose_name='导出历史交易信息')
    SalePer =  models.BooleanField(verbose_name='导出销售人员业绩')
    ProSummary = models.BooleanField(verbose_name='导出产品汇总表')
    ModRule = models.BooleanField(verbose_name='修改用户权限')
    setcustprice = models.BooleanField(verbose_name='设置客户价格',default=False)


    class Meta:
        indexes = [
            models.Index(fields = ['Userid','Roleid'])
        ]

        verbose_name = '用户权限'
        verbose_name_plural = '用户权限'


# **********  销售人员绑定表  ************
class custsalebind(models.Model):
    Customerid = models.ForeignKey(webuser,related_name = 'Customerid_Webuser',verbose_name='顾客')
    Saleid = models.ForeignKey(webuser,related_name = 'Saleid_Webuser',verbose_name='销售人员')
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
    CommName = models.CharField(max_length = 100,unique = True,verbose_name ='商品名称')
    Commimg = models.ImageField(upload_to = upload_commodityimg,blank = True)
    logisticsimg = models.ImageField(upload_to = upload_commodityimg,blank = True)
    reportimg = models.ImageField(upload_to = upload_commodityimg,blank = True)
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
    Commid = models.ForeignKey(commodityinfo,verbose_name='商品名称')
    CeiViewNum = models.BigIntegerField(default = 0,verbose_name='浏览次数')
    CeiBuyNUm = models.BigIntegerField(default = 0,verbose_name='销量')

    class Meta:
        indexes = [
            models.Index(fields = ['Commid'])
        ]


# **********  商品规格表  *************
class commditydetail(models.Model):
    Commid = models.ForeignKey(commodityinfo)
    Codbrand = models.CharField(default='',null=True, blank=True,max_length=15,verbose_name='品牌')
    Codfunction = models.CharField(default='',null = True, blank = True,max_length=15,verbose_name='功能')
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
        return str(self.Codbrand) + " | " + str(self.Codfunction) + " | " + str(self.Commid) + " | " + str(self.CodUnit) + " | "\
               + str(self.Codthick) + "|" + str(self.CodSize) +"|" + str(self.Cod_Protlevel)



# *********  客户单价表  ************
class custcommprice(models.Model):
    Cpuserid = models.ForeignKey(webuser,on_delete = models.CASCADE ,verbose_name = '用户名')
    Cpcommid = models.ForeignKey(commditydetail ,verbose_name = '商品及规格')
    CpunPrice = models.FloatField(verbose_name = '单价')

    class Meta:
        verbose_name = '客户单价表 '
        verbose_name_plural = '客户单价表'
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
        (2,'价格待审核'),
        (3,'客户待确认'),
        (4,'待付款'),
        (5,'待出货'),
        (6,'待收货'),
        (7,'已完成'),
    )

    SfUserid = models.ForeignKey(webuser,on_delete=models.CASCADE,verbose_name='用户')
    # Scid = models.OneToOneField(shoppingcart)
    flowid = models.CharField(max_length=30)
    Sfstatus = models.IntegerField(choices = Sfstatus_choices, verbose_name = '订单状态')
    SfCarryPrice = models.FloatField(default= 0)
    SfisCarryPrice = models.BooleanField(default = False)
    SfCreatetime = models.DateTimeField(auto_now_add = True,verbose_name='创建时间')
    SfRemark = models.TextField(blank = True)
    SfModtime = models.DateTimeField(auto_now = True)
    SfAddress = models.CharField(max_length = 255,null = True,verbose_name = '地址')
    sfsubmitname = models.CharField(max_length = 100,verbose_name='确认人员',blank=True)
    sfsubmittime = models.DateTimeField(null = True,verbose_name='确认时间',blank=True)
    sfpayname = models.CharField(max_length = 100,verbose_name='财务人员',blank=True)
    sfpaytime = models.DateTimeField(null = True,verbose_name='付款时间',blank=True)
    sfsmname = models.CharField(max_length = 100,verbose_name='出货人员',blank=True)
    sfsmtime = models.DateTimeField(null = True,verbose_name='出货时间',blank=True)

    class Meta:
        indexes = [
            models.Index(fields = ['SfUserid'])
        ]


# ********* 订单商品信息表 ***********
class shoppingflowproduct(models.Model):
    shoppingflowid = models.ForeignKey(shoppingflow,verbose_name="订单号")
    shoppinginfoid = models.ForeignKey(commodityinfo)
    shoppingdetailid = models.ForeignKey(commditydetail)
    sfpnum = models.IntegerField(verbose_name = "数量")
    sfpsumprice = models.FloatField(verbose_name="价格")
    sfpUnit = models.CharField(max_length=50, null=True, blank=True, verbose_name='单位')
    sfpthick = models.CharField(max_length=15, null=True, blank=True, verbose_name='厚度')
    sfpSize = models.CharField(max_length=30, null=True, blank=True, verbose_name='尺寸')
    sfp_Protlevel = models.CharField(max_length=5, null=True, blank=True, verbose_name='环保等级')
    sfpunPrice = models.FloatField(verbose_name='单价')
    sfpUnmun = models.IntegerField(blank=True, null=True, verbose_name='每件数量')

    class Meta:
        indexes = [
            models.Index(fields=['shoppingflowid','shoppinginfoid'])
        ]


# *********  订单流程完成商品表  **********
class shoppingendflow(models.Model):
    sefuserid = models.ForeignKey(webuser,related_name = 'shoppingflow_webuser_userid',verbose_name="用户ID")
    sefsaleid = models.ForeignKey(webuser,related_name = 'shoppingflow_webuser_custid',verbose_name='销售人员',null=True)
    Sefflowid = models.CharField(max_length=30,verbose_name='订单号')
    sefusername = models.CharField(max_length = 50,verbose_name="用户名")
    sefcarryprice = models.FloatField(verbose_name='运费')
    sefmark = models.TextField(verbose_name='备注')
    sefaddress = models.CharField(max_length = 255,null = True,verbose_name = '地址')
    sefcreatetime = models.DateTimeField(verbose_name='创建时间')
    SefFinishtime = models.DateTimeField(auto_now = True)
    sefsubmitname = models.CharField(max_length = 100,verbose_name='管理人员')
    sefsubmittime = models.DateTimeField(null = True,verbose_name='确认时间')
    sefpayname = models.CharField(max_length = 100,verbose_name='财务人员')
    sefpaytime = models.DateTimeField(null = True,verbose_name='付款时间')
    sefsmname = models.CharField(max_length = 100,verbose_name='出货人员')
    sefsmtime = models.DateTimeField(null = True,verbose_name='出货时间')

    class Meta:
        indexes = [
            models.Index(fields=['Sefflowid','sefuserid'])
        ]


# *********  订单流程完成商品表  **********
class shoppingendflowproduct(models.Model):
    shoppingendflowid = models.ForeignKey(shoppingendflow,on_delete=models.CASCADE)
    sefproductid = models.ForeignKey(commodityinfo,verbose_name='商品id')
    sefdetailid = models.ForeignKey(commditydetail,verbose_name='规格id')
    SefClass = models.CharField(max_length=50)
    Sefbrand = models.CharField(default='',null=True, blank=True,max_length=15,verbose_name='品牌')
    seffunc = models.CharField(default='',null=True, blank=True,max_length=15,verbose_name='功能')
    SefName = models.CharField(max_length=100)
    SefunPrice = models.FloatField()
    SefNum = models.IntegerField()
    SefPrice = models.FloatField()
    sefUnit = models.CharField(max_length=50, null=True, blank=True, verbose_name='单位')
    sefthick = models.CharField(max_length=15, null=True, blank=True, verbose_name='厚度')
    sefSize = models.CharField(max_length=30, null=True, blank=True, verbose_name='尺寸')
    sef_Protlevel = models.CharField(max_length=5, null=True, blank=True, verbose_name='环保等级')
    SefUnmun = models.IntegerField(null=True, blank=True, verbose_name='每件数量')

    class Meta:
        indexes= [
            models.Index(fields=['shoppingendflowid'])
        ]


# *********  新闻类别表  **********
class newsclass(models.Model):
    Nclassname = models.CharField(max_length = 50)

    class Meta:
        verbose_name = '新闻种类'
        verbose_name_plural = '新闻种类'

    def __str__(self):
        return self.Nclassname

def upload_advimg(instance, filename):
    advimg_path = 'HdWxShop/static/advimg'
    filenames = os.listdir(advimg_path)
    name = filename.split('.')[0]
    if '.' in filename:
        filetype = filename.split('.')[1]
    else:
        filetype = None
    temp = 0
    while filename in filenames:
        name += "_" + str(temp)
        if filetype:
            filename = name + "." + filetype
        temp += 1
    return os.path.join(advimg_path, filename)


# *********  新闻信息表  **********
class newsinfo(models.Model):
    Newsclassid = models.ForeignKey(newsclass)
    Newsbody = models.TextField(null = True)
    Newstitle = models.CharField(max_length = 255)
    Newsimage = models.ImageField(upload_to=upload_advimg,blank=True,null=True,default="",verbose_name="预览图片")
    Newsabstract = models.TextField(verbose_name="摘要")
    NewsCreatetime = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = '新闻信息'
        verbose_name_plural = '新闻信息'
        indexes = [
            models.Index(fields = ['Newsclassid'])
        ]

    def __str__(self):
        return self.Newstitle



# *********  商品广告表  **********
class advinfo(models.Model):
    Advcommid = models.ForeignKey(commodityinfo)
    Advimg = models.ImageField(upload_to = upload_advimg)
    Advtitle = models.CharField(max_length = 25)
    AdvCreatetime = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = '广告信息'
        verbose_name_plural = '广告信息'

    def __str__(self):
        return self.Advtitle



# **********  主页展示信息 ************
class indexshowcommodity(models.Model):
    indexclass = models.ForeignKey(commodityclass)
    showmany = models.IntegerField(default=5)



# **********  主页展示信息 ************
class indexcommend(models.Model):
    commendidx = models.IntegerField(verbose_name="优先级")
    commenddetail = models.ForeignKey(commditydetail,verbose_name="商品")



# *********  网页日志表  **********
class webdata(models.Model):
    Datatime = models.DateTimeField(auto_now_add = True)
    DataClassid = models.IntegerField()
    DataText = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields = ['Datatime','DataClassid'])
        ]


