/*    全选    */
$("#allcb").change(function checkall() {
    if($("#allcb").is(":checked")){
        $('.ncheck').prop("checked",true);
    }else{
        $('.ncheck').prop("checked",false);
    }
})



/*    增减按钮    */
function inputcount(ths,type){
    var num_inputnode = ths.parentNode.getElementsByClassName('num')[0];
    var num_value = num_inputnode.value;
    if(type==="add"){
        num_value ++;
    }else{
        num_value --;
    }
    num_inputnode.value =num_value;
    fresh_sum()
}


/*** 确认sweetalter **/
function submit_sure(ths,swaltitle,swaltext) {
    var formdom = ths.form;
    swal({
        title:swaltitle,
        text: swaltext,
        icon: "info",
          buttons: {
            cancel: true,
            confirm: true
        },
        dangerMode: true
    }).then(function (result) {
        if(result){
            swal({  title: "Success!",
                text: "页面将会在2秒后跳转",
                icon: "success",
                button: "关闭"
            });
            setTimeout(function () {formdom.submit();},2000)
        }else{
            return false;
        }
    })

}


/* 获取管理页面左边链接 */
function getwebsite_leftinfo() {
    $.ajax({
        url: '/freshen_businessleft/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            if(data.rcode === 1){
                leftul = $('#website-leftul');
                var businessleft = data.businesslist;
                var searchleft = data.searchlist;
                leftul.append('<li class="nav-header">业务管理</li>');
                for(var i=0;businessleft.length>i;i++){
                    var newbusinessli = document.createElement('li');
                    newbusinessli.innerHTML = "<a href=" + businessleft[i].link + ">" + businessleft[i].name + "</a>";
                    leftul.append(newbusinessli)
                }
                leftul.append('<li class="nav-header">信息查询</li>');
                for(var j=0;searchleft.length>j;j++){
                    var newsearchli = document.createElement('li');
                    newsearchli.innerHTML = "<a href=" + searchleft[j].link + ">" + searchleft[j].name + "</a>";
                    leftul.append(newsearchli)
                }
            }
        }
    })
}


/***  出发下方按钮active  ***/
function navfooteractive(navid){
    var nav = document.getElementById(navid);
        nav.className = "navfooter-active"
}


/*   获取商店缓存   */
function getshopinfocache(){
    $.ajax({
      url:'/refresh_shopinfocache/',
      type:'GET',
      datatype:'json',
      success:function (data) {
          if(data.code === 1){
              var ipage = data.ipage;
              var pcls = data.pcls;
              var psize = data.psize;
              var thick = data.thick;
              var protlevel = data.thick;
              var brand = data.brand;
              var function_value = data.function_value;
              var get_search = data.get_search;
              var orderby = data.orderby;
              var orderasc = data.orderasc;
              if(psize||thick||protlevel){
                  $('#otherhide').attr('class','collapse in')
              }
              if(pcls){
                  changeshopselect('ul','ul-pcls',String(pcls))
              }
              if(brand){
                  changeshopselect('ul','ul-brand',brand)
              }
              if(function_value){
                  changeshopselect('ul','ul-function',function_value)
              }
              if(psize){
                  changeshopselect('select','psize',psize)
              }
              if(thick){
                  changeshopselect('select','thick',thick)
              }
              if(protlevel){
                  changeshopselect('select','protlevel',protlevel)
              }
              if(get_search){
                  $("input[name='search']").val(get_search)
              }
              if(ipage){
                  get_productdata(ipage,pcls,orderby,orderasc)
              }else{
                  get_productdata(1,pcls,orderby,orderasc)
              }
              $('.selectpicker').selectpicker('refresh')
          }else{
              get_productdata(1)
          }
      }
    })
}


/*  商店改变  */
function changeshopselect(type,sid,yourvalue){
    if(type === 'ul') {
        var sul = document.getElementById(sid);
        sul.getElementsByClassName('active')[0].removeAttribute('class');
        lidoms = sul.getElementsByTagName('li');
        for (var i = 1; i < lidoms.length; i++) {
            var livalue = lidoms[i].getAttribute('value');
            if (livalue === yourvalue) {
                lidoms[i].setAttribute('class','active');
            }
        }
    }else if(type === 'select'){
        var myselect = document.getElementById(sid);
        var options = myselect.getElementsByTagName('option');
        for(var j=0;j< options.length;j++){
            var optionvalue = options[j].getAttribute('value');
            if(optionvalue === yourvalue){
                options[j].selected = true;
            }
        }
    }
}


/*    获取商品信息    */
function get_productdata(page,pcls,orderby,asc){
	    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
        var search = $("input[name='search']").val();
        var thick = $('#thick').val();
        var psize = $('#psize').val();
        var protlevel = $('#protlevel').val();
        $('#shopinfo').empty();
        if(pcls&&pcls!=="None"){
            var ulpcls = document.getElementById('ul-pcls');
            var liactive = ulpcls.getElementsByClassName('active');
            liactive[0].removeAttribute("class");
        }
        var brand_dom = document.getElementById('ul-brand');
        var brand_value = brand_dom.getElementsByClassName('active')[0].getAttribute('value');
        var function_dom = document.getElementById('ul-function');
        var function_value = function_dom.getElementsByClassName('active')[0].getAttribute('value');
        $.ajax({
            url: '/freshen_shopinfo/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_value,
                'page': page,
                'search':search,
                'psize':psize,
                'thick':thick,
                'protlevel':protlevel,
                'brand':brand_value,
                'function':function_value,
                'pcls':pcls,
                'orderby':orderby,
                'asc':asc
            },dataType: 'text',
        success: function (data) {
                document.getElementById('shopinfo').innerHTML = data;
                document.getElementById('li-' + String(pcls)).className = "active";
                document.getElementById('btn_search').onclick = function(){get_productdata(1,pcls)};
                document.getElementById('btn_select').onclick = function(){get_productdata(1,pcls)};
                document.getElementById('unprice-sort').onclick = function () {get_productdata(1,pcls,'unprice',1)};
                document.getElementById('unprice-sorted').onclick = function () {get_productdata(1,pcls,'unprice',2)};

            }
        })
    }



function ajax_addcollect(ths,worktype) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var detailid = ths.getAttribute("dataid");
    var wtype = worktype;
    $.ajax({
        url: '/ajax_addcollect/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'detailid': detailid,
            'worktype': wtype
        },
		dataType:'json',
        success:function (data) {
            if (data.Msg === 'iscollect') {
                $(ths).html('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>已收藏');
				$(ths).attr('class','btn btn-success');
				$(ths).attr('onclick','ajax_addcollect(this,\'del\')')
				}
			else if (data.Msg === 'sudelete'){
                $(ths).html ('<span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>收藏');
				$(ths).attr('class','btn btn-warning');
				$(ths).attr('onclick','ajax_addcollect(this,\'add\')')
                }
            else if (data.Msg === 'sucollect') {
                $(ths).html('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>已收藏');
				$(ths).attr('class','btn btn-success');
				$(ths).attr('onclick','ajax_addcollect(this,\'del\')')
            }
            else if (data.Msg === 'nologin') {
				window.location.href="/login/";
			}
        }
    })
}


function ajax_sitecollect(ths,worktype) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var detailid = ths.getAttribute("dataid");
    var wtype = worktype;
    $.ajax({
        url: '/ajax_addcollect/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'detailid': detailid,
            'worktype': wtype
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'sudelete'){
                document.getElementById("div_collect" + detailid).remove();
            }
            else if (data.Msg === 'nologin') {
				window.location.href="/login/";
			}
        }
    })
}


function fresh_sum(){
    var alltotal = 0;
    var total_dom = document.getElementById('total');
    var tr_doms = document.getElementsByClassName('data_tr');
    for(var i=tr_doms.length-1;i>=0;i--){
        var tr_inputdom = tr_doms[i].getElementsByClassName('num')[0];
        var input_num = tr_inputdom.value;
        var input_unprice = tr_inputdom.getAttribute('unprice');
        var ths_total = input_num * input_unprice;
        tr_doms[i].getElementsByClassName('ths_total')[0].innerHTML = '￥' + String(ths_total);
        alltotal += ths_total
    }
        total_dom.innerHTML = '￥' + String(alltotal)
}


function ajax_addshopingcart(ths,worktype){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    if (worktype ==='buy'){
        var buynum = $('#productnum').val();
        var detailid = $('#btn_addshoppingcart').attr('dataid');
        var re = /^[0-9]+$/;
        if (!re.test(buynum)) {
            $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>数量必须是数字.</p></div>");
            $('#errorinfo').fadeIn();
            return
        }
        if (parseInt(buynum) <=0){
            $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>数量必须大于0.</p></div>");
            $('#errorinfo').fadeIn();
            return
        }
    }else if(worktype ==='del'){
        var buynum = null;
        var detailid = ths.getAttribute('scid');
    }
    var wtype = worktype;
    $.ajax({
        url: '/ajax_addshoppingcart/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'buynum' : buynum,
            'detailid': detailid,
            'worktype': wtype
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'buysucc'){
                $('#buyModal').modal('hide');
                $('#infomodal_title').text('成功');
                $('#infomodal_message').text('已成功加入到您的购物车!');
                $('#infomodal').modal('show');
            }
            else if (data.Msg === 'delsucc') {
                 ismobile = document.getElementsByClassName('mobilesc-aproduct');
                 ths.parentNode.parentNode.remove();
                 fresh_sum()

            }
            else if (data.Msg === 'nophone'){
                $('#buyModal').modal('hide');
                $('#infomodal_title').text('失败');
                $('#infomodal_message').html("<p class='text-danger'>对不起,需要现绑定手机才能购买.</p><a href='/website/userbindphone/'><span class='glyphicon glyphicon glyphicon-phone' aria-hidden='true'></span>前往绑定手机</a>")
                $('#infomodal').modal('show');
            }
            else if (data.Msg === 'uperr') {
                $('#buyModal').modal('hide');
                $('#infomodal_title').text('失败');
                $('#infomodal_message').html("<p class='text-danger'>数量必须大于0.</p>");
                $('#infomodal').modal('show');
            }
            else if (data.Msg === 'nologin') {
				window.location.href="/login/";
			}
			/*** 刷新购物车数量 ***/
			fresh_amount()
        }
    })
}


/*    异步提交订单    */
function submitorder() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var tr_doms = document.getElementsByClassName('data_tr');
    var tr_list = "{";
    for(var i=tr_doms.length-1;i>=0;i--){
        var tr_inputdom = tr_doms[i].getElementsByClassName('num')[0];
        var tr_buttom =tr_doms[i].getElementsByClassName('btn btn-danger')[0];
        var ths_num = parseInt(tr_inputdom.value);
        var ths_scid = tr_buttom.getAttribute('scid');
        tr_list = tr_list + '"' + String(ths_scid) + '":"' + String(ths_num) + '",'
    }
    tr_list += '}';

    $.ajax({
        url: '/ajax_submitorder/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'tr_list':tr_list
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'submitsucc'){
                window.location.href="submitshoppingcart/";
            }
            else if(data.Msg === 'uperr'){
                $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>数量必须大于0.</p></div>");
                $('#errorinfo').fadeIn();
                return
            }
        }
    })
}


$('#buyModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var dataid = button.data('dataid');
  var title  = button.data('title');
  var price  = button.data('price');
  var thick  = button.data('thick');
  var codsize= button.data('codsize');
  var unit   = button.data('unit');
  var Unum   = button.data('unum');
  var inventory = button.data('inventory');
  var protlevel = button.data('protlevel');
  var imgurl = button.data('pimg');
  var modal = $(this);
  var docstrong = document.createElement("strong");
  docstrong.innerHTML = price;
  docstrong.style.color = "indianred";
  docstrong.id = "unprice_value";

  $('#btn_addshoppingcart').attr('dataid',dataid);
  modal.find('.modal-title').text(title);
  modal.find('#p-uprice').text('单价:￥').append(docstrong);
  modal.find('#p-thick').text('厚度：' + thick);
  modal.find('#p-size').text('尺寸：' + codsize);
  modal.find('#p-protlevel').text('环保等级：' + protlevel);
  modal.find('#p-nmun').text('单件包装量：' + String(Unum) + unit);
  $('#productnum').val(1);

  modal.find('.img-thumbnail').attr('src',imgurl);
  //modal.find('.modal-body input').val(recipient)
  total_buymodal()
})




/*    删除订单信息订单信息modal    */
$('#delModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var fpid = button.data('fpid');
        var modal = $(this);
        modal.find('#btn_submitdel').attr('onclick','deleteflowproduct('+ String(fpid) +')')
    })


/*    信息modal infomoadl    */
function infomadal(mess,messclass){
    $('#infomodal_message').attr('class',messclass).text(mess)
}



/*    修改订单信息modal    */
$('#xModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var worktype = button.data('worktype');
    var fpid = button.data('fpid');
    var infoname = button.data('infoname');
    var detailname = button.data('detailname');
    var spnum = button.data('spnum');
    var sumprice = button.data('sumprice');
    var spunit = button.data('spunit');
    var spthick = button.data('spthick');
    var spsize = button.data('spsize');
    var protlevel = button.data('protlevel');
    var unprice = button.data('unprice');
    var unmun = button.data('unmun');
    var imgurl = button.data('imgurl');
    var detailid = button.data('detailid');
    var pinfoid = button.data('pinfoid');

    var modal = $(this);
    $("#s-productname").empty();
    $("#s-detail").empty();
    if (worktype === 'mod'){
        modal.find('.modal-title').text('修改');
        var infoop = document.createElement("option");
        var detailop = document.createElement("option");
        infoop.setAttribute("value", pinfoid);
        infoop.text = infoname;
        detailop.setAttribute("value", detailid);
        detailop.text = detailname;
        modal.find("#s-productname").append(infoop);
        modal.find("#s-detail").append(detailop);
    }else if (worktype === 'add'){
        modal.find('.modal-title').text('添加');
        var infoop = document.createElement("option");
        infoop.setAttribute("value", '');
        modal.find("#s-productname").append(infoop);
    }
    $.ajax({
        url: '/ajax_adminflowoperate/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype':'query-fp'
        },
        dataType: 'json',
    success: function (data) {
        if (data.Msg === 'succ') {
            var fplist = data.plist;
            for (var i = fplist.length - 1; i >= 0; i--) {
                var thsinfoop = document.createElement("option");
                thsinfoop.text = fplist[i][0];
                thsinfoop.setAttribute("value", fplist[i][1]);
                modal.find("#s-productname").append(thsinfoop);
                }
            }
        }
    })

    if (worktype === 'mod') {
        modal.find("#fp-change").val(fpid);
        modal.find("#p-unprice").val(unprice);
        modal.find("#p-thick").val(spthick);
        modal.find("#p-size").val(spsize);
        modal.find("#p-protlevel").val(protlevel);
        modal.find("#p-nmun").val(unmun);
        modal.find("#productnum").val(spnum);
        modal.find('.img-thumbnail').attr('src', imgurl);
        modal.find("#h3-total").text(sumprice);
        modal.find('#btn_submitxModal').attr('onclick','submitflowproduct()')
    }if(worktype === 'add'){
        $('#p-unprice').val("");
        $('#p-thick').val("");
        $('#p-size').val("");
        $('#p-protlevel').val("");
        $('#p-nmun').val("");
        $('#productnum').val("");
        modal.find("#h3-total").text('');
        modal.find('#btn_submitxModal').attr('onclick','addflowproduct()')
    }
})


/*    修改xmodal 商品名称事触发   */
 $("select#s-productname").change(function(){
     var productid = $(this).val();
     var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
     var custid = $('#p-username').attr('userid');
     $.ajax({
         url: '/ajax_adminflowoperate/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'query-pd',
             'productid':productid,
             'custid':custid
         },
         dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                var imgurl = data.imgurl;
                $('#modal-img').attr('src',imgurl);
                var dlist = data.dlist;
                $('#s-detail').empty();
                for (var i = 0; dlist.length >= i +1 ; i++) {
                    var thsdetailop = document.createElement("option");
                    thsdetailop.text = dlist[i][0];
                    thsdetailop.setAttribute("value", dlist[i][1]);
                    $("#s-detail").append(thsdetailop);
                }
                $("#p-unprice").val(data.unprice);
                $("#p-thick").val(data.thick);
                $("#p-size").val(data.psize);
                $("#p-protlevel").val(data.protlevel);
                $("#p-nmun").val(data.nmun);
                $("#productnum").val(1);
                $("#h3-total").text(data.unprice);
            }

        }
     })
 })



/*    修改xmodal 商品规格事触发   */
 $("select#s-detail").change(function(){
     var detailid = $("#s-detail").val();
     var custid = $('#p-username').attr('userid');
     var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
     $.ajax({
         url: '/ajax_adminflowoperate/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'query-detail',
             'detailid':detailid,
             'custid':custid
         },
         dataType: 'json',
        success: function (data) {
             if (data.Msg === 'succ') {
                 var unprice = data.unprice;
                 var thick = data.thick;
                 var psize = data.psize;
                 var protlevel = data.protlevel;
                 var nmun = data.nmun;
                 $("#p-unprice").val(unprice);
                 $("#p-thick").val(thick);
                 $("#p-size").val(psize);
                 $("#p-protlevel").val(protlevel);
                 $("#p-nmun").val(nmun);
                 $("#productnum").val(1);
                 $("#h3-total").text(unprice);
             }
         }
     })
 })


/*    确认修改订单商品信息   */
function submitflowproduct() {
    var custid = $('#p-username').attr('userid');
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var productid = $("#s-productname").val();
    var detailid = $("#s-detail").val();
    var unprice = $("#p-unprice").val();
    var thick = $("#p-thick").val();
    var psize = $("#p-size").val();
    var protlevel = $("#p-protlevel").val();
    var nmun = $("#p-nmun").val();
    var productnum = $("#productnum").val();
    var fpid = $("#fp-change").val();
    var flowid = $("#flowid").attr('flowid');
    var renum = /^[0-9]+$/;
    var reunprice = /^[0-9]+\.?[0-9]*$/;
    if(!renum.test(productnum)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>数量必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!renum.test(nmun)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>每件数量必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!reunprice.test(unprice)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>单价格式有误.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_adminflowoperate/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'save-fp',
            'detailid': detailid,
            'custid': custid,
            'productid':productid,
            'unprice':unprice,
            'thick':thick,
            'psize':psize,
            'protlevel':protlevel,
            'nmun':nmun,
            'productnum':productnum,
            'flowid':flowid,
            'fpid':fpid
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }else if(data.Msg === 'error') {
                infomadal(data.errmsg, 'bg-danger');
                $('#infomodal').modal('show');
            }
        }
    })

}

/*    确认添加订单商品信息   */
function addflowproduct() {
    var custid = $('#p-username').attr('userid');
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var productid = $("#s-productname").val();
    var detailid = $("#s-detail").val();
    var unprice = $("#p-unprice").val();
    var thick = $("#p-thick").val();
    var psize = $("#p-size").val();
    var protlevel = $("#p-protlevel").val();
    var nmun = $("#p-nmun").val();
    var productnum = $("#productnum").val();
    var flowid = $("#flowid").attr('flowid');
    var renum = /^[0-9]+$/;
    var reunprice = /^[0-9]+\.?[0-9]*$/;
    if(!renum.test(productnum)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>数量必须是数字.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!renum.test(nmun)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>每件数量必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!reunprice.test(unprice)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>单价格式有误.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
     $.ajax({
         url: '/ajax_adminflowoperate/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'add-fp',
             'detailid': detailid,
             'custid': custid,
             'productid':productid,
             'unprice':unprice,
             'thick':thick,
             'psize':psize,
             'protlevel':protlevel,
             'nmun':nmun,
             'productnum':productnum,
             'flowid':flowid
         },
         dataType: 'json',
         success: function (data) {
            if (data.Msg === 'succ'){
            window.location.reload();
            }else if(data.Msg === 'error'){
                infomadal(data.errmsg,'bg-danger');
                $('#infomodal').modal('show');
            }
        }
    })
}


/*    删除订单商品信息   */
function deleteflowproduct(fpid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url: '/ajax_adminflowoperate/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'del-fp',
            'fpid': fpid
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }else if(data.Msg === 'error'){
                swal({  title: "error!",
                        text: "删除失败，您没有足够的权限！",
                        icon: "error",
                        button: "关闭"
                    });
            }
        }
    })
}


/*    审核订单不通过   */
function auditerror() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var flowid = $("#flowid").attr('flowid');
    var carryprice = $("#input_Carryprice").val();
    var iscarryprice = $("#iscarryprice").is(":checked");
    $.ajax({
        url: '/ajax_adminflowoperate/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'aud-fp',
            'flowid':flowid,
            'carryprice':carryprice,
            'iscarryprice':iscarryprice
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }else if(data.Msg === 'error'){
                infomadal(data.errmsg,'text-danger');
                $('#infomodal').modal('show');
            }
        }
    })
}


/****  运费修改  ****/
function changecarryprice() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var flowid = $("#flowid").attr('flowid');
    var carryprice = $('#input_Carryprice').val();
    var iscarryprice = $('#iscarryprice').val();
    $.ajax({
        url: '/ajax_adminflowoperate/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'save-cp',
            'flowid':flowid,
            'carryprice':carryprice,
            'iscarryprice':iscarryprice
        },
        dataType: 'json',
        success: function (data) {
            if (data.code === 1) {
                swal({  title: "Success!",
                        text: "修改成功！",
                        icon: "success",
                        button: "关闭"
                    });
                fresh_ordertotal()
            }else if(data.code === 99){
                swal({  title: "error!",
                        text: "删除失败，您没有足够的权限！",
                        icon: "error",
                        button: "关闭"
                    });
            }
        }
    })

}




/* change detail ajax */
function changedetail(detailid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var dunit = $("[name$='dunit']").val();
    var dthick = $("[name$='dthick']").val();
    var dsize = $("[name$='dsize']").val();
    var protlevel = $("[name$='dprotlevel']").val();
    var dnmun = $("[name$='dnmun']").val();
    var inventory = $("[name$='dinventory']").val();
    var unprice = $("[name$='dunPrice']").val();
    var brand = $("[name$='brand']").val();
    var func = $("[name$='func']").val();
    var iscover = $("[name$='iscover']").is(":checked");
    var renum = /^[0-9]+$/;
    var reunprice = /^[0-9]+\.?[0-9]*$/;
    if(!renum.test(dnmun)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>每件数量必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!renum.test(inventory)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>库存必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!reunprice.test(unprice)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>单价格式有误.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_adminproduct/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'mod-detail',
            'detailid': detailid,
            'dunit': dunit,
            'dthick':dthick,
            'dsize':dsize,
            'protlevel':protlevel,
            'dnmun':dnmun,
            'inventory':inventory,
            'unprice':unprice,
            'brand':brand,
            'func':func,
            'iscover':iscover
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }else if(data.Msg === 'nologin'){
                window.location.href="/login/";
            }
        }
    })
}



/* 添加商品类型 */
function addpcls() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var clsname = $('#addpcls-input').val();
    $.ajax({
        url: '/ajax_adminproduct/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'add-pcls',
            'clsname': clsname
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                var clsid = data.clsid;
                var clsselectdom = $('#productclass');
                var newclsoption = document.createElement('option');
                newclsoption.value = clsid;
                newclsoption.innerText = clsname;
                clsselectdom.append(newclsoption);
                newclsoption.selected = true;
                $('#addpclsmodal').modal('hide');
                swal('成功!', '添加成功.', 'success')
            }else if (data.Msg === 'norule') {
                alert("没有足够权限")
            }
        }
    })
}


/* add detail ajax */
function adddetail(productid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var dunit = $("[name$='dunit']").val();
    var dthick = $("[name$='dthick']").val();
    var dsize = $("[name$='dsize']").val();
    var protlevel = $("[name$='dprotlevel']").val();
    var dnmun = $("[name$='dnmun']").val();
    var inventory = $("[name$='dinventory']").val();
    var unprice = $("[name$='dunPrice']").val();
    var brand = $("[name$='brand']").val();
    var func = $("[name$='func']").val();
    var renum = /^[0-9]+$/;
    var reunprice = /^[0-9]+\.?[0-9]*$/;
    if(!renum.test(dnmun)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>每件数量必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!renum.test(inventory)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>库存必须是整数.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    if(!reunprice.test(unprice)){
        $('#errorinfo').html("<div id='myAlert' class='alert alert-warning'><a href='#' class='close' data-dismiss='alert'>&times;</a><p>单价格式有误.</p></div>");
        $('#errorinfo').fadeIn();
        return
    }
    $.ajax({
        url: '/ajax_adminproduct/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'add-detail',
            'productid': productid,
            'dunit': dunit,
            'dthick':dthick,
            'dsize':dsize,
            'protlevel':protlevel,
            'dnmun':dnmun,
            'inventory':inventory,
            'unprice':unprice,
            'func':func,
            'brand':brand
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            }else if(data.Msg === 'nologin'){
                window.location.href="/login/";
            }
        }
    })
}


/* detailmodal */
$('#detailModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var detailid = button.data('detailid');
    var productid = $("#productid").text();
    var modal = $(this);
    if(detailid){
        $("[name$='iscover']").prop("checked",false).removeAttr("disabled","");
        $("[name$='brand']").val(button.data("brand"));
        $("[name$='func']").val(button.data("func"));
        $("[name$='dunit']").val(button.data("dunit"));
        $("[name$='dthick']").val(button.data("dthick"));
        $("[name$='dsize']").val(button.data("dsize"));
        $("[name$='dprotlevel']").val(button.data("dprotlevel"));
        $("[name$='dnmun']").val(button.data("dunmun"));
        $("[name$='dinventory']").val(button.data("dinventory"));
        $("[name$='dunPrice']").val(button.data("unprice"));
        $("#detail-commit").attr("onclick","changedetail(" + String(detailid) + ")")
    }else{
        $("[name$='brand']").val("");
        $("[name$='func']").val("");
        $("[name$='dunit']").val("");
        $("[name$='dthick']").val("");
        $("[name$='dsize']").val("");
        $("[name$='dprotlevel']").val("");
        $("[name$='dnmun']").val("");
        $("[name$='dinventory']").val("");
        $("[name$='dunPrice']").val("");
        $("[name$='iscover']").prop("checked",false).attr("disabled","");
        $("#detail-commit").attr("onclick","adddetail(" + String(productid) + ")")
    }
});


/* 删除规格或商品 */
function jsdeleteproduct(worktype) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var doms_checked = document.getElementsByClassName("ncheck");
    var deletelist = new Array();
    var j = 0;
    for (var i = doms_checked.length - 1; i >= 0; i--) {
        if (doms_checked[i].checked) {
            deletelist[j] = doms_checked[i].value;
            j++
        }
    }
    $.ajax({
        url: '/ajax_adminproduct/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': worktype,
            'deletelist': JSON.stringify(deletelist)
        },
        dataType: 'json',
        success: function (data) {
            if (data.Msg === 'succ') {
                window.location.reload();
            } else if (data.Msg === 'nologin') {
                window.location.href = "/login/";
            } else if (data.Msg === 'norule') {
                alert("没有足够权限")
            }
        }
    })
}


/*   添加新闻类型   */
function addnewscls(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var newscls = $("input[name='newscls']").val();
    var worktype = 'addcls';
    $.ajax({
        url: '/ajax_adminnews/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': worktype,
            'newscls':newscls
        },
        dataType: 'json',
        success: function (data) {
            if(data.rcode === 1){
                window.location.reload();
            }
        }
    })
}


/******* 删除新闻信息 *******/
function delnews(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var doms_checked = document.getElementsByClassName("ncheck");
    var deletelist = new Array();
    var j = 0;
    for (var i = doms_checked.length - 1; i >= 0; i--) {
        if (doms_checked[i].checked) {
            deletelist[j] = doms_checked[i].value;
            j++
        }
    }
    $.ajax({
        url: '/ajax_adminnews/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'deletelist': json.stringify(deletelist),
            'worktype':'delnews'
        },
        dataType: 'json',
        success: function (data) {
            if(data.rcode === 1){
                window.location.reload();
            }
        }
    })
}


/*   刷新购物车数量   */
function fresh_amount() {
    $.ajax({
        url: '/fresh_amount/',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#showAmount').text(data.amount)
        }
    })
}

/*** 刷新订单详情页面中的商品  ***/
function refreshmyflowproduct(flowid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    innerloading('flowproductinfo');
    $.ajax({
        url: '/freshen_myshowflow/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'flowid':flowid
        },
        dataType:'text',
        success:function (data) {
            $('#flowproductinfo').html(data);
            /*  计算价格  */
            var unprice_doms = document.getElementsByClassName('unprice');
            var product_total = 0;
            for(var i=unprice_doms.length -1; i>=0 ;i--){
                var ths_unprice = unprice_doms[i].innerText;
                ths_unprice = ths_unprice.replace("￥",'');
                product_total += parseFloat(ths_unprice)
            }
            var carryprice = parseFloat(document.getElementById('carryprice').innerText);
            document.getElementById('productprice').innerText = product_total.toFixed(2);
            document.getElementById('totalprice').innerText = (product_total + carryprice).toFixed(2)
        }
    })
}



/*** 推荐商品管理 ***/
function admingetcommend() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url:'/ajax_admincommend/',
        type:'POST',
        data:{
            'csrfmiddlewaretoken': csrf_value,
            'worktype':'get'
        },
        dataType:'json',
        success:function(data){
            if(data.rcode === '1'){
                var commendlist = data.commendlist;
                commendlist_html = "";
                htmlhead = "<div class='admincommendrow'>";
                htmlfoot = "</div>";
                for(var i=0;i<commendlist.length;i++){
                    htmlbody = "<div class='admin-commenddrag'>&nbsp<input class='admin-commendinput' value='" + String(commendlist[i].cindex) + "' detailid='" + String(commendlist[i].pid) + "'></div>" +
                                "<div class='admin-commendname'>&nbsp" + commendlist[i].pname + "</div>" +
                                "<div class='admin-commendline'>&nbsp" +  commendlist[i].prcls  + "</div>" +
                                "<div class='admin-commendline'>&nbsp" + commendlist[i].brand + "</div>" +
                                "<div class='admin-commenddetail'>&nbsp" + commendlist[i].thick + "\\" + commendlist[i].psize + "\\" + commendlist[i].protlevel + "</div>" +
                                "<div class='admin-commendbutton'><a class='btn btn-default' role='button' onclick=\"admindelcomend(this,'" + String(commendlist[i].cid) + "')\"><span class='glyphicon glyphicon-trash' aria-hidden='true'></span></a></div>";
                    commendlist_html += htmlhead  + htmlbody + htmlfoot
                }
                document.getElementById('admincommend-body').innerHTML = commendlist_html;
            }
        }
    })
}


/**** 推荐商品删除 ****/
function admindelcomend(ths,commendid) {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    $.ajax({
        url:'/ajax_admincommend/',
        type:'POST',
        data:{
            'csrfmiddlewaretoken': csrf_value,
            'worktype':'del',
            'commendid':commendid
        },
        dataType:'json',
        success:function(data){
            if(data.rcode === '1'){
                ths.parentNode.parentNode.remove()
            }else if (data.rcode === '97'){
                alert('删除失败');
            }
        }
    })
}


/*   添加商品修改select   */
 $("select#addcommend-product").change(function() {
     var productid = $(this).val();
     var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
     $.ajax({
         url: '/ajax_admincommend/',
         type: 'POST',
         data: {
             'csrfmiddlewaretoken': csrf_value,
             'worktype': 'detail',
             'productid': productid
         },
         dataType: 'json',
         success: function (data) {
            if(data.rcode === '1'){
                var datalist = data.details;
                var detailselect = $('#addcommend-detail');
                detailselect.empty();
                for(var i=0;i<datalist.length;i++){
                    var optionelement = document.createElement('option');
                    optionelement.value = datalist[i].id;
                    optionelement.text = datalist[i].name;
                    detailselect.append(optionelement)
                }
            }
         }
     })
 })



function addcommend() {
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var detailid = $('#addcommend-detail').val();
    $.ajax({
        url: '/ajax_admincommend/',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'add',
            'detailid': detailid
        },
        dataType: 'json',
        success: function (data) {
            if(data.rcode === '1'){
                admingetcommend();
                $('#addcommendModal').modal('hide')

            }else if(data.rcode === '96'){
                alter('添加失败!')
            }
        }
    })
}


/**  保存推荐商品信息  ***/
function savecommend(){
    var csrf_value = $("input[name='csrfmiddlewaretoken']").val();
    var commendarray = new Array();
    var commenddoms = document.getElementsByClassName('admin-commendinput');
    var cindex = "";
    var detailid = "";
    for(var i=0;i<commenddoms.length;i++){
        cindex = commenddoms[i].value;
        detailid = commenddoms[i].getAttribute('detailid');
        commendarray[i] = String(cindex) + "&" + String(detailid)
    }
    $.ajax({
        cache:false,
        url: '/ajax_admincommend/',
        type: 'POST',
        traditional:true,
        data: {
            'csrfmiddlewaretoken': csrf_value,
            'worktype': 'save',
            'commendlist': commendarray
        },
        dataType: 'json',
        success: function (data) {
            if(data.rcode === '1') {
                admingetcommend();
            }else{
                alter('更新失败！')
            }
        }
    })

}



/* loading  */
function innerloading(domid) {
    document.getElementById(domid).innerHTML ="<div class=\"myloading\">\n" +
        "                   <div class=\"loading-container\">\n" +
        "                        <div class=\"shape shape-1\"></div>\n" +
        "                        <div class=\"shape shape-2\"></div>\n" +
        "                        <div class=\"shape shape-3\"></div>\n" +
        "                        <div class=\"shape shape-4\"></div>\n" +
        "                    </div>\n" +
        "                   </div>"
}



/*    浏览图片Modal   */
$('#imgModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var imgurl = button.data('imgurl');
    var modal = $(this);
    modal.find('#imgInModalID').attr('src', imgurl);
})


