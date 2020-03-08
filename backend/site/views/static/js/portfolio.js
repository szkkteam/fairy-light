/*
 * Isotope initialize for portfolio
 */
var isoContainer = $('.portfolio-container');

// Workaround: window on load event used, to make sure all media is loaded on the page
$(window).on('load', function() {
    isoContainer.isotope({
        itemSelector: '.portfolio-item',
        layoutMode: 'fitRows'
    });
});

$('#portfolio-filters li').on('click', function() {
    $("#portfolio-filters li").removeClass('filter-active');
    $(this).addClass('filter-active');

    isoContainer.isotope({
        filter: $(this).data('filter')
    });
});

/*
 * Init venobox
 */
$('.venobox').venobox();
