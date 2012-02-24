$(document).bind("mobileinit", function () {

    // Navigation
    //$.mobile.page.prototype.options.backBtnText = "Go back";
    $.mobile.page.prototype.options.addBackBtn      = true;
     //$.mobile.selectmenu.prototype.options.nativeMenu = false;
     //$.mobile.selectmenu.prototype.options.hidePlaceholderMenuItems = false;
    //$.mobile.page.prototype.options.backBtnTheme    = "d";

    // Page
    //$.mobile.page.prototype.options.headerTheme = "e";  // Page header only
    //$.mobile.page.prototype.options.contentTheme    = "e";
    //$.mobile.page.prototype.options.footerTheme = "e";

    //// Listviews
    //$.mobile.listview.prototype.options.headerTheme = "e";  // Header for nested lists
    //$.mobile.listview.prototype.options.theme           = "e";  // List items / content
    //$.mobile.listview.prototype.options.dividerTheme    = "e";  // List divider

    //$.mobile.listview.prototype.options.splitTheme   = "e";
    //$.mobile.listview.prototype.options.countTheme   = "e";
    //$.mobile.listview.prototype.options.filterTheme = "e";
    ////$.mobile.listview.prototype.options.filterPlaceholder = "Filter data...";
});

var period = 'day'
//$.mobile.page.prototype.options.domCache = false;
//$.mobile.page.prototype.options.addBackBtn = true;
//
function onDataReceived(series) {
  // we get all the data in one go, if we only got partial
  // data, we could merge it with what we already got
  //console.log(series.Home);
  constraint2 = { 
    threshold: -1,
    color: "rgb(253, 159, 36)",
    evaluate : function(y, threshold){ return y < threshold; }
  }
  constraint1 = { 
    threshold: -4,
    color: "rgb(237,28,36)",
    evaluate : function(y, threshold){ return y < threshold; }
  }
  plot_data = [{data:series, constraints:[constraint1, constraint2], color: "rgb(0, 146, 69)"}];
  $.mobile.hidePageLoadingMsg();
  $('#data-plot').show();
  $.plot($("#data-plot"), plot_data, { xaxis: { mode: "time" }});
}
function update_series () {
  $('#data-plot').hide();
  $.mobile.showPageLoadingMsg();
  $.ajax({
    url: '/rdc/get/' + period,
    method: 'GET',
    dataType: 'json',
    success: onDataReceived
  });
};
var plot_data = [];


$( document ).delegate("#dataPage", "pagecreate", function() {
  $( "#dataPage" ).bind( "pageshow", function( event, data ){
    period = 'day'
    update_series();
  });
  $( window ).bind( "orientationchange", function( event, data ){
    $.plot($("#data-plot"), plot_data, { xaxis: { mode: "time" }});
  });
  $( window ).bind( "resize", function( event, data ){
    $.plot($("#data-plot"), plot_data, { xaxis: { mode: "time" }});
  });
  $("#day").click(function() {
    period = 'day';
    update_series();
  });
  $("#week").click(function() {
    period = 'week';
    update_series();
  });
  $("#month").click(function() {
    period = 'month';
    update_series();
  });
});
