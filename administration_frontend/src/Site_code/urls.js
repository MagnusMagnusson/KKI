let urls = {};

urls.HOME = "/";
urls.CATS = "/kettir";
urls.CATSEARCH = urls.CATS;
urls.CATPROFILE = urls.CATS + "/:catid";

const makePage = (name, path) => {
    return {name, path};
}

const makeCategory = (name, links) => {
    return {name, links};
}
const navbarList = [
    makeCategory("Kettir", [
        makePage("Leit", urls.CATSEARCH)]
    ),
    makeCategory("Félagar",[]),
    makeCategory("Ræktanir",[]),
    makeCategory("Sýningar",[])
];

export default urls;
export {urls, navbarList};