import React from 'react';
import {CatSearchComponent} from './SearchPages';
import {  Route } from "react-router-dom";
import urls from '../../Site_code/urls';


function CatRouter(props){
    return(
            <div>                
                <Route path={urls.CATSEARCH} exact component={CatSearchComponent}></Route>
                <Route path={urls.CATPROFILE}></Route>
            </div>
    );
};

let exp = {CatRouter};

export default exp;