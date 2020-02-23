function login() {
    D = {
        'user': $("#uname").val(),
        'password': $("#pword").val()
    }
    $(".warning").hide();
    $.ajax({
        type: "POST",
        url: "/api/login",
        dataType: 'json',
        data: D,
        success: function (d) {
            if (d.success) {
                location.reload();
            }
            else {
                $(".warning").show();
            }

        }
    });
}

$(document).ready(function () {
    $("#login button").on('click', function (e) {
        login();
    })
});