/*
 * Isotope initialize for portfolio
 */
var portfolioIsotope = $('.portfolio-container').isotope({
    itemSelector: '.portfolio-item',
    layoutMode: 'fitRows'
});

$('#portfolio-filters li').on('click', function() {
    $("#portfolio-filters li").removeClass('filter-active');
    $(this).addClass('filter-active');

    portfolioIsotope.isotope({
        filter: $(this).data('filter')
    });
});

/*
 * Init venobox
 */
$('.venobox').venobox();
