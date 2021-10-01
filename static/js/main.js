$(document).ready(function() {

    $('#view-form').on('submit', function(elem) {
        elem.preventDefault();
        $('#alerts').empty();
        $('#success').empty();
        let errors = new Array();

        // check city
        let city_id = Number.parseInt($('#select-city').val());
        if (Number.isNaN(city_id)) errors.push('Оберіть ваше місто')

        // check goverment number
        let gov_num = $('#gov-num').val();
        if (gov_num.lenght < 4) errors.push('Вкажіть правильний держ. номер авто')

        let callsign = $('#callsign').val();
        
        
        if (window.FormData === undefined) {
            alert('В вашем браузере FormData не поддерживается')
        } else {
            let formData = new FormData();
            let car_file = $("#car-view")[0].files[0];
            if (car_file['type'].indexOf('video') == -1) errors.push('Невірний формат файлу! Завантажте будь-ласка відео-файл')
            
            if (errors.length == 0) {
                formData.append('file', car_file);
                formData.append('gov_num', gov_num);
                formData.append('city_id', city_id);
                formData.append('callsign', callsign);

                $.ajax({
                    type: "POST",
                    url: '/send_view',
                    cache: false,
                    contentType: false,
                    processData: false,
                    data: formData,
                    dataType : 'json',
                    success: function(msg){
                        console.log(msg);
                        if (msg.error == '') {
                            let alert_template = $('#success-temp').html();
                            alert_template = $(alert_template).attr('id', 'success-main');
                            $('#success').append(alert_template);
                            $('#gov-num').val('');
                            $('#callsign').val('');
                            $('#car-view').val(null);
                        } else {
                            let alert_template = $('#alert-temp').html();
                            alert_template = $(alert_template).attr('id', 'alert-main');
                            $('#alerts').append(alert_template);
                            $('#alert-main').text(msg.error)
                        }
                    },
                    error: function() {
                        let alert_template = $('#alert-temp').html();
                            alert_template = $(alert_template).attr('id', 'alert-main');
                            $('#alerts').append(alert_template);
                            $('#alert-main').text("Сталася помилка при завантаженні відео-огляду! Будь-ласка зв'яжіться з вашим регіональним офісом в робочий час або спробуйте знову")
                    }
                });
            } else {
                errors.forEach(function(elem, index) {
                    let alert_template = $('#alert-temp').html();
                    alert_template = $(alert_template).attr('id', 'alert-' + index);
                    $('#alerts').append(alert_template);
                    $('#alert-' + index).text(elem);
                })
            }
        }
     
    });
});