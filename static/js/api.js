
class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.findMember = "/api/leit/felagi";
        this.urlList.getPerson = "/api/saekja/einstaklingur";
        this.urlList.submitPayment = "/api/skra/greidsla";
        this.urlList.submitPerson = "/api/skra/einstaklingur";
    }

    findMember(terms,callback) {
        this.get(this.urlList.findMember,terms, callback);
    }

    getPerson(terms, callback) {
        this.get(this.urlList.getPerson, terms, callback);
    }

    submitPayment(data, callback) {
        this.post(this.urlList.submitPayment, data, callback);
    }

    submitPerson(data, callback) {
        this.post(this.urlList.submitPerson, data, callback);
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

    getModule(module, callback) {
        let t = this;
        $.ajax(
            {
                url: "/modules/"+module,
                method: "GET"
            }
        ).done(function (msg) {
            callback(msg);
        });
    }
}