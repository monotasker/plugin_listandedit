//content moved to view file because of difficulty injecting after page load
//
//$(document).ready(function(){
//
//if($('#main').hasClass('listing') || $('#main').hasClass('editing')){
//    /* set listpane height to optimal */
//    /* if pane heights are wrong, change the value of the heightadjust variable to tweak it */
//    var heightadjust = 48;
//    var lpos = $('#listpane').offset();
//    var vpos = $('#viewpane').offset();
//    var listtop = lpos.top;
//    var viewtop = vpos.top;
//    var winheight = $(window).height();
//    /* I'm using the html5 footer element here, to use standard id just change 'footer' to '#footer' */
//    var headheight = $('#header').height();
//    var navheight = $('#list_control').height();
//    var footheight = $('#footer').height();
//    var listheight = winheight - footheight - headheight - heightadjust - navheight;
//    var viewheight = winheight - footheight - headheight - heightadjust - navheight;
//    $('#listpane').css('height', listheight);
//    $('#viewpane').css('height', viewheight);
//
//    /* make sure pane heights resize properly when window resizes */
//    $(window).bind('resize', function(){
//        $('#listpane').css('height', listheight);
//        $('#viewpane').css('height', viewheight);
//    });
//}
//});
