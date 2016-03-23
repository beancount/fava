var Clipboard = require('clipboard');

module.exports.initClipboard = function() {
    new Clipboard('.status-indicator');
    new Clipboard('#copy-balances', {
        text: function(trigger) {
            var text = trigger.getAttribute('data-clipboard-text').split('\n');
            text.splice(0, 2);
            return text.join('\n').trim();
        }
    });
};
