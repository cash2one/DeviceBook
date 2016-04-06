function mysum(){

		var p = {};
		$("input[name='received']").each(function(){
    		var o = new Object()
			id=$(this).attr("id").substring(7);
			value=$(this).prop("checked");
				if (value){
					o.received=true; ;
				}else{
					o.received=false;
				}
			p[id]=o
		})

		 $("input[name='remarks']").each(function(){
			 var o = new Object()
			id=$(this).attr("id").substring(7);
			value=$(this).val();

			if (value){
				p[id].remarks=value;
			}else{
			p[id].remarks="";
			}
		})

		 $("input[name='deliver_date']").each(function(){
			 var o = new Object()
			id=$(this).attr("id").substring(12);
			value=$(this).val();
			if (value){
				p[id].deliver_date=value;
			}else{
			p[id].deliver_date=null;
			}
		})

        $("input[name='arrival_date']").each(function(){
			 var o = new Object()
			id=$(this).attr("id").substring(12);
			value=$(this).val();
			if (value){
				p[id].arrival_date=value;
			}else{
			p[id].arrival_date=null;
			}
		})

		var data = JSON.stringify(p);

		$.ajax({
				  type: 'POST',
				  url: '/_data',
				  data: {data:data},
				  dataType: 'json'
        });
        alert("提交成功");
        window.location.reload();
	}