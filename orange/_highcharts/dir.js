/**
 * JavaScripts to return variables in an object.
 * 
 */
 /**/
dir = function(object) {
    stuff = [];
    for (s in object) {
        stuff.push(s);
    }
    stuff.sort();
    return String(stuff);
};

test2 = function() { alert("h2");};