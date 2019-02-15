
/**  修改用户权限  **/
function ajax_changerule(worktype) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var userid = $("#userid").text();
    var wtype = worktype;
    var isadv = $("input[value='isadv']").is(":checked");
    var isnews = $("input[value='isnews']").is(":checked");
    var isinfo = $("input[value='isinfo']").is(":checked");
    var isaddp = $("input[value='isaddp']").is(":checked");
    var ismodp = $("input[value='ismodp']").is(":checked");
    var isaddo = $("input[value='isaddo']").is(":checked");
    var ismodo = $("input[value='ismodo']").is(":checked");
    var ismodop = $("input[value='ismodop']").is(":checked");
    var isappo = $("input[value='isappo']").is(":checked");
    var isacko = $("input[value='isacko']").is(":checked");
    var ispado = $("input[value='ispado']").is(":checked");
    var isshpo = $("input[value='isshpo']").is(":checked");
    var isreco = $("input[value='isreco']").is(":checked");
    var istrif = $("input[value='istrif']").is(":checked");
    var issalp = $("input[value='issalp']").is(":checked");
    var isprsm = $("input[value='isprsm']").is(":checked");
    var ismodu = $("input[value='ismodu']").is(":checked");
    var isstcp = $("input[value='isstcp']").is(":checked");
    $.ajax({
        url: '/ajax_adminuser/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'userid': userid,
            'isadv':isadv,
            'isnews':isnews,
            'isinfo':isinfo,
            'isaddp':isaddp,
            'ismodp':ismodp,
            'isaddo':isaddo,
            'ismodo':ismodo,
            'ismodop':ismodop,
            'isappo':isappo,
            'isacko':isacko,
            'ispado':ispado,
            'isshpo':isshpo,
            'isreco':isreco,
            'istrif':istrif,
            'issalp':issalp,
            'isprsm':isprsm,
            'ismodu':ismodu,
            'isstcp':isstcp,
            'worktype': wtype
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                infomadal('修改权限成功!','text-success');
                $('#infomodal').modal('show');
            }else if(data.Msg === 'error'){
                infomadal('修改失败,请刷新页面后重试.','text-danger');
                $('#infomodal').modal('show');
            }
        }
    })
}




/****  商品选择change触发 *****/
 $("select#user-productname").change(function(){
     var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
     var userid = $("#userid").text();
     var productid =  $("#user-productname").val();
     $.ajax({
         url: '/ajax_adminflowoperate/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'query-pd',
             'productid': productid,
             'custid': userid
         },
         dataType: 'json',
         success: function (data) {
             $('#user-productdetail').empty();
             if (data.Msg === 'succ') {
                var dlist = data.dlist;
                 for (var i = 0; dlist.length >= i +1 ; i++) {
                    var thsdetailop = document.createElement("option");
                    thsdetailop.text = dlist[i][0];
                    thsdetailop.setAttribute("value", dlist[i][1]);
                    $("#user-productdetail").append(thsdetailop);
                    $("input[name='user-unPrice']").val(data.unprice)
                }
             }
         }
     })
 })


/****  规格选择change触发 *****/
 $("select#user-productdetail").change(function() {
     var detailid = $("#user-productdetail").val();
     var custid = $("#userid").text();
     var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
     $.ajax({
         url: '/ajax_adminflowoperate/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'query-detail',
             'detailid': detailid,
             'custid': custid
         },
         dataType: 'json',
         success: function (data) {
             if (data.Msg === 'succ') {
                $("input[name='user-unPrice']").val(data.unprice)
             }
         }
     })
 })





/****  添加客户价格 *****/
function setcprice(userid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var detailid = $("#user-productdetail").val();
    var unprice = $("input[name='user-unPrice']").val();
     $.ajax({
         url: '/ajax_adminuser/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'userid': userid,
             'detailid':detailid,
             'unprice':unprice,
             'worktype':'setcp'
         },
         dataType: 'json',
         success: function (data) {
             if (data.Msg === 'succ') {
                 $('#addccpModal').modal('hide');
                 freshen_taprice(userid);
             }else if(data.Msg === 'hascp') {
                 infomadal('该客户单价已存在', 'text-danger');
                 $('#infomodal').modal('show');
             }else if(data.Msg === 'norule'){
               infomadal('没有权限','text-danger');
               $('#infomodal').modal('show');
             }else if(data.Msg === 'error'){
                infomadal('添加失败,请刷新页面后重试.','text-danger');
                $('#infomodal').modal('show');
            }
         }
     })
}


/****  删除所选用户单价 *****/
function deluserunprice(userid){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var deletelist = new Array();
    var doms_checked = document.getElementsByClassName("ncheck");
    var j = 0;
    for (var i = doms_checked.length - 1; i >= 0; i--) {
        if (doms_checked[i].checked) {
            deletelist[j] = doms_checked[i].value;
            j++
        }
    }
        $.ajax({
            url: '/ajax_adminuser/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_value,
                'worktype': 'delcp',
                'deletelist': JSON.stringify(deletelist)
            },
            dataType: 'json',
            success: function (data) {
                if (data.Msg === 'succ') {
                 freshen_taprice(userid);
                 $('#delusercp-Modal').modal('hide');
             }else if(data.Msg === 'error'){
                infomadal('添加失败,请刷新页面后重试.','text-danger');
                $('#infomodal').modal('show');
                }
            }
        })
}


/*********** 刷新客户单价数据 **************/
function freshen_taprice(userid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var taprice_dom = $('#cptbody');
    taprice_dom.empty();
    $.ajax({
        url: '/freshen_taprice/',
        type: 'POST',
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'custid': userid
        },
        success: function (data) {
            if (data.Msg === 'succ') {
                var cpdata = data.data;
                for(var i = 0; cpdata.length >= i +1 ; i++){
                    var trdom = document.createElement("tr");
                    var trhtml = "";
                    trhtml += "<td><input class=\"ncheck\" type=\"checkbox\" value=\"" + cpdata[i].cpid + "\"></td>";
                    trhtml += "<td class='detailname'>" + cpdata[i].pname + "</td>" +
                              "<td>"  + cpdata[i].thick + " | " + cpdata[i].psize + " | " +
                               cpdata[i].protlevel + " | " + cpdata[i].inventory + " | " + cpdata[i].unmun + cpdata[i].unit + "</td>";
                    trhtml += "<td class='detailcp'> ￥" + cpdata[i].custprice + "</td>";
                    trdom.innerHTML = trhtml;
                    taprice_dom.append(trdom);
                }
            }
        }
    })
}


/*************** 删除客户单价模态框 *****************/
$('#delusercp-Modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var doms_checked = document.getElementsByClassName("ncheck");
    var oldom = document.getElementById("delcpmodal-ol");
    oldom.innerHTML = "";
        for(var i = doms_checked.length - 1; i >= 0; i--){
        if(doms_checked[i].checked){
            var lidom = document.createElement("li");
            var check_parent = doms_checked[i].parentNode.parentNode;
            var detailinfotr = check_parent.getElementsByClassName("detailname")[0];
            var detailcp = check_parent.getElementsByClassName("detailcp")[0];
            lidom.innerText= detailinfotr.innerText + detailcp.innerText;
            oldom.append(lidom);
        }
    }

})


/************** 销售人员解邦客户模态框 **************/
$('#unbindModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var customerid = button.data('custid');
    var custname = button.data('custname');
    $("#unbind-modalbody").html("<p class='lead'>是否解邦客户<strong>"+ custname +"</strong></p>");
    document.getElementById('btn_unbindcust').onclick = function(){saleunbindcust(String(customerid))}
})


/********************* 销售人员解邦客户 *****************/
function saleunbindcust(custid){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
        $.ajax({
            url: '/ajax_unbindcust/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_value,
                'custid': custid
            },
            dataType: 'json',
            success: function (data) {
                if (data.rcode === 1){
                    window.location.reload();
                }
            }
        })
}


/********** 销售人员绑定客户 **********/
function salebindcust() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var custid = $("select[name='sale-custid']").val();
    $.ajax({
        url: '/salebindcust/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'custid':custid
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }
        }
    })
}

/******** 用户信息页面修改密码 ********/
function cpassword(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var oldpassword = $('#oldpassword').val();
    var newpassword1 = $('#newpassword1').val();
    var newpassword2 = $('#newpassword2').val();
    $('#errorinfo').empty();
    if(newpassword1 !== newpassword2){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>两次输入的密码不一致.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(newpassword1.length < 6){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>密码长度需要大于6位.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_cpassword/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'oldpassword':oldpassword,
            'newpassword1':newpassword1,
            'newpassword2':newpassword2
        },
        dataType: 'json',
        success: function (data) {
            if (data.rcode === 1) {
                $('#info-content').html('<p class="text-success">修改密码成功</p>');
                $('#cpassword').modal('hide');
                $('#infomodal').modal('show');
            }else if(data.rcode === 2){
                $('#info-content').html('<p class="text-danger">旧密码错误</p>');
                $('#cpassword').modal('hide');
                $('#infomodal').modal('show');
            }else{
                $('#info-content').html('<p class="text-danger">修改密码异常,可能是两次密码输入不正确.</p>');
                $('#cpassword').modal('hide');
                $('#infomodal').modal('show');
            }
        }
    })
}


/****** 获取验证码 *******/
function sendcheckcode(worktype) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var phonenum = $('#myphone').val();
    var re = /^(\w){11}$/;
    if(!re.test(phonenum)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>手机格式有误.请重新输入</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/sendcheckcode/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'phonenum': phonenum,
            'worktype':worktype
        },
        dataType: 'json',
        success: function (data) {
            if (data.rcode === 1){
                var mybutton = $('#btn_sendcode');
                mybutton.attr("disabled","disabled");
                buttonloading(mybutton,60)
            }if (data.rcode === 0 ){
                alert('请稍候再试');
            }
        }
    })
}


/****** 重置密码时用的发送验证码 ******/
function resetpassword_sendcode(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var phonenumber = $("#phonenumber").val();
    var username = $('#username').val();
    var checkcode = $('#bfsendcheck').val();
    $.ajax({
        url: '/rpwdsms/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'phonenumber': phonenumber,
            'username':username,
            'checkcode':checkcode
        },
        dataType: 'json',
        success: function (data) {
            var input_bfsendcheck = $('#bfsendcheck');
            if (data.rcode === 1){
                var mybutton = $('#btn_sendcode');
                mybutton.attr("disabled","disabled");
                buttonloading(mybutton,60)
            }else if(data.rcode === 2){
                alert('请稍候再试');
            }else if(data.rcode === 99){
                alert('账户或手机号码不正确');
                input_bfsendcheck.css('border-color','');
                input_bfsendcheck.val("");
                $('#check_code_img').click()
            }else if(data.rcode === 98){
                input_bfsendcheck.css('border-color','#a94442');
                input_bfsendcheck.val("");
                $('#check_code_img').click()
            }
        }
    })
}



/******** 设置销售人员 ********/
function setsale() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var saleid = $('#saleselect').val();
    $.ajax({
        url: '/ajax_setsale/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'saleid':saleid
        },
        dataType: 'json',
        success: function (data) {
            if(data.rcode === 1){
                window.location.reload();
            }else{
                $('#info-content').html('<p class="text-danger">绑定结果异常,请稍候再试.</p>');
                $('#salebindmodal').modal('hide');
                $('#infomodal').modal('show');
            }
        }
    })
}


/************* 更改昵称 ************/
function changewebusername() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var webusername = $("#newwebusername").val();
    $('#errorinfo').empty();
    var re = /^[a-zA-Z0-9_\u4e00-\u9fa5]{1,18}$/;
    if (!re.test(webusername)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>输入格式有误.请重新输入</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_cwebusername/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'webusername': webusername
        },
        dataType: 'json',
        success: function (data) {
            if (data.rcode === 1){
                $('#p-webusername').html("昵称:" + String(webusername) + "&nbsp&nbsp<button data-toggle='modal' data-target='#changun' type='button' class='btn btn-primary btn-xs'><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button>");
                $('#oldwebusername').val(String(webusername));
                $('#changun').modal('hide');
            }else{
                $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>修改失败</p></div>");
                $('#errorinfo').fadeIn();
            }
        }
    })
}


/************* 刷新个人页面订单详情 ************/
function refresh_userflow() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url: '/fresh_userflow/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value
        }, dataType: 'text',
        success: function (data) {
           $('#mobile-userflow').html(data)
        }
    })
}


/********  地址管理modal *************/
$('#adminaddressModal').on('show.bs.modal', function (event) {
    innerloading('adminaddress-content');
    refreshen_myaddress()
})


function refreshen_myaddress(){
    $.ajax({
        url: '/freshen_myaddress/',
        type: 'GET',
        dataType: 'text',
        success: function (data) {
            $('#adminaddress-content').html(data)
        }
    })
}

/****  编辑地址  ***/
function edit_address(ths,addressid) {
    var btnnode = ths.parentNode;
    var edit_input = btnnode.parentNode.parentNode.getElementsByClassName('form-control')[0];
    edit_input.disabled = false;
    edit_input.focus();
    btnnode.innerHTML = "<button class='btn btn-default' type='button' onclick='submit_address(this," + String(addressid) + ")'><span class='glyphicon glyphicon-ok' aria-hidden='true'></span></button>\n" +
                        "<button class='btn btn-default' type='button' onclick='refreshen_myaddress()'><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button>"
}


/**** 确认地址 ***/
function submit_address(ths,addressid) {
    var btnnode = ths.parentNode;
    var edit_input = btnnode.parentNode.parentNode.getElementsByClassName('form-control')[0];
    var address = edit_input.value;
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    if(!address){
        $('#addressmodal-message').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>地址不能为空</p></div>").fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_adminaddress/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'type':'edit',
            'address':address,
            'addressid':addressid
        }, dataType: 'json',
        success: function (data) {
            if(data.code === '1'){
                refreshen_myaddress()
            }else if(data.code === '500'){
                $('#addressmodal-message').html("<div id='myAlert' class='alert alert-danger'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>修改失败</p></div>").fadeIn()
            }
        }
    })
}


/**** 删除地址 ***/
function del_address(addressid){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url:'/ajax_adminaddress/',
        type:'POST',
        data:{
            'csrfmiddlewaretoken': csrf_value,
            'type':'del',
            'addressid':addressid
        },dataType:'json',
        success:function (data) {
            if(data.code === '1'){
                refreshen_myaddress()
            }else if(data.code === '500'){
                $('#addressmodal-message').html("<div id='myAlert' class='alert alert-danger'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>删除失败</p></div>").fadeIn();
            }
        }
    })
}

/******** 添加新地址 *******/
function add_address(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var address = $('#addaddress_input').val();
    if(!address){
        $('#addressmodal-message').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>地址不能为空</p></div>").fadeIn();
        return
    }
    $.ajax({
        url:'/ajax_adminaddress/',
        type:'POST',
        data:{
            'csrfmiddlewaretoken': csrf_value,
            'type':'add',
            'address':address
        },dataType:'json',
        success:function (data) {
            if(data.code === '1'){
                refreshen_myaddress()
            }else if(data.code === '500'){
                $('#addressmodal-message').html("<div id='myAlert' class='alert alert-danger'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>添加失败</p></div>").fadeIn();
            }else if(data.code === '501'){
                $('#addressmodal-message').html("<div id='myAlert' class='alert alert-danger'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>地址最多保持10个</p></div>").fadeIn();
            }
        }
    })
}


/****** submit 获取个人地址信息 *****/
    function refreshen_myaddressoption() {
        var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
        $.ajax({
            url: '/ajax_adminaddress/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_value,
                'type': 'get'
            }, dataType: 'json',
            success: function (data) {
                if(data.code === '1'){
                    var addresslist = data.addresslist;
                    var addressdom = $("#address");
                    addressdom.empty();
                    for(var i=0; addresslist.length >= i+1; i++){
                        var addressoptions = document.createElement("option");
                        addressoptions.text = addresslist[i];
                        addressoptions.setAttribute("value",addresslist[i]);
                        addressdom.append(addressoptions)
                    }
                }
            }
        })
    }


/*** 刷新用户管理界面个人收藏信息 ***/
function fresh_custcollect(custid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url: '/refreshen_tacollect/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'custid': custid
        }, dataType: 'json',
        success: function (data) {
            if(data.rcode === 1){
                var tbody = $('#custcollect-tbody');
                var collectlist = data.collectlist;
                for(var i=0;collectlist.length >=i;i++){
                    var tempelm = document.createElement('tr');
                    tempelm.innerHTML = "<td>" + String(collectlist[i].pid) + "</td>" +
                                        "<td><a href='/shop/product/" + String(collectlist[i].pid) + "'>" + collectlist[i].pname + "</a></td>" +
                                        "<td>" + collectlist[i].detail +"</td>" +
                                        "<td>" + collectlist[i].cdate + "</td>";
                    tbody.append(tempelm)
                }

            }
        }
    })
}

function buttonloading(thisbutton,time){
    if(time>0){
        time = time - 1;
        setTimeout(function(){thisbutton.html(String(time) + "s秒后再获取");buttonloading(thisbutton,time)},1000);
    }else{
        thisbutton.removeAttr("disabled");
        thisbutton.html("获取验证码")
    }
}


