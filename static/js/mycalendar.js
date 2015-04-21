        $(document).ready(function() {
            $('#id_date, #id_date_start, #id_date_end').daterangepicker({
                singleDatePicker: true,
                startDate: moment(),
                minDate: '2014-01-01',
                format: 'DD.MM.YYYY',
                locale: {
                        daysOfWeek: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
                        monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
                        firstDay: 1
                }
            }, function(start, end, label) {
                console.log(start.toISOString(), end.toISOString(), label);
            });
        });