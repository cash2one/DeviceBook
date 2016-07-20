 <script type="text/javascript">
        function autoRowSpan(tableID, rowNumber, colNumber) {
            var lastValue = "";
            var value = "";
            var pos = 1;
            var i = rowNumber;
            $("#tbID .Acdtr").each(function () {
                value = $(this).children().eq(2).text();
                if (lastValue == value) {
                    tableID.rows[i].deleteCell(colNumber);
                    tableID.rows[i - pos].cells[colNumber].rowSpan = tableID.rows[i - pos].cells[colNumber].rowSpan + 1;
 
 
                    tableID.rows[i].deleteCell(1);
                    tableID.rows[i - pos].cells[1].rowSpan = tableID.rows[i - pos].cells[1].rowSpan + 1;
                    pos++;
                }
                else {
                    lastValue = value;
                    pos = 1;
                }
                i++;
            });
        }
	window.onload=function(){
 var tb=document.getElementById("tb");
"autoRowSpan(tb,1,6)

}	
 
    </script>