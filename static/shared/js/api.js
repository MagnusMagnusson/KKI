
class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.find = "/api/leit/";
        this.urlList.getPerson = "/api/saekja/einstakling";
        this.urlList.getCat = "/api/saekja/kott";
        this.urlList.get = "/api/saekja/";
        this.urlList.submitPayment = "/api/skra/greidsla";
        this.urlList.submitPerson = "/api/skra/einstaklingur";
        this.urlList.submitMember = "/api/skra/felagi";
        this.urlList.submitCattery = "/api/skra/raektun";
        this.urlList.submitNeuter = "/api/skra/geldingu";
        this.urlList.submitCatOwner = "/api/skra/eigendaskipti";
        this.urlList.submitShow = "/api/skra/syning";
        this.urlList.submitCat = "/api/skra/kottur";
        this.urlList.submitJudge = "/api/skra/domari";
        this.urlList.nextRegNr = "/api/util/skraningarnumer";
    }

    prepare(dictionary) {
        let dat = {}
        dat['data'] = JSON.stringify(dictionary);
        return dat;
    }

    /*
        find {
            type : 'Model',
            terms : 'field',
            value : 'blue'
        }
    */
    find(data,callback) {
        this._get(this.urlList.find,data, callback);
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
        this._get(this.urlList.getPerson, terms, callback);
    }

    getCat(terms, callback) {
        this._get(this.urlList.getCat, terms, callback);
    }

    /*
        will retrieve any items that have fields exactly matching the specified terms and values
        get{
            type: The model being sought after
            values: value being retrieved,
                a dictionary with the key being the term being searched,
                the value being the string that has to be matched.
        }
    */
    get(data, callback) {
        data = this.prepare(data);
        this._get(this.urlList.get, data, callback);
    }

    submitPayment(data, callback) {
        this._post(this.urlList.submitPayment, data, callback);
    }

    submitPerson(data, callback) {
        this._post(this.urlList.submitPerson, data, callback);
    }

    submitMember(data, callback) {
        this._post(this.urlList.submitMember, data, callback);
    }

    submitCattery(data, callback) {
        this._post(this.urlList.submitCattery, data, callback);
    }

    submitNeuter(data, callback) {
        this._post(this.urlList.submitNeuter, data, callback);
    }

    submitCatOwner(data, callback) {
        this._post(this.urlList.submitCatOwner, data, callback);
    }

    submitShow(data, callback) {
        this._post(this.urlList.submitShow, data, callback);
    }

    submitCat(data, callback) {
        this._post(this.urlList.submitCat, data, callback);
    }

    getNextRegNr(callback) {
        this._get(this.urlList.nextRegNr, {}, callback);
    }

    _get(url, data, callback) {
        $.ajax({
            method: "GET",
            url: url,
            data:data,
        }).done(function (msg) {
            callback(msg);
        });
    }

    _post(url, data, callback) {
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