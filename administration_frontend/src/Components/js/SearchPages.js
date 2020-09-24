import React from 'react';
import {SearchPage} from './SearchComponents';
import "../css/SearchPages.css"


class GenericSearchComponent extends React.Component {
    constructor(props){
        super();
        this.apiLocation = null; ///Overwrite
        this.state = {
            'results':[]
        };
        this.getResults = this.getResults.bind(this);
        this.processResults = this.processResults.bind(this);
    }

    getResults(x){
        let data = JSON.stringify({"search":{"name":x}});
        fetch(this.apiLocation + "?data="+data).then(x => x.json()).then(data => {
            if(data.success){
                this.setState({results:data.results});
            }
        });
    }

    render(){
        return(
            <SearchPage getResults={this.getResults} results={this.processResults()}>

            </SearchPage>
        )
    }

    ///Overwrite in inheriting classes
    processResults(data){
        let r = []
        for(let x of this.state.results){
            r.push({"key":x.id, "element":(<b key={x.id}>{JSON.stringify(x)}</b>)});
        }
        return r;
    }
}


class CatSearchComponent extends GenericSearchComponent{
    constructor(props){
        super();
        this.apiLocation = "/api/kettir"
    }

    processResults(data){
        let r = []
        for(let x of this.state.results){
            let result = {
                "key":x.registry_number,
                "element":(<a key={x.registry_number}>
                    <span>
                        <strong>{x.name}</strong> 
                        <small>
                            ({x.ems}), 
                            {x.registry_number}, 
                            f:{x.birthdate}
                        </small>
                    </span>
                </a>)
            };
            r.push(result);
        }
        return r;
    }
}

class CatterySearchComponent extends GenericSearchComponent{
    constructor(props){
        super();
        this.apiLocation = "/api/raektanir"
    }

    processResults(data){
        let r = []
        for(let x of this.state.results){
            let phone_number = x.phone_number ? " - "+x.phone_number: ""
            let address = x.address ? " - "+x.address : " - Heimilisfang ekki skráð";
            let result = {
                "key":x.id,
                "element":(<a key={x.id}>
                    <span>
                        <strong>{x.name} </strong> 
                        <small>
                             {x.email}{phone_number}{address}
                        </small>
                    </span>
                </a>)
            };
            r.push(result);
        }
        return r;
    }
}

class MemberSearchComponent extends GenericSearchComponent{
    constructor(props){
        super();
        this.apiLocation = "/api/felagar";
    }

    getBubble(last_payment){        
        let currYear = new Date().getUTCFullYear();
        let year = new Date(last_payment).getUTCFullYear();
        let lastPayment = null;
        if(year !== "Invalid Date"){
            lastPayment = currYear - year;
        }

        let color = "red";
        let text = "Ógreitt";
        if(lastPayment){
            color = lastPayment === 0 ? "green": lastPayment === 1 ? "orange" : "red";
            text = year;
        }
        return (
            <span className={"bubble "+color}>{text}</span>
        );
    }

    processResults(data){
        let r = []
        for(let x of this.state.results){
            let bubble = this.getBubble(x.last_payment);
            let address = x.address ? " - "+x.address : " - Heimilisfang ekki skráð";
            let result = {
                "key":x.id,
                "element":(<a key={x.id}>
                    <span>
                        {bubble}<strong>{x.name}[{x.member_id}] - </strong> 
                        <small>
                              {x.email}
                        </small>
                        <br/>
                        <small><i>{x.ssn}</i> - {x.address}</small>
                    </span>
                </a>)
            };
            r.push(result);
        }
        return r;
    }
}

export {CatSearchComponent, CatterySearchComponent, MemberSearchComponent}