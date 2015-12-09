(function ($) {

    function Rectangle(x, y, width, height, margin) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.margin = margin;
    }

    Rectangle.prototype.style = function () {
        return {
            top: this.y + 'px',
            left: this.x + 'px',
            width: (this.width - this.margin) + "px",
            height: (this.height - this.margin) + "px"
        };
    };

    Rectangle.prototype.isWide = function () {
        return this.width > this.height;
    };

    function TreeMap($div, options) {
        options = options || {};
        this.$div = $div;

        $div.css('position', 'relative');
        this.rectangle = new Rectangle(0, 0, $div.width(), $div.height(), 0);

        this.nodeClass = function () {
            return '';
        };
        this.click = function () {
        };
        this.mouseenter = function () {
        };
        this.mouseleave = function () {
        };
        this.mousemove = function () {
        };
        this.paintCallback = function () {
        };
        this.ready = function () {
        };
        this.itemMargin = 0;
        this.smallestFontSize = 15;
        this.startingFontSize = 24;
        this.centerLabelVertically = true;

        $.extend(this, options);

        this.setNodeColors = function ($box, node) {
            if (this.backgroundColor)
                $box.css('background-color', this.backgroundColor($box, node));
            if (this.color)
                $box.css('color', this.color($box, node));
        };
    }

    TreeMap.SIDE_MARGIN = 20;
    TreeMap.TOP_MARGIN = 20;

    TreeMap.prototype.paint = function (nodeList) {
        nodeList = this.squarify(nodeList, this.rectangle);

        for (var i = 0; i < nodeList.length; i++) {
            var node = nodeList[i];
            var nodeBounds = node.bounds;

            var boxId = node.id || 'treemap-node-' + i;
            var $box = $('<div id=' + boxId + '></div>');
            $box.css($.extend(nodeBounds.style(), {
                'position': 'absolute'
            }));

            this.setNodeColors($box, node);

            $box.addClass('treemap-node');

            var self = this;
            $box.bind('click', node, function (e) {
                self.click(e.data, e);
            });
            $box.bind('mouseenter', node, function (e) {
                self.mouseenter(e.data, e);
            });
            $box.bind('mouseleave', node, function (e) {
                self.mouseleave(e.data, e);
            });
            $box.bind('mousemove', node, function (e) {
                self.mousemove(e.data, e);
            });

            $box.appendTo(this.$div);
            $box.addClass(this.nodeClass(node, $box));

            var $content = $("<div>" + node.label + "</div>");
            $content.addClass('treemap-label');
            $content.css({
                'display': 'inline',
                'position': 'relative',
                'text-align': 'center',
                'font-size': this.startingFontSize + 'px'
            });
            $box.append($content);

            this.fitLabelFontSize($content, node);

            if (this.centerLabelVertically) {
                $content.css('margin-top', (parseInt($box.height()) / 2) - (parseInt($content.height()) / 2) + 'px');
            }
        }
        this.ready();
    };

    TreeMap.prototype.fitLabelFontSize = function ($content, node) {
        var nodeBounds = node.bounds;
        while ($content.height() + TreeMap.TOP_MARGIN > nodeBounds.height || $content.width() + TreeMap.SIDE_MARGIN > nodeBounds.width) {
            var fontSize = parseFloat($content.css('font-size')) - 3;
            if (fontSize < this.smallestFontSize) {
                $content.remove();
                break;
            }
            $content.css('font-size', fontSize + 'px');
        }
        $content.css('display', 'block');
        this.paintCallback($content, node);
    };

    TreeMap.HORIZONTAL = 1;
    TreeMap.VERTICAL = 2;

    TreeMap.prototype.squarify = function (nodeList, rectangle) {
        nodeList.sort(function (a, b) {
            return b.value - a.value;
        });
        this.divideDisplayArea(nodeList, rectangle);

        return nodeList;
    };

    TreeMap.prototype.divideDisplayArea = function (nodeList, destRectangle) {
        // Check for boundary conditions
        if (nodeList.length === 0)
            return;

        if (nodeList.length == 1) {
            nodeList[0].bounds = destRectangle;
            return;
        }

        var halves = this.splitFairly(nodeList);

        var leftSum = this.sumValues(halves.left),
            rightSum = this.sumValues(halves.right),
            totalSum = leftSum + rightSum;

        if (destRectangle.isWide()) {
            var midPoint = Math.round((leftSum * destRectangle.width) / totalSum);
            this.divideDisplayArea(halves.left, new Rectangle(destRectangle.x, destRectangle.y, midPoint, destRectangle.height, this.itemMargin));
            this.divideDisplayArea(halves.right, new Rectangle(destRectangle.x + midPoint, destRectangle.y, destRectangle.width - midPoint, destRectangle.height, this.itemMargin));
        } else {
            var midPoint = Math.round((leftSum * destRectangle.height) / totalSum);
            this.divideDisplayArea(halves.left, new Rectangle(destRectangle.x, destRectangle.y, destRectangle.width, midPoint, this.itemMargin));
            this.divideDisplayArea(halves.right, new Rectangle(destRectangle.x, destRectangle.y + midPoint, destRectangle.width, destRectangle.height - midPoint, this.itemMargin));
        }
    };

    TreeMap.prototype.splitFairly = function (nodeList) {
        var halfValue = this.sumValues(nodeList) / 2;
        var accValue = 0;
        var length = nodeList.length;

        for (var midPoint = 0; midPoint < length; midPoint++) {
            if (midPoint > 0 && (accValue + nodeList[midPoint].value > halfValue))
                break;
            accValue += nodeList[midPoint].value;
        }

        return {
            left: nodeList.slice(0, midPoint),
            right: nodeList.slice(midPoint)
        };
    };

    TreeMap.prototype.sumValues = function (nodeList) {
        var result = 0;
        var length = nodeList.length;
        for (var i = 0; i < length; i++)
            result += nodeList[i].value;
        return result;
    };

    $.fn.treemap = function (json, options) {
        var self = this;
        return this.fadeOut('fast', function () {
            self.empty().fadeIn('fast', function () {
                new TreeMap(self, options).paint(json);
            });
        });
    };

})(jQuery);
