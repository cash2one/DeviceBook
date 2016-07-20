function SpanGrid(tabObj, cellindex, beginRow) {
    var colIndex = cellindex;
    var rowBeginIndex = beginRow;
    if (tabObj != null) {
        var i, j, m;

        var intSpan;
        var strTemp;
        m = 0;
        for (i = rowBeginIndex; i < tabObj.rows.length; i++) {
            intSpan = 1;
            m++;
            strTemp = tabObj.rows[i].cells[colIndex].innerText;
            for (j = i + 1; j < tabObj.rows.length; j++) {
                if (strTemp == tabObj.rows[j].cells[colIndex].innerText) {
                    intSpan++;
                    tabObj.rows[i].cells[colIndex].rowSpan = intSpan;
                    tabObj.rows[j].cells[colIndex].style.display = "none";
                }
                else {
                    break;
                }
            }

        }
        i = j - 1;
    }
}
window.onload=function(){
 var tb=document.getElementById("tb");
 SpanGrid(tb,0,1)
SpanGrid(tb,1,1)
SpanGrid(tb,2,1)
SpanGrid(tb,3,1)
SpanGrid(tb,4,1)
SpanGrid(tb,5,1)
SpanGrid(tb,6,1)
SpanGrid(tb,7,1)
SpanGrid(tb,8,1)
SpanGrid(tb,9,1)
SpanGrid(tb,10,1)
SpanGrid(tb,11,1)


}
