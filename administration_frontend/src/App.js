import React from 'react';
import {MemberSearchPage} from './Components/js/SearchPages';
import "./Components/css/master.css"

class App extends React.Component {
  constructor(props){
    super();
  }
  render(){
    return (
      <MemberSearchPage></MemberSearchPage>
    );
  }
}

export default App;
