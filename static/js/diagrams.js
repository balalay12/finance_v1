        var c = document.getElementById('cost').value
        c *= -1
        var e = document.getElementById('earn').value
        console.log(e)
        console.log(c)
        var buyers = document.getElementById('buyers').getContext('2d');
        var buyerData = {
            labels : ["Доход","Расход"],
            datasets : [
                {
                fillColor : "rgba(172,194,132,0.4)",
                strokeColor : "#ACC26D",
                pointColor : "#fff",
                pointStrokeColor : "#9DB86D",
                data : [e,c]
                }
            ]
        }
        new Chart(buyers).Bar(buyerData);

        var countries= document.getElementById("countries").getContext("2d");
        var colorArr = ["#CD5C5C", "#878BB6", "#FFFF00", "#4ACAB4", "#FF8153", "#9370DB", "#00FF7F", "#D2691E"]
        var valueArr = []
        var catArr = []
        $('#sum li').each(function (i, item) {
            valueArr.push($(item).text());
        });
        $('#cat li').each(function (i, item) {
            catArr.push($(item).text());
        });
        var i = 0,
        resultArr = [];
        for (i; i <= valueArr.length -1; i++) {
         var itemColor = colorArr[i],
             itemValue = parseInt(valueArr[i]),
             itemLabel = catArr[i];

         resultArr.push({
             value: itemValue,
             color: itemColor,
             label: itemLabel
         });
        }
        console.log(resultArr);
        var pieOptions = {
        segmentShowStroke : false,
        animateScale : true
}
        new Chart(countries).Pie(resultArr, pieOptions);