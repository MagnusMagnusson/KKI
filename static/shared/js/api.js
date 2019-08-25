
class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.find = "/api/leit/";
        this.urlList.getPerson = "/api/saekja/einstakling";
        this.urlList.getCat = "/api/saekja/kott";
        this.urlList.getById = "/api/saekja/";
        this.urlList.submitPayment = "/api/skra/greidsla";
        this.urlList.submitPerson = "/api/skra/einstaklingur";
        this.urlList.submitMember = "/api/skra/felagi";
        this.urlList.submitCattery = "/api/skra/raektun";
        this.urlList.submitNeuter = "/api/skra/geldingu";
        this.urlList.submitCatOwner = "/api/skra/eigendaskipti";
        this.urlList.submitShow = "/api/skra/syning";
        this.urlList.submitCat = "/api/skra/kottur";
        this.urlList.nextRegNr = "/api/util/skraningarnumer";
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
    
    /*
        getPerson{
            'ssn': ssn to look up,
            'member': only look up members
            'name': filter by name
        }
        returns a list of all persons that fit *all* specified criteria.
    */
    getPerson(terms, callback) {
        this.get(this.urlList.getPerson, terms, callback);
    }

    getCat(terms, callback) {
        this.get(this.urlList.getCat, terms, callback);
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

    submitNeuter(data, callback) {
        this.post(this.urlList.submitNeuter, data, callback);
    }

    submitCatOwner(data, callback) {
        this.post(this.urlList.submitCatOwner, data, callback);
    }

    submitShow(data, callback) {
        this.post(this.urlList.submitShow, data, callback);
    }

    submitCat(data, callback) {
        this.post(this.urlList.submitCat, data, callback);
    }

    getNextRegNr(callback) {
        this.get(this.urlList.nextRegNr, {}, callback);
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