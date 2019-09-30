class Api{
    constructor() {
        this.urlList = {};
        this.setupURLs();
    }

    setupURLs() {
        this.urlList.cats = "/api/kettir";
        this.urlList.members = "/api/felagar";
        this.urlList.judge = "/api/domarar";
        this.urlList.catteries = "/api/raektanir";
        this.urlList.shows = "/api/syningar";
        this.urlList.ems = "/api/ems"
        this.urlList.cert = "/api/stig"
        this.urlList.award = "/api/verdlaun"
        this.urlList.people = "/api/folk"
        //this.urlList.find = "/api/leit/";
        //this.urlList.getPerson = "/api/saekja/einstakling";
        //this.urlList.getCat = "/api/saekja/kott";
        //this.urlList.get = "/api/saekja/";
        //this.urlList.submitPayment = "/api/skra/greidsla";
        //this.urlList.submitPerson = "/api/skra/einstaklingur";
        //this.urlList.submitMember = "/api/skra/felagi";
        //this.urlList.submitCattery = "/api/skra/raektun";
        //this.urlList.submitNeuter = "/api/skra/geldingu";
        //this.urlList.submitCatOwner = "/api/skra/eigendaskipti";
        //this.urlList.submitShow = "/api/skra/syning";
        //this.urlList.submitCat = "/api/skra/kottur";
        //this.urlList.submitJudge = "/api/skra/domari";
        //this.urlList.nextRegNr = "/api/util/skraningarnumer";
    }

    getUrl(model, idArray = []) {
        switch (model) {
            case "cat": {
                if (idArray.length == 0) {
                    return this.urlList.cats;
                } else {
                    return this.urlList.cats + "/" + idArray[0]
                }
                break;
            }
            case "person": {
                if (idArray.length == 0) {
                    return this.urlList.people;
                } else {
                    return this.urlList.people + "/" + idArray[0]
                }
                break;
            }
            case "member": {
                if (idArray.length == 0) {
                    return this.urlList.members;
                } else {
                    return this.urlList.members + "/" + idArray[0]
                }
                break;
            }
            case "judge": {
                if (idArray.length == 0) {
                    return this.urlList.judge;
                } else {
                    return this.urlList.judge + "/" + idArray[0]
                }
                break;
            }
            case "cattery": {
                if (idArray.length == 0) {
                    return this.urlList.catteries;
                } else {
                    return this.urlList.catteries + "/" + idArray[0]
                }
                break;
            }
            case "show": {
                if (idArray.length == 0) {
                    return this.urlList.shows;
                } else {
                    return this.urlList.shows + "/" + idArray[0]
                }
                break;
            }
            case "entry": {
                if (idArray.length == 0) {
                    throw "Not enough information to fetch entrants. Specify show";
                } else if (idArray.length == 1) {
                    return this.urlList.shows + "/" + idArray[0] + "/keppendur";
                } else {
                    return this.urlList.shows + "/" + idArray[0] + "/keppendur/" + idArray[1];
                }
                break;
            }
            case "ems": {
                if (idArray.length == 0) {
                    return this.urlList.ems;
                } else if (idArray.length == 1) {
                    return this.urlList.ems + "/" + idArray[0];
                } else {
                    return this.urlList.ems + "/" + idArray[0] + "/" + idArray[1];
                }
                break;
            }
            case "cert": {
                if (idArray.length == 0) {
                    return this.urlList.cert;
                } else {
                    return this.urlList.cert + "/" + idArray[0]
                }
            }
            case "award": {
                if (idArray.length == 0) {
                    return this.urlList.award;
                } else {
                    return this.urlList.award + "/" + idArray[0]
                }
            }
        }
        throw "No resource exists with name "+model;
    }

    prepare(dictionary) {
        let dat = {}
        dat['data'] = JSON.stringify(dictionary);
        return dat;
    }

    /*
        find {
            type : 'Model'
            terms : 'field',
            value : 'blue'
        }
    */
    find(model, searchDict, callback, idArray = []) {
        let url;
        url = this.getUrl(model, idArray);
        let d = {
            "search": searchDict
        };
        d = this.prepare(d);
        this._get(url,d, callback);
    }

    get(model, filterDict, callback, idArray = [], page = 0) {
        let url;
        url = this.getUrl(model, idArray);
        let d = {
            "filter": filterDict,
            "page":page
        }
        d = this.prepare(d);
        this._get(url, d, callback);
    }

    edit(model, patchDict, callback, idArray = []) {
        let url = this.getUrl(model, idArray);
        let d = this.prepare(patchDict);
        this._ajax("PATCH", url, d, callback);
    }

    create(model, patchDict, callback, idArray = []) {
        let url = this.getUrl(model, idArray);
        let d = this.prepare(patchDict);
        this._ajax("POST", url, d, callback);
    }

    /*
        getPerson{
            <dict:terms>, key:value dict stating which properties must be present 
        }
        returns a list of all persons that fit *all* specified criteria.
    */
    getPerson(terms, callback) {
        this.get("member", terms, callback);
    }

    getCat(data, callback) {
        let dat = this.prepare(data);
        this._get(this.urlList.cats, dat, callback);
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
    __get(data, callback) {
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
        this._ajax("GET", url, data, callback);
    }

    _post(url, data, callback) {
        this._ajax("POST", url, data, callback);
    }

    _patch(url, data, callback) {
        this._ajax("PATCH", url, data, callback);
    }

    _ajax(method, url, data, callback) {
        $.ajax({
            method: method.toUpperCase(),
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