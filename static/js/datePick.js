/*
 * $-color 0.1 - New Wave Javascript
 *
 * Copyright (c) 2008 King Wong

 * $Date: 2008-10-3  $
 */
(function($){
	var ___d = new Date();
	var ___tem___ = ___d.getTime();
	var _sobj;
	$.extend({
		selectDateSettings:{
			date:___d.getFullYear()+"-"+(___d.getMonth()+1)+"-"+___d.getDate(),
			//startYear:___d.getFullYear()-20,
			startYear:___d.getFullYear(),
			endYear:___d.getFullYear()+1,
			dateFormat:"yyyy-mm-dd",
			target:window.self
		},
		selectDateSetup: function( settings ) {
			$.extend( $.selectDateSettings, settings );
		}
	})
	$.fn.extend({
		selectDate:function(){
			var _d = new Date();
			//var ___tem___ = _d.getTime();
			var nowDate = eval("new Date("+$.selectDateSettings.date.replace(new RegExp("-","gm"),",")+")");
			nowDate.setMonth(nowDate.getMonth()-1);
			return this.each(function(){
				var __showDate = function(_obj)
				{
					var _strYear = new Array();
					var _strMonth = new Array();
					var _mon = new Array('1','2','3','4','5','6','7','8','9','10','11','12');
					var _left = parseInt($(_obj).offset().left);
					var _top = parseInt($(_obj).offset().top);
					var _width = parseInt($(_obj).width());
					var _height = parseInt($(_obj).height());
					
					var _maxindex = function(){
						var ___index = 0;
						$.each($("*",$.selectDateSettings.target.document),function(i,n){
							 var __tem = $(n,$.selectDateSettings.target.document).css("z-index");
							 if(__tem>=0)
							 {
								if(__tem >= ___index)
								{
									___index = __tem + 1;	
								}
							 }
						 });
						return ___index;
					}();
					
					for(var i = 0 ; i < 12 ; i++)
					{
						if(i == nowDate.getMonth())
						{
							_strMonth.push('<option value="'+(i+1)+'" selected="selected">'+_mon[i]+'</option>');
						}
						else
						{
							_strMonth.push('<option value="'+(i+1)+'">'+_mon[i]+'</option>');
						}
					}
					for(var j = $.selectDateSettings.startYear ; j <= $.selectDateSettings.endYear ; j++)
					{
						if(j == nowDate.getFullYear())
						{
							_strYear.push('<option value="'+j+'" selected="selected">'+j+'</option>');
						}
						else
						{
							_strYear.push('<option value="'+j+'">'+j+'</option>');
						}
					}
					var getDayStr = function(y,m)
					{
						var year;
						var month;
						var nextyear;
						var nextmonth;
						if(y=="" || y==undefined)
						{
							year = parseInt($("select[id=year_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val());
							month = parseInt($("select[id=mon_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val());
						}
						else
						{
							year = parseInt(y);
							month = parseInt(m);
						}
						if(year==0){
							year = nowDate.getFullYear();
							month = nowDate.getMonth()+1;
						}
						var _selectD;
						if(month==0){
							_selectD = new Date(year-1,11,1);
						}else{
							_selectD = new Date(year,month-1,1);
						}
						if(month==12){
							nextyear = year+1;
							nextmonth = 0;
						}
						else
						{
							nextyear = year;
							nextmonth = month;
						}
						var _nextD = new Date(nextyear,nextmonth,1);
						var __day = parseInt(Math.abs(_nextD - _selectD) / 1000 / 60 / 60 /24);
						var __str__ = new Array();
						__str__.push('<tr>');
						for(var ii = 0 ; ii < _selectD.getDay(); ii++)
						{
							__str__.push('<td width="22" align="center" valign="middle" bgcolor="#EDF2FC">&nbsp;</td>');
						}
						for(var nn = 1 ; nn <= __day; nn++)
						{
							var _DD_ = new Date(year,month-1,nn);
							__str__.push('<td width="22" align="center" valign="middle" style="cursor:pointer; background-color:#EDF2FC;" mce_style="cursor:pointer; background-color:#EDF2FC;" class="king_date_css" onmouseover="this.style.backgroundColor=\'red\';" onmouseout="this.style.backgroundColor=\'#EDF2FC\';">'+nn+'</td>');
							if(_DD_.getDay()==6)
							{
								__str__.push('</tr>');
								if(nn<__day)
								{
									__str__.push('<tr>');
								}
							}
						}
						var __NN__ = _selectD.getDay() + __day;
						var __mod__ = __NN__%7
						if(__mod__!=0){
							for(var mm = 0 ; mm < (7-__mod__) ; mm++)
							{
								__str__.push('<td width="22" align="center" valign="middle" bgcolor="#EDF2FC">&nbsp;</td>');
							}
							__str__.push('</tr>');
						}
						return '<table cellpadding="0" style="margin:0 auto; width:150px;" cellspacing="1" style="background-color:#CCCCCC; font-size:12px;" mce_style="background-color:#CCCCCC; font-size:12px;"><tr><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">日</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">一</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">二</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">三</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">四</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">五</td><td width="22" align="center" valign="middle" bgcolor="#EDF2FC">六</td></tr>'+__str__.join("")+'</table>';
					}
					var __changeDate = function()
					{
						$("#daystr_"+___tem___,$.selectDateSettings.target.document).empty();
						$("#daystr_"+___tem___,$.selectDateSettings.target.document).append(getDayStr());
						$(".king_date_css",$.selectDateSettings.target.document).click(function(){
							var _y_ = $("select[id=year_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val();
							var _m_ = $("select[id=mon_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val();
							var _d_ = $(this).text();
							_m_ = _m_.length < 2 ? "0"+_m_ : _m_;
							_d_ = _d_.length < 2 ? "0"+_d_ : _d_;
							var returndate = $.selectDateSettings.dateFormat.replace("yyyy",_y_).replace("mm",_m_).replace("dd",_d_);
							$(_obj).val(returndate);
						});
					}
					var _str = '<div id="dateShowDiv_'+___tem___+'" style="width:164px;position:absolute;z-index:'+_maxindex+';left:'+(_left+_width-200)+'px;top:'+(_top+_height)+'px;border:1px solid #990;"><table cellpadding="0" cellspacing="0" width="164" style="background-color:#EDF2FC;" mce_style="background-color:#EDF2FC;"><tr><td><table cellpadding="0" cellspacing="1" style="background-color:#EDF2FC; font-size:12px; width:100%;"><tr style="height:25px;"><td>&nbsp; <select id="year_'+___tem___+'">'+_strYear.join("")+'</select> 年 </td><td><select id="mon_'+___tem___+'">'+_strMonth.join("")+'</select> 月 </td></tr></table></td></tr><tr><td><span id="daystr_'+___tem___+'"></span></td></tr><tr>  <td><div style="text-align:center; height:22px; line-height:22px; float:left; margin-left:15px;"><a href="javascript:void(null);" mce_href="javascript:void(null);" id="currentdate_'+___tem___+'" style="font-size:12px; text-align:center; text-decoration:none;" mce_style="font-size:12px; text-align:center; text-decoration:none;">选择今天</a></div><a href="javascript:;" mce_href="javascript:;" id="selectDateClose_'+___tem___+'" style="background:url(images/tab-close.gif); width:12px; height:12px;display:block;float:right; margin:5px 5px 0 0;" title="close"></a></td></tr></table></div>';
					$("body",$.selectDateSettings.target.document).append(_str);
					$("#daystr_"+___tem___,$.selectDateSettings.target.document).append(getDayStr());
					$("#year_"+___tem___,$.selectDateSettings.target.document).change(function(){
						__changeDate();
					});
					$("#mon_"+___tem___,$.selectDateSettings.target.document).change(function(){
						__changeDate();
					});
					$(".king_date_css",$.selectDateSettings.target.document).click(function(){
						var _y_ = $("select[id=year_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val();
						var _m_ = $("select[id=mon_"+___tem___+"] option[selected]",$.selectDateSettings.target.document).val();
						var _d_ = $(this).text();
						_m_ = _m_.length < 2 ? "0"+_m_ : _m_;
						_d_ = _d_.length < 2 ? "0"+_d_ : _d_;
						var returndate = $.selectDateSettings.dateFormat.replace("yyyy",_y_).replace("mm",_m_).replace("dd",_d_);
						$(_obj).val(returndate);
						$("#dateShowDiv_"+___tem___,$.selectDateSettings.target.document).remove();
					});
					$("#currentdate_"+___tem___,$.selectDateSettings.target.document).click(function(){
						var _m_ = (nowDate.getMonth()+1).toString();
						var _d_ = nowDate.getDate().toString();
						_m_ = _m_.length < 2 ? "0"+_m_ : _m_;
						_d_ = _d_.length < 2 ? "0"+_d_ : _d_;
						var returndate = $.selectDateSettings.dateFormat.replace("yyyy",nowDate.getFullYear()).replace("mm",_m_).replace("dd",_d_);
						$(_obj).val(returndate);
						$("#dateShowDiv_"+___tem___,$.selectDateSettings.target.document).remove();
					});
					$("#selectDateClose_"+___tem___,$.selectDateSettings.target.document).click(function(){
					$("#dateShowDiv_"+___tem___,$.selectDateSettings.target.document).remove();
				});
				}
				
				$(this).click(function(){
					$("#dateShowDiv_"+___tem___,$.selectDateSettings.target.document).remove();
					_sobj = this;
					__showDate(_sobj);
				});
			});
			
		}
	});
	$($.selectDateSettings.target.document).click(function(e){
		e = e ? e : window.event;
		var tag = e.srcElement || e.target;
		if(_sobj && _sobj.id==tag.id)return false;
		var _temObj = tag;
		while(_temObj)
		{
			if(_temObj.id=="dateShowDiv_"+___tem___)return;
			_temObj = _temObj.parentNode;
		}
		$("#dateShowDiv_"+___tem___,$.selectDateSettings.target.document).remove();			   
	});
})(jQuery);// JavaScript Document