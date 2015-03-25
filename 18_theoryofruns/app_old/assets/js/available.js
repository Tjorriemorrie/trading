$('.fill-modal').on('click', function(event) {
    fillModal($(this).parents('div.painting-item'));
});

function fillModal(thumbnail) {
    $('.modal-body .thumbnail img').attr('src', thumbnail.find('img').attr('src'));
    $('.modal-body .thumbnail h3').text(thumbnail.find('h4').text());
    $('.modal-body .thumbnail p').text(thumbnail.find('.price').text());
    $('#painting_id').val(thumbnail.data('id'));

    $('#btn').show();
    $('#modalContent').show();
    $('#modalSuccess').hide();
}

$('#modalRequest').on('shown.bs.modal', function(event) {
    $('#name').focus();
});

$('form').on('submit', function(event) {
    event.preventDefault();
    submitForm();
});

function submitForm() {
    $('#btn').button('loading');
    var data = $('#request').serialize();
    console.log(data);
    var post = $.post(
        '/available',
        data
    );

    post.done(function(res) {
        $('#btn').hide();
        $('#modalContent').hide();
        $('#modalSuccess').show();
    });

    post.fail(function(err) {
        alert('Message sent errored');
    });

    post.always(function() {
        $('#btn').button('reset');
    });
}