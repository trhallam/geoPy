/**
 * JavaScripts to return options and data selected from chart.
 * http://jsfiddle.net/k159ak5h/1/
 */
 
returnJS.getLegendSelectedSeries = function(chart) {
	 /* Return booleans for the series selected in the Legdend of a Highchart. */
	 var visibleSeries = [];
	 for (var i in chart.series) {
		 visibleSeries[chart.series[i].name] = chart.series[i].visible.toString();
         /*alert(chart.series[i].name+" : "+chart.series[i].visible.toString())*/
	 }
	 return visibleSeries;
};

returnJS.checkAr = function(array) {
	for (var i in array) {
	alert(i+" : "+array[i]);	
	}
	
};