function isset(object){
    return (object in window);  // only works in a browser
}

$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

//  Checks that string starts with the specific string
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str) {
        return this.slice(0, str.length) == str;
    };
}

// http://stackoverflow.com/a/25359264
$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}

// http://stackoverflow.com/a/27385169
var decodeEntities = (function() {
    // this prevents any overhead from creating the object each time
    var element = document.createElement('div');

    // regular expression matching HTML entities
    var entity = /&(?:#x[a-f0-9]+|#[0-9]+|[a-z0-9]+);?/ig;

    return function decodeHTMLEntities(str) {
        // find and replace all the html entities
        str = str.replace(entity, function(m) {
            element.innerHTML = m;
            return element.textContent;
        });

        // reset the value
        element.textContent = '';

        return str;
    }
})();

// Formats the given number to two fixed decimals.
function formatCurrency(x) {
    return parseFloat(x).toFixed(2)
}

// Formats the given date according to formatString.
// Currently only the following formatString-parts are defined:
//     MMM => Month-name in 3-letter-English
//     YY  => Last two digits of the year
if (typeof Date.prototype.formatWithString != 'function') {
    var defaultLocaleMonthsShort = 'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_');
    Date.prototype.formatWithString = function (formatString) {
        var dateStr = formatString;
        dateStr = dateStr.replace('YY', this.getYear().toString().slice(-2));
        dateStr = dateStr.replace('MMM', defaultLocaleMonthsShort[this.getMonth()]);
        return dateStr;
    };
}

// http://stackoverflow.com/a/7195920
function isNumber(num) {
    return (typeof num == 'string' || typeof num == 'number') && !isNaN(num - 0) && num !== '';
};
