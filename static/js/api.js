
class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.findMember = "/api/finna/felagi";
    }

    findMember(name,callback) {
        this.get(this.urlList.findMember, { name }, callback);
    }

    get(url, data, callback) {
        $.ajax({
            method: "GET",
            url: url,
            data:data,
        }).done(function (msg) {
            callback(msg);
        });
    }

    post(url, data, callback) {
        $.ajax({
            method: "POST",
            url: url,
            data: data,
        }).done(function (msg) {
            callback(msg);
        });
    }
}