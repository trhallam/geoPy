/**
 * JavaScripts to return variables in an object.
 * 
 */
 
returnJS.dir = function(object) {
    stuff = [];
    for (s in object) {
        stuff.push(s);
    }
    stuff.sort();
    return stuff.toString();
}