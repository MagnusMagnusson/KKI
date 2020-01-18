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
        this.urlList.ems = "/api/ems";
        this.urlList.cert = "/api/stig";
        this.urlList.award = "/api/verdlaun";
        this.urlList.organizations = "/api/felog";
        this.urlList.people = "/api/folk";
        this.urlList.getNextRegNr = "/api/util/skrnr";
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
            case "nomination": {
                if (idArray.length == 0) {
                    throw "Not enough information to construct information";
                } else if(idArray.length == 1) {
                    return this.urlList.shows + "/" + idArray[0] + "/tilnefningar";
                } else {
                    return this.urlList.shows + "/" + idArray[0] + "/tilnefningar/" + idArray[1];
                }
            }

            case "organization": {
                if (idArray.length == 0) {
                    return this.urlList.organizations;
                } else {
                    return this.urlList.organizations + "/" + idArray[0]
                }
                break;
            }
        }
        throw "No resource exists with name "+model;
    }

    prepare(dictionary) {
        let dat = {}
        dat['data'] = JSON.stringify(dictionary);
        return dat;
    }

    find(model, searchDict, callback, onError = {}, idArray = [], e = {}) {
        let url;
        url = this.getUrl(model, idArray);
        let d = e;
        d.search = searchDict;
        d = this.prepare(d);
        this._get(url,d, callback, onError);
    }

    get(model, filterDict, callback, onError, idArray = [], e = {}) {
        let url;
        url = this.getUrl(model, idArray);
        let d = e;
        d.filter = filterDict;
        d = this.prepare(d);
        this._get(url, d, callback, onError);
    }

    getfind(model, filterDict, searchDict, callback, onError, idArray = [], e = {}) {
        let url;
        url = this.getUrl(model, idArray);
        let d = e;
        d.filter = filterDict;
        d.search = searchDict;
        d = this.prepare(d);
        this._get(url, d, callback, onError);
    }

    getAll(model, filterDict, callback, onError, idArray, e = {}) {
        let url;
        url = this.getUrl(model, idArray);
        let d = e;
        e.filter = filterDict;
        e.offset = -1;
        d = this.prepare(d);
        this._get(url, d, callback, onError);
    }

    edit(model, patchDict, callback, onError, idArray = []) {
        let url = this.getUrl(model, idArray);
        let d = this.prepare(patchDict);

        this._ajax("PATCH", url, d, callback, onError);
    }

    create(model, patchDict, callback, onError, idArray = []) {
        let url = this.getUrl(model, idArray);
        let d = this.prepare(patchDict);
        this._ajax("POST", url, d, callback, onError);
    }

    delete(model, patchDict, callback, onError, idArray = []) {
        let url = this.getUrl(model, idArray);
        let d = this.prepare(patchDict);
        this._ajax("DELETE", url, d, callback, onError);
    }

    getPerson(terms, callback, onError) {
        this.get("member", terms, callback, onError);
    }

    getCat(data, callback, onError) {
        let dat = this.prepare(data);
        this._get(this.urlList.cats, dat, callback, onError);
    }

    __get(data, callback, onError) {
        data = this.prepare(data);
        this._get(this.urlList.get, data, callback, onError);
    }

    getNextRegNr(callback) {
        this._get(this.urlList.getNextRegNr, {}, callback);
    }

    _get(url, data, callback, onError) {
        console.log(onError);
        this._ajax("GET", url, data, callback, onError);
    }

    _post(url, data, callback, onError) {
        this._ajax("POST", url, data, callback, onError);
    }

    _patch(url, data, callback, onError) {
        this._ajax("PATCH", url, data, callback, onError);
    }

    _ajax(method, url, data, callback, onError) {
        console.log("AAAAAAAA");
        $.ajax({
            method: method.toUpperCase(),
            url: url,
            data: data,
        }).done(function (msg) {
            if (msg.success) {
                if (callback) {
                    callback(msg);
                }
            } else {
                if (onError) {
                    onError(msg);
                }
            }
            }).fail(function (msg) {
                if (onError) {
                    onError(msg.responseJSON);
                }
        });;
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