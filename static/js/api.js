
class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.find = "/api/leit/";
        this.urlList.getPerson = "/api/saekja/einstakling";
        this.urlList.getById = "/api/saekja/";
        this.urlList.submitPayment = "/api/skra/greidsla";
        this.urlList.submitPerson = "/api/skra/einstaklingur";
        this.urlList.submitMember = "/api/skra/felagi";
        this.urlList.submitCattery = "/api/skra/raektun";
    }

    /*
        find {
            type : 'Model',
            terms : 'field',
            value : 'blue'
        }
    */
    find(data,callback) {
        this.get(this.urlList.find,data, callback);
    }

    getPerson(terms, callback) {
        this.get(this.urlList.getPerson, terms, callback);
    }

    /*
        getById{
            type: The model being sought after
            id: the ID of the item being sought after
        }
    */
    getById(data, callback) {
        this.get(this.urlList.getById, data, callback);
    }

    submitPayment(data, callback) {
        this.post(this.urlList.submitPayment, data, callback);
    }

    submitPerson(data, callback) {
        this.post(this.urlList.submitPerson, data, callback);
    }

    submitMember(data, callback) {
        this.post(this.urlList.submitMember, data, callback);
    }

    submitCattery(data, callback) {
        this.post(this.urlList.submitCattery, data, callback);
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
            if (msg.success) {
                callback(msg);
            } else {
                alert(msg.error);
            }
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