import React from 'react';
import "../css/HeaderComponents.css";
import { Link } from "react-router-dom";
import { navbarList } from '../../Site_code/urls';

function NavBar(props){
    return (<div>
            <Link to="/">Home</Link>
            <Link to="/kettir">Kettir</Link>
        </div>);
}

function Brand(){
    return (
        <a  href="" id="brand">
            <strong>KYNJAKETTIR</strong>
            <small>KATTARÆKTARFÉLAG ÍSLANDS</small>
        </a>
    );
}

//Links = 
function Header(props){
    return (
        <div className="header">
            <Brand></Brand>
            <NavBar links={props.navbar}></NavBar>
        </div>
    );
}

export {NavBar, Brand, Header};