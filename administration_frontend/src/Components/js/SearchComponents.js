import React from 'react';
import '../css/SearchComponents.css';

/// onClick
function SearchButton(props){
    return (<button className ="searchbutton" onClick={props.onClick}></button>);
}

/// (searchValue, updateSearchValue, onSearch)
function SearchBar(props){
    return (<div>
            <div className="searchbar">
                <input value={props.searchValue} onChange={x => props.updateSearchValue(x.target.value)}></input>
                <SearchButton onClick={s => props.onSearch(props.searchValue)}></SearchButton>
            </div>
        </div>);
}

/// (getResults, results)
class SearchPage extends React.Component{
    constructor(props){
        super();
        this.state = {
            'value':''
        };
        this.search = this.search.bind(this);
        this.updateBar = this.updateBar.bind(this);
    }

    updateBar(value){
        this.setState({"value":value});
    }

    search(){
        this.props.getResults(this.state.value);
    }

    render(){
    let res = this.props.results.map(item => (<li key={item.key}>{item.element}</li>))
        return(
            <div className="searchpage">
                <SearchBar searchValue={this.state.value} updateSearchValue={this.updateBar} onSearch={this.search}></SearchBar>
                <div>
                    <ul>
                        {res}
                    </ul>
                </div>
            </div>
        )
    }


}

export default SearchPage
export {SearchBar, SearchPage};