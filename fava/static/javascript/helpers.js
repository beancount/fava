// Fix sidebar styling
$(document).ready(function() {
    var mainHeight = $('.main').outerHeight();
    var minHeight = $(window).height() - $('header').offset().top - $('header').outerHeight();
    var sidebarHeight = $('aside').outerHeight();
    $('.main, aside').css('min-height', Math.max(mainHeight, minHeight, sidebarHeight) + 'px');
});

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

// http://stackoverflow.com/a/27385169
window.decodeEntities = (function() {
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

// Test if Number supports toLocaleString
// http://stackoverflow.com/questions/31871771/testing-for-tolocalestring-support/31872133#31872133
function toLocaleStringSupportsOptions() {
  return !!(typeof Intl == 'object' && Intl && typeof Intl.NumberFormat == 'function');
}

if (toLocaleStringSupportsOptions() == false) {
    Number.prototype.toLocaleString = function(locale, opts) {
        var x = this.valueOf();
        if (opts && opts.minimumFractionDigits) {
            x = parseFloat(x).toFixed(opts.minimumFractionDigits);
        }
        var sx = (''+x).split('.'), s = '', i, j;
        i = sx[0].length;
        while (i > 3) {
            j = i - 3;
            s = ',' + sx[0].slice(j, i) + s;
            i = j;
        }
        s = sx[0].slice(0, i) + s;
        sx[0] = s;
        return sx.join('.');
    };
};

// Formats the given number to two fixed decimals.
window.formatCurrency = function (x) {
    return parseFloat(x).toLocaleString(undefined, { minimumFractionDigits: 2 })
}

// Formats the given date according to formatString.
// Currently only the following formatString-parts are defined:
//     MMM => Month-name in 3-letter-English
//     YY  => Last two digits of the year
if (typeof Date.prototype.formatWithString != 'function') {
    var defaultLocaleMonthsShort = 'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec'.split('_');
    Date.prototype.formatWithString = function (formatString) {
        var dateStr = formatString;
        dateStr = dateStr.replace('YYYY', this.getFullYear().toString());
        dateStr = dateStr.replace('YY', this.getFullYear().toString().slice(-2));
        dateStr = dateStr.replace('MMM', defaultLocaleMonthsShort[this.getMonth()]);
        return dateStr;
    };
}

// http://stackoverflow.com/a/7195920
window.isNumber = function(num) {
    return (typeof num == 'string' || typeof num == 'number') && !isNaN(num - 0) && num !== '';
};

window.pad = function(n) { return n < 10 ? '0' + n : n };
