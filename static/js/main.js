$(document).ready(function() {

    $('#view-form').on('submit', function(elem) {
        elem.preventDefault();
        let errors = [];

        // check city
        let city_id = Number.parseInt($('#select-city').val());
        if (city_id === NaN) errors.push('Оберіть ваше місто')

        // check goverment number
        let gov_num = $('#gov-num').val();
        if (gov_num.lenght < 4) errors.push('Вкажіть правильний держ. номер авто')

        let video_file = $('car-view').val();
    });
});