/**/ 
var returnJS = (function() {
    return {
        checkAr:function(array) {
			for (var i in array) {
				alert(i+" : "+array[i]);
			}
		},
        getLegendSelectedSeries:function(chart) {
			"Return booleans for the series selected in the Legdend of a Highchart.";
			var visibleSeries = [];
			for (var i in chart.series) {
				visibleSeries[chart.series[i].name] = chart.series[i].visible.toString();
			}
			return visibleSeries;
		}
	};		   
}());

