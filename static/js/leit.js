$(document).ready(function(){
    $("#leitarTakki").on("click", function (e) {
        var name = $("#leitargluggi").text();
        window.Api.findMember({ name }, memberResults);
    });
})
let year = new Date().getFullYear();
function memberResults(msg) {
    let res = msg.results;
    console.log(res);
    $("#nidurstodur ol").empty()
    for (let member of res) {
        member = member[1];
        let payment;
        let last_payment = null;
        if (member.last_payment) {
            last_payment = member.last_payment.split("-")[0];
            let cls = "red";
            if (last_payment == year) {
                cls = "green";
            }
            if (last_payment == year - 1) {
                cls = "yellow";
            }
            payment = $("<span class='"+cls+" payment-bubble'>"+last_payment+"</span>");
        } else {
            payment = $("<span class='red payment-bubble'>Ógreitt</span>");
        }
  
        let li = $("<li></li>");
        let a = $("<a href='/felagar/" + member.id+"'></a>");
        let strong = $("<strong>" + member.name + " </strong> ");
        let emm = null;
        if (member.email) {
            emm = $("<i class='result-subtext'> " + member.email + "</i>");
        }
        let address = member.address + ", " + member.postcode + ", " + member.city;
        let span = $("<span class='result-subtext'><i>"+member.ssn+"</i> - <i>"+address+"</i></span>")
        $(a).append(payment);
        $(a).append(strong);
        if (emm) {
            $(a).append(emm);
        }
        $(a).append($("<br/>"));
        $(a).append(span);
        $(li).append(a);
        $("#nidurstodur ol").append(li);
    }
}
