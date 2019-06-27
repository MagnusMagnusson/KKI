function login() {
    console.log("logging in");
    D = {
        'user': $("#uname").val(),
        'password': $("#pword").val()
    }
    console.log(D);
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
                alert(d.error);
            }

        }
    });
}

$(document).ready(function () {
    $("#login button").on('click', function (e) {
        login();
    })
});