﻿function login() {
    D = {
        'user': $("#uname").val(),
        'password': $("#pword").val()
    }
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