/*
 Template Name: Inspire - Bootstrap 4 Admin Dashboard
 Author: UIdeck
 Website: www.uideck.com
File: morris init js
 */

!(function ($) {
  'use strict'

  var MorrisCharts = function () {}

  //creates line chart
  ;(MorrisCharts.prototype.createLineChart = function (
    element,
    data,
    xkey,
    ykeys,
    labels,
    lineColors
  ) {
    Morris.Line({
      element: element,
      data: data,
      xkey: xkey,
      ykeys: ykeys,
      labels: labels,
      hideHover: 'auto',
      gridLineColor: '#eef0f2',
      resize: true, //defaulted to true
      lineColors: lineColors,
    })
  }),
   
    (MorrisCharts.prototype.init = async function () {
      var $lineData = [
        { y: '2018-01-01', a: 10 },
        { y: '2018-01-02', a: 20 },
        { y: '2018-01-03', a: 30 },
        { y: '2018-01-04', a: 40 },
        { y: '2018-01-05', a: 50 },
        { y: '2018-01-06', a: 60 },
        { y: '2018-01-07', a: 70 },
        { y: '2018-01-08', a: 80 },
        { y: '2018-01-09', a: 90 },
        { y: '2018-01-10', a: 100 }
      ];
      $.ajax({
        url: 'https://api.thingspeak.com/channels/2281910/fields/4.json?results=10',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          $lineData = data.feeds.map(function(feed) {
            return { y: feed.created_at, a: parseInt(feed.field4) };
          });
            console.log($lineData);
            MorrisCharts.prototype.createLineChart(
              'morris-line-example',
              $lineData,
              'y',
              ['a'],
              ['Data'],
              ['green']
              );
            },
            error: function(xhr, status, error) {
              console.error(error);
            }
          });
    }),
    //init
    ($.MorrisCharts = new MorrisCharts()),
    ($.MorrisCharts.Constructor = MorrisCharts)
})(window.jQuery),
  //initializing
  (function ($) {
    'use strict'
    $.MorrisCharts.init()
  })(window.jQuery)
