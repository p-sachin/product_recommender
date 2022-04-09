jQuery(document).ready(function($){

"use strict";

var nav_offset_top = $('header').height() + 345;

var best_product_slider = $('.best_product_slider');
if (best_product_slider.length) {
  best_product_slider.owlCarousel({
    items: 4,
    loop: true,
    dots: false,
    autoplay: true,
    autoplayHoverPause: true,
    autoplayTimeout: 5000,
    nav: true,
    navText: ["next", "previous"],
    responsive: {
      0: {
        margin: 15,
        items: 1,
        nav: false
      },
      576: {
        margin: 15,
        items: 2,
        nav: false
      },
      768: {
        margin: 30,
        items: 3,
        nav: true
      },
      991: {
        margin: 30,
        items: 4,
        nav: true
      }
    }
  });
}


AOS.init();

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();   
});

// Navigation Scroll

function navbarOnScroll(){
    if ( $('.header-content').length){ 
        $(window).scroll(function() {
            var scroll = $(window).scrollTop();   
            if (scroll >= nav_offset_top ) {
                $(".header-content").addClass("navbar-scroll");
            } else {
                $(".header-content").removeClass("navbar-scroll");
            }
        });
    };
};
navbarOnScroll();

// SinglePage Scroll

 function SinglePage() {

    $(document).on('click', '#navbarCollapse a[href^="#"]', function (event) {
    event.preventDefault();
    var href = $.attr(this, 'href');
    $('html, body').animate({
        scrollTop: $($.attr(this, 'href')).offset().top
    }, 500, function() {
        // window.location.hash = href;
    });
    });

};

SinglePage();

// ScrollIt

function scroll() {
 $.scrollIt({
    upKey: 38,
    downKey: 40,
    activeClass: 'active',
    easing: 'swing',
    scrollTime: 600,
    onPageChange: null
 });
}

scroll();

  // About SkillBar

  function skillbar() {
 $(".skill-bar").each(function() {
    $(this).waypoint(function() {
        var progressBar = $(".progress-bar");
        progressBar.each(function(indx){
            $(this).css("width", $(this).attr("aria-valuenow") + "%")
        })
    }, {
        triggerOnce: true,
        offset: 'bottom-in-view'
    });
});
}

skillbar();

});



