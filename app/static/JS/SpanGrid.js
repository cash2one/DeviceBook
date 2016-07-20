!function($){  
 $.fn.rowspan=function(options){  
 var defaults = {}  
 var options = $.extend(defaults, options);  
 this.each(function () {  
  
 var tds=$(this).find("tbody td:nth-child("+options.td+")");  
 var current_td=tds.eq(0);  
 var k=1;  
 tds.each(function(index, element) {  
 if($(this).text()==current_td.text()&&index!=0){  
 k++;  
 $(this).remove();  
 current_td.attr("rowspan",k);  
 current_td.css("vertical-align","middle");  
 }else{  
 current_td=$(this);  
 k=1;  
 }  
 });  
  
 })  
 }  
}( window.jQuery );
$("#my-table").rowspan({td:1});  