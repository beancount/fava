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

if (toLocaleStringSupportsOptions() === false) {
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
module.exports.formatCurrency = function (x) {
    return parseFloat(x).toLocaleString(undefined, { minimumFractionDigits: 2 })
}

// https://gist.github.com/dblock/1081513
Date.prototype.getWeek = function() {
    // Create a copy of this date object
    var target = new Date(this.valueOf());

    // ISO week date weeks start on monday, so correct the day number
    var dayNr = (this.getDay() + 6) % 7;

    // Set the target to the thursday of this week so the
    // target date is in the right year
    target.setDate(target.getDate() - dayNr + 3);

    // ISO 8601 states that week 1 is the week with january 4th in it
    var jan4 = new Date(target.getFullYear(), 0, 4);

    // Number of days between target date and january 4th
    var dayDiff = (target - jan4) / 86400000;

    if (new Date(target.getFullYear(), 0, 1).getDay() < 5) {
        // Calculate week number: Week 1 (january 4th) plus the
        // number of weeks between target date and january 4th
        return 1 + Math.ceil(dayDiff / 7);
    }
    else {  // jan 4th is on the next week (so next week is week 1)
        return Math.ceil(dayDiff / 7);
    }
};

Date.prototype.getQuarter = function() {
    var month = new Date(this.valueOf()).getMonth();
    if (month < 3)               { return 1; }
    if (month > 2 && month < 6)  { return 2; }
    if (month > 5 && month < 9)  { return 3; }
    else                         { return 4; }
}

// http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript
function pad(num, size){ return ('000000000' + num).substr(-size); }

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
        dateStr = dateStr.replace('MM', pad(this.getMonth() + 1, 2));
        dateStr = dateStr.replace('DD', pad(this.getDay(), 2));
        dateStr = dateStr.replace('ww', pad(this.getWeek(), 2));
        dateStr = dateStr.replace('q', this.getQuarter().toString());
        return dateStr;
    };
}

// http://stackoverflow.com/a/7195920
module.exports.isNumber = function(num) {
    return (typeof num == 'string' || typeof num == 'number') && !isNaN(num - 0) && num !== '';
};

module.exports.pad = function(n) { return n < 10 ? '0' + n : n };
