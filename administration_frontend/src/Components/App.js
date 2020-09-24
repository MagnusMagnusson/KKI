import React from 'react';
import { Route,  BrowserRouter } from "react-router-dom";

import Routers from './js/Routers'
import {Header} from './js/HeaderComponents';
import "./css/master.css"

function Test(){
  return (<b>lul</b>);
}

class App extends React.Component {
  constructor(props){
    super();
  }
  render(){
    return (
      <div>
          <BrowserRouter>
              <Header></Header>
              <Route path="/" exact component={Test}></Route>
              <Route path="/kettir" component={Routers.CatRouter}></Route>
          </BrowserRouter>
      </div>
    );
  }
}

export default App;
