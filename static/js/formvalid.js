/*
Jquery
janchie 2010.1
1.02版
*/

(function($){
$.fn.extend({
	valid:function(){
		if( ! $(this).is("form") ) return;

		var items = $.isArray(arguments[0]) ? arguments[0] : [],
		isBindSubmit = typeof arguments[1] ==="boolean" ? arguments[1] :true,
		isAlert = typeof arguments[2] ==="boolean" ? arguments[2] :false,

		rule = {
			"eng" : /^[A-Za-z]+$/,
			"chn" :/^[\u0391-\uFFE5]+$/,
			"mail" : /\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*/,
			"url" : /^http[s]?:\/\/[A-Za-z0-9]+\.[A-Za-z0-9]+[\/=\?%\-&_~`@[\]\':+!]*([^<>\"\"])*$/,
			"currency" : /^\d+(\.\d+)?$/,
			"number" : /^\d+$/,
			"int" : /^[0-9]{1,30}$/,
			"double" : /^[-\+]?\d+(\.\d+)?$/,
			"username" : /^[a-zA-Z]{1}([a-zA-Z0-9]|[._]){3,19}$/,
			"password" : /^[\w\W]{6,20}$/,
			"safe" : />|<|,|\[|\]|\{|\}|\?|\/|\+|=|\||\'|\\|\"|:|;|\~|\!|\@|\#|\*|\$|\%|\^|\&|\(|\)|`/i,
			"dbc" : /[ａ-ｚＡ-Ｚ０-９！＠＃￥％＾＆＊（）＿＋｛｝［］｜：＂＇；．，／？＜＞｀～　]/,
			"qq" : /[1-9][0-9]{4,}/,
			"date" : /^((((1[6-9]|[2-9]\d)\d{2})-(0?[13578]|1[02])-(0?[1-9]|[12]\d|3[01]))|(((1[6-9]|[2-9]\d)\d{2})-(0?[13456789]|1[012])-(0?[1-9]|[12]\d|30))|(((1[6-9]|[2-9]\d)\d{2})-0?2-(0?[1-9]|1\d|2[0-8]))|(((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00))-0?2-29-))$/,
			"year" : /^(19|20)[0-9]{2}$/,
			"month" : /^(0?[1-9]|1[0-2])$/,
			"day" : /^((0?[1-9])|((1|2)[0-9])|30|31)$/,
			"hour" : /^((0?[1-9])|((1|2)[0-3]))$/,
			"minute" : /^((0?[1-9])|((1|5)[0-9]))$/,
			"second" : /^((0?[1-9])|((1|5)[0-9]))$/,
			"mobile" : /^((\(\d{2,3}\))|(\d{3}\-))?13\d{9}$/,
			"phone" : /^[+]{0,1}(\d){1,3}[ ]?([-]?((\d)|[ ]){1,12})+$/,
			"zipcode" : /^[1-9]\d{5}$/,
			"IDcard" : /^((1[1-5])|(2[1-3])|(3[1-7])|(4[1-6])|(5[0-4])|(6[1-5])|71|(8[12])|91)\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$/,
			"ip" : /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/,		
			"file": /^[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/,
			"image" : /.+\.(jpg|gif|png|bmp)$/i,
			"word" : /.+\.(doc|rtf|pdf)$/i,

            "port":function(port){return (!isNaN(port) && port>0 && port<65536)? true:false;},
			"eq": function(arg1,arg2){ return arg1==arg2 ? true:false;},
			"gt": function(arg1,arg2){ return arg1>arg2 ? true:false;},
			"gte": function(arg1,arg2){ return arg1>=arg2 ? true:false;},
			"lt": function(arg1,arg2){ return arg1<arg2 ? true:false;},
			"lte": function(arg1,arg2){ return arg1<=arg2 ? true:false;}
			
		},

		msgSuffix = {
			"eng" : "only english welcomed" ,
			"chn" : "only chinese welcomed",
			"mail" : "invalid email format",
			"url" : "invalid url format",
			"currency" : "invalid number format",
			"number" : "only number welcomed",
			"int" : "only integer welcomed",
			"double" : "only float welcomed",
			"username" :"invalid username format,4-20 characters",
			"password" : "warning, you'd better use 6-20 characters",
			"safe" : "forbidden special characters",
			"dbc" : "forbidden full width characters",
			"qq" : "invalid qq format",
			"date" : "invalid date format",
			"year" : "invalid year format",
			"month" :"invalid month format",
			"day" : "invalid day format",
			"hour" : "invalid hour format",
			"minute" :"invalid minute format",
			"second" :"invalid second format",
			"mobile" : "invalid mobile format",
			"phone" : "invalid phone format",
			"zipcode" : "invalid zipcode format",
			"IDcard" : "invalid identity format",
			"ip" : "invalid ip format",
            "port" : "invalid port format",
			"file": "invalid file format",
			"image" : "invalid image format",
			"word" : "invalid word file format",
			"eq": "not equal",
			"gt": "no greater than",
			"gte": "no greater than or equal",
			"lt": "no smaller than",
			"lte": "no smaller than or equal"
		},

		msg = "", formObj = $(this) , checkRet = true, isAll,
		tipname = function(namestr){ return "tip_" + namestr.replace(/([a-zA-Z0-9])/g,"-$1"); },		

		typeTest = function(){
			var result = true,args = arguments;
			if(rule.hasOwnProperty(args[0])){
				var t = rule[args[0]], v = args[1];
				result = args.length>2 ? t.apply(arguments,[].slice.call(args,1)):($.isFunction(t) ? t(v) :t.test(v));
			}
			return result;
		},

		showError = function(fieldObj,filedName,warnInfo){
			checkRet = false;
			var tipObj = $("#"+tipname(filedName));
			if(tipObj.length>0) tipObj.remove();
			var tipPosition = fieldObj.next().length>0 ? fieldObj.nextAll().eq(this.length-1):fieldObj.eq(this.length-1);
            tipPosition.after("<span class='tooltip' id='"+tipname(filedName)+"'> "+warnInfo+" </span>");

			if(isAlert && isAll) msg = warnInfo;
		},

		showRight = function(fieldObj,filedName){
			var tipObj = $("#"+tipname(filedName));
			if(tipObj.length>0) tipObj.remove();
			var tipPosition = fieldObj.next().length>0 ? fieldObj.nextAll().eq(this.length-1):fieldObj.eq(this.length-1);
			tipPosition.after("<span class='tooltip' id='"+tipname(filedName)+"'>correct</span>");
		},

		findTo = function(objName){
			var find;
			$.each(items, function(){
				if(this.name == objName && this.simple){
					find = this.simple;	return false;
				}
			});
			if(!find) find = $("[name='"+objName+"']")[0].name;
			return find;
		},

		fieldCheck = function(item){
			var i = item, field = $("[name='"+i.name+"']",formObj[0]);
			if(!field[0]) return;

			var warnMsg,fv = $.trim(field.val()),isRq = typeof i.require ==="boolean" ? i.require : true;

			if( isRq && ((field.is(":radio")|| field.is(":checkbox")) && !field.is(":checked"))){
				warnMsg =  i.message|| "choice needed";
				showError(field ,i.name, warnMsg);

			}else if (isRq && fv == "" ){				
				warnMsg =  i.message|| ( field.is("select") ? "choice needed" :"not none" );
				showError(field ,i.name, warnMsg);

			}else if(fv != ""){
				if(i.min || i.max){
					var len = fv.length, min = i.min || 0, max = i.max;
					warnMsg =  i.message || (max? "range"+min+"~"+max+"":"min length"+min);

					if( (max && (len>max || len<min)) || (!max && len<min) ){
						showError(field ,i.name, warnMsg);	return;
					}
				}
				if(i.type){
					var matchVal = i.to ? $.trim($("[name='"+i.to+"']").val()) :i.value;
					var matchRet = matchVal ? typeTest(i.type,fv,matchVal) :typeTest(i.type,fv);

					warnMsg = i.message|| msgSuffix[i.type];
					if(matchVal) warnMsg += (i.to ? findTo(i.to) +"value" :i.value);

					if(!matchRet) showError(field ,i.name, warnMsg);
					else showRight(field,i.name);

				}else{
					showRight(field,i.name);
				}

			}else if (isRq){
				showRight(field,i.name);
			}
		
		},

		validate = function(){
			$.each(items, function(){isAll=true; fieldCheck(this);});
			
			if(isAlert && msg != ""){
				alert(msg);	msg = "";
			}
			return checkRet;
		};

		$.each(items, function(){			
			var field = $("[name='"+this.name+"']",formObj[0]);
			if(field.is(":hidden")) return;

			var obj = this,toCheck = function(){ isAll=false; fieldCheck(obj);};
			if(field.is(":file") || field.is("select")){
				field.change(toCheck);
			}else{
				field.blur(toCheck);
			}
		});		

		if(isBindSubmit) {
			$(this).submit(validate);
		}else{
			return validate();
		}
		
	}

});

})(jQuery);
