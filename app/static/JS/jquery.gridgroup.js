/*
*gridgroup���������
*         head�����飬ָ��ͷ���з��飬����ֵԽ��ǰ���������ȼ�Ҳ�ߡ���ͷ�����飬���Ϊnull��Ĭ�Ϸ��顣
*         column�����飬ָ�������з��飬����ֵԽ��ǰ���������ȼ�Խ�ߡ����Ϊnull��Ĭ�Ϸ��顣
*         ע�⣺ָ����head��ʽ�����column���齫��Ч��head���ȼ�����column�����������Ҫ�з��飬headֵ����null
* @method group(head,column) ���������÷��������������������»��Ʒ��鱨�����ݡ�
*         head��ͬ��
*         column��ͬ��
* @���� �Ĵ�����  
* ˵�����ڱ�js�Ļ����޸ģ��뱣��������Ϣ��
*/
(function ($) {
    $.fn.extend({
        gridgroup: function (options) {
            //��ȡ�����


            var gridConfig = this.data["tableData"];
            //��ʼ�������


            if (!gridConfig) {
                //��ͷ


                var heads = [];
                //������


                var columns = [];
                var $table = $(this);

                var $trs = $("thead tr", $(this));
                for (var i = 0; i < $("th", $($trs[0])).length; i++) {
                    var ch = [];
                    $.each($trs, function () {
                        ch.push($(this).find("th")[i].innerText);
                    });
                    heads.push(ch);
                }

                $("tbody tr", $table).each(function () {
                    var column = [];
                    $(this).find("td").each(function () {
                        column.push(this.innerText);
                    });
                    columns.push(column);
                });
                this.data["tableData"] = {
                    heads: heads,
                    columns: columns
                }
                gridConfig = this.data["tableData"];
            }
            //��������


            function analyse(data,hcconfig) {
                var hc = [];
                var hcindex = [];
                if (hcconfig) {
                    $.each(hcconfig.zindex, function (hczindex) {
                        var zconfig = hcconfig.hc[hczindex];
                        var zhcindex = [];
                        var zhc = [];
                        for (var index = 0; index < data.length; index++) {
                            if (checkArray(index, zconfig.index) > -1) {
                                if (checkArray(data[index], zhcindex) < 0) {
                                    zhc.push({
                                        index: [],
                                        parent: hczindex
                                    });
                                    zhcindex.push(data[index]);
                                }
                                zhc[checkArray(data[index], zhcindex)].index.push(index);
                            }
                        }
                        $.merge(hc, zhc);
                        $.merge(hcindex, zhcindex);
                    });
                } else {
                    for (var index = 0; index < data.length; index++) {
                        
                        if (checkArray(data[index], hcindex) < 0) {
                            hc.push({
                                index: []
                            });
                            hcindex.push(data[index]);
                        }
                        hc[checkArray(data[index], hcindex)].index.push(index);
                    }
                }
                var index = [];
                for (var hczindex = 0; hczindex < hcindex.length; hczindex++) {
                    var cfindex=hc[hczindex].index;
                    $.merge(index, cfindex);
                }
                return {
                    index: index,
                    zindex:hcindex,
                    hc:hc
                };
            }
            function defaultanalyse(columnconfig, data) {

                var zhcindex = [];
                var zhc = [];
                if (!columnconfig) {
                    for (var i = 0; i < data.length;) {
                        var title = data[i];
                        var index = [];
                        for (var m = i; m < data.length; m++) {
                            if (title == data[m]) {
                                index.push(m);
                                i++;
                            } else {
                                break;
                            }
                        }
                        zhc.push({ index: index });
                        zhcindex.push(title);
                    }
                } else {
                    for (var i = 0; i < data.length;) {
                        var title = data[i];
                        var index = [];
                        var max = 0;
                        for (var ca = 0; ca < columnconfig.hc.length; ca++) {
                            max += columnconfig.hc[ca].index.length;
                            if (checkArray(i, columnconfig.hc[ca].index) >= 0) {
                                break;
                            }
                        }
                        for (var m = i; m < max; m++) {
                            if (title == data[m]) {
                                i++;
                                index.push(m);
                            } else {
                                break;
                            }
                        }
                        max = 0;
                        zhc.push({ index: index });
                        zhcindex.push(title);
                    }
                }
                
               return {
                    index: null,
                    zindex: zhcindex,
                    hc: zhc
                }
            }
            function checkArray(key, array) {
                var index=-1;
                for (var i = 0; i < array.length; i++) {
                    if (key == array[i]) {
                        index = i;
                        break;
                    }
                }
                return index+"";
            }

            //��ͷ���鷽��


            function groupHead(dom,head,headconfig,rowIndex) {
                var columnc;
                /****************ͷ������******************/
                var $thead = $("thead", dom);
                $thead.html("");

                if (!head) {
                    for (var h = 0; h < headconfig[0].length; h++) {
                        var hc = [];
                        $.each(rowIndex, function (index) {
                            hc.push(headconfig[this][h]);
                        });
                        columnc = defaultanalyse(columnc, hc);
                        //����ͷ


                        var $tr = $("<tr></tr>");
                        for (var i = 0; i < columnc.zindex.length; i++) {
                            var $th = $("<th colspan='" + columnc.hc[i].index.length + "' style='text-align:center;vertical-align:middle;'>" + columnc.zindex[i] + "</th>");
                            $tr.append($th);
                        }
                        $thead.append($tr);
                    }
                } else {
                    if (head.length != headconfig[0].length) {
                        for (var i = 0; i < headconfig[0].length; i++) {
                            if (!checkArray(i, head)) {
                                head.push(i);
                            }
                        }
                    }
                    //�������ͷ����


                    $.each(head, function () {
                        var col = this;
                        var hc = [];
                        $.each(headconfig, function (index) {
                            hc.push(this[col]);
                        });
                        columnc = analyse(hc, columnc);
                        //����ͷ


                        var $tr = $("<tr></tr>");
                        for (var i = 0; i < columnc.zindex.length; i++) {
                            var $th = $("<th colspan='" + columnc.hc[i].index.length + "' style='text-align:center;vertical-align:middle;'>" + columnc.zindex[i] + "</th>");
                            $tr.append($th);
                        }
                        $thead.append($tr);
                    });
                }
                return columnc.index;
            }
            //�����з��鷽��


            function groupColumn(dom, column, columnconfig) {
                var columnc;
                /****************ͷ������******************/
                var $tbody = $("tbody", dom);
                $tbody.html("");
                var trconfig = [];
                var groupSpan = [];
                //�������ͷ����


                $.each(column, function (zindex) {
                    var col = this;
                    var hc = [];
                    $.each(columnconfig, function (index) {
                        hc.push(this[col]);
                    });
                    columnc = analyse(hc, columnc);
                    var row = 0;
                    $.each(columnc.zindex, function (index) {
                        groupSpan.push({
                            rowspan: columnc.hc[index].index.length,
                            value:this,
                            proint: [row, zindex]
                        });
                        row += columnc.hc[index].index.length;
                    });
                    trconfig.push(columnc);
                });
                for (var i = trconfig.length - 1; i > 0; i--) {
                    var cf = trconfig[i];
                    for (var m = 0; m < cf.hc.length;m++){
                        if (!trconfig[i - 1].hc[cf.hc[m].parent]["child"]) {
                            trconfig[i - 1].hc[cf.hc[m].parent]["child"] = [];
                        }
                        trconfig[i - 1].hc[cf.hc[m].parent]["child"].push({
                            zindex: cf.zindex[m],
                            cf: cf.hc[m]
                        });
                    }
                    
                }
                var columndata = [];
                var cellIndex = [];
                for (var i = 0; i < columnc.index.length; i++) {
                    var data = [];
                    var olddata = columnconfig[columnc.index[i]];
                    for (var m = 0; m < column.length; m++) {
                        data.push(olddata[column[m]]);
                        if(i==0) cellIndex.push(column[m]);
                    }
                    for (var m = 0; m < olddata.length; m++) {
                        if (checkArray(m, column) == -1) {
                            data.push(olddata[m]);
                            if (i == 0) cellIndex.push(m);
                        }
                    }
                    columndata.push(data);
                }
                var index = [];
                $.each(columndata, function (row) {
                    var $tr = $("<tr></tr>");
                    //var 


                    //������������


                    $.each(columndata[row], function (cell) {
                        if (cell<column.length) {
                            var checkpoint = checkPoint(row, cell, groupSpan);
                            if (checkpoint) {
                                var $td = $("<td rowspan='" + checkpoint.rowspan + "' style='text-align:center;vertical-align:middle;'>" + this + "</td>");
                                $tr.append($td);
                            }
                        } else {
                            var $td = $("<td>" + this + "</td>");
                            $tr.append($td);
                        }
                    });
                    $tbody.append($tr); 
                });             
                return cellIndex;
            }
            //У����������


            function checkPoint(row, cell, data) {
                for (var i = 0; i < data.length; i++) {
                    var datainfo = data[i];
                    if (datainfo.proint[0] == row && datainfo.proint[1] == cell) {
                        return datainfo;
                    }
                }
            }
            //���鷽��


            function group(head, column) {
                var config = this.data["tableData"];
                //ͷ����


                var headconfig = config.heads;
                //������


                var columnconfig = config.columns;
                //�ж��Ƿ���ͷ������


                if (head && head instanceof Array) {
                    var index = groupHead(this, head, headconfig);
                    //�з���


                    groupColumn(this, index, columnconfig);
                } else {
                    var index=[];
                    if (!column || !(column instanceof Array)) {
                        $.each(headconfig, function (zindex) {
                            index.push(zindex);
                        });
                    } else {
                        index = column;
                        $.each(headconfig, function (zindex) {
                            if (!checkArray(zindex, index)) {
                                index.push(zindex);
                            }
                        });
                    }
                    var rowIndex=groupColumn(this, index, columnconfig);
                    //�������ͷ���飬ͷ�ڲ��ı��е�������Զ��ϲ�


                    var index = groupHead(this, null, headconfig, rowIndex);
                }
                return this;
            }
            //������ע����麯����


            this.group = group;
            this.group(options["head"], options["column"]);
            return this;
        }
    });
    
})(jQuery);