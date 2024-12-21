'use strict';

window.addEventListener('load', function () {

  console.log("Hello World!");

});


window.addEventListener('scroll', function () {
  var element = document.getElementById("description-box");
  var elem_offset = document.getElementById("description-container").offsetTop;
  var scroll_height = window.scrollY;
  console.log(String(elem_offset));

  if (scroll_height > elem_offset) {
    console.log("tick");
    element.classList.add("sticky");
  } else {
    element.classList.remove("sticky");
  }

});


function toggleLength(evt) {
  console.log('click');
  evt.currentTarget.classList.toggle("has-count");
//  evt.currentTarget.classList.toggle("redacted");
}


//
//function sticky_relocate() {
//    var window_top = $(window).scrollTop();
//    var div_top = $('#sticky-anchor').offset().top;
//    if (window_top > div_top)
//        $('#description-box').addClass('sticky');
//    else
//        $('#description-box').removeClass('sticky');
//}

//$(function() {
//    $(window).scroll(sticky_relocate);
//    sticky_relocate();
//});

