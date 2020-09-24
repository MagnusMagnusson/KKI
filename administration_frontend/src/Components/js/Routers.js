import React from 'react';
import {CatSearchComponent} from './SearchPages';
import {  Route } from "react-router-dom";


function CatRouter(props){
    return(
            <div>                
                <Route path="/kettir" exact component={CatSearchComponent}>
                </Route>
                <Route path="/kettir/test">
                    <b>test</b>
                </Route>
            </div>
    );
}

let exp = {CatRouter};

export default exp;