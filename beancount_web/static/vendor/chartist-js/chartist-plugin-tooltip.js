(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module.
    define(["chartist"], function (Chartist) {
      return (root.returnExportsGlobal = factory(Chartist));
    });
  } else if (typeof exports === 'object') {
    // Node. Does not work with strict CommonJS, but
    // only CommonJS-like enviroments that support module.exports,
    // like Node.
    module.exports = factory(require("chartist"));
  } else {
    root['Chartist.plugins.tooltips'] = factory(Chartist);
  }
}(this, function (Chartist) {

  /**
   * Chartist.js plugin to display a data label on top of the points in a line chart.
   *
   */
  /* global Chartist */
  (function (window, document, Chartist) {
    'use strict';

    var defaultOptions = {
      currency: undefined,
      tooltipOffset: {
        x: 0,
        y: -20
      },
      appendToBody: false,
      class: undefined
      // showTooltips: true,
      // tooltipEvents: ['mousemove', 'touchstart', 'touchmove'],
      // labelClass: 'ct-label',
      // labelOffset: {
      //   x: 0,
      //   y: -10
      // },
      // textAnchor: 'middle'
    };

    Chartist.plugins = Chartist.plugins || {};
    Chartist.plugins.tooltip = function (options) {
      options = Chartist.extend({}, defaultOptions, options);

      return function tooltip(chart) {
        var tooltipSelector = 'ct-point';
        if (chart instanceof Chartist.Bar) {
          tooltipSelector = 'ct-bar';
        } else if (chart instanceof Chartist.Pie) {
          // Added support for donut graph
          if (chart.options.donut) {
            tooltipSelector = 'ct-slice-donut';
          } else {
            tooltipSelector = 'ct-slice-pie';
          }
        }

        var $chart = chart.container;
        var $toolTip = $chart.querySelector('.chartist-tooltip');
        if (!$toolTip) {
          $toolTip = document.createElement('div');
          $toolTip.className = (!options.class) ? 'chartist-tooltip' : 'chartist-tooltip ' + options.class;
          if (!options.appendToBody) {
            $chart.appendChild($toolTip);
          } else {
            document.body.appendChild($toolTip);
          }
        }
        var height = $toolTip.offsetHeight;
        var width = $toolTip.offsetWidth;

        hide($toolTip);

        function on(event, selector, callback) {
          $chart.addEventListener(event, function (e) {
            if (!selector || hasClass(e.target, selector))
              callback(e);
          });
        }

        on('mouseover', tooltipSelector, function (event) {
          var $point = event.target;
          var tooltipText = '';

          var meta = $point.getAttribute('ct:meta') || $point.parentNode.getAttribute('ct:meta') || $point.parentNode.getAttribute('ct:series-name') || '';
          var value = $point.getAttribute('ct:value');

          if (options.tooltipFnc) {
            tooltipText = options.tooltipFnc(meta, value);
          } else {

            meta = '<span class="chartist-tooltip-meta">' + meta + '</span>';
            value = '<span class="chartist-tooltip-value">' + value + '</span>';

            if (meta) {
              tooltipText += meta + '<br>';
            } else {
              // For Pie Charts also take the labels into account
              // Could add support for more charts here as well!
              if (chart instanceof Chartist.Pie) {
                var label = next($point, 'ct-label');
                if (label.length > 0) {
                  tooltipText += text(label) + '<br>';
                }
              }
            }

            if (options.currency) {
              value = options.currency + value.replace(/(\d)(?=(\d{3})+(?:\.\d+)?$)/g, "$1,");
            }
            tooltipText += value;
          }

          $toolTip.innerHTML = tooltipText;
          setPosition(event);
          show($toolTip);

          // Remember height and width to avoid wrong position in IE
          height = $toolTip.offsetHeight;
          width = $toolTip.offsetWidth;
        });

        on('mouseout', tooltipSelector, function () {
          hide($toolTip);
        });

        on('mousemove', null, function (event) {
          setPosition(event);
        });

        function setPosition(event) {
          // For some reasons, on FF, we can't rely on event.offsetX and event.offsetY,
          // that's why we prioritize event.layerX and event.layerY
          // see https://github.com/gionkunz/chartist-js/issues/381
          height = height || $toolTip.offsetHeight;
          width = width || $toolTip.offsetWidth;
          if (!options.appendToBody) {
            $toolTip.style.top = (event.layerY || event.offsetY) - height + options.tooltipOffset.y + 'px';
            $toolTip.style.left = (event.layerX || event.offsetX) - width / 2 + options.tooltipOffset.x + 'px';
          } else {
            $toolTip.style.top = event.pageY - height  + options.tooltipOffset.y + 'px';
            $toolTip.style.left = event.pageX - width / 2 + options.tooltipOffset.x + 'px';
          }
        }
      }
    };

    function show(element) {
      element.classList.add('tooltip-show');
    }

    function hide(element) {
      element.classList.remove('tooltip-show');
    }

    function hasClass(element, className) {
      return (' ' + element.getAttribute('class') + ' ').indexOf(' ' + className + ' ') > -1;
    }

    function next(element, className) {
      do {
        element = element.nextSibling;
      } while (element && !hasClass(element, className));
      return element;
    }

    function text(element) {
      return element.innerText || element.textContent;
    }

  } (window, document, Chartist));

  return Chartist.plugins.tooltips;

}));
