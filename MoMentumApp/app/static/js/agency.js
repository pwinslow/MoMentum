/*!
 * Start Bootstrap - Agency Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

// JS function that provides a probability gauge
 function probability_needle(needle_position){
         var gaugeOptions = {

             chart: {
                 type: 'solidgauge'
             },

             credits: {
               enabled: false
             },

             title: null,

             pane: {
                 center: ['50%', '85%'],
                 size: '140%',
                 startAngle: -90,
                 endAngle: 90,
                 background: {
                     backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
                     innerRadius: '60%',
                     outerRadius: '100%',
                     shape: 'arc'
                 }
             },

             tooltip: {
                 enabled: false
             },

             // the value axis
             yAxis: {
                 stops: [
                     [0.1, '#55BF3B'], // green
                     [0.5, '#DDDF0D'], // yellow
                     [0.9, '#DF5353'] // red
                 ],
                 lineWidth: 0,
                 minorTickInterval: null,
                 tickAmount: 5,
                 title: {
                     y: -85
                 },
                 labels: {
                     y: 16
                 }
             },

             plotOptions: {
                 solidgauge: {
                     dataLabels: {
                         y: 5,
                         borderWidth: 0,
                         useHTML: true
                     }
                 }
             }
           };

           // The speed gauge
           var chartSpeed = Highcharts.chart('probability-needle', Highcharts.merge(gaugeOptions, {
             yAxis: {
                 min: 0,
                 max: 100,
                 title: {
                     //text: 'Probability of Petition Success'
                     text: '<div style="text-align:center"><span style="font-size:20px;color:black">Probability of Petition Success</span></div>'
                 }
             },
             series: [{
                 //name: 'Speed',
                 data: [needle_position],
                 dataLabels: {
                     format: '<div style="text-align:center"><span style="font-size:25px;color:black">{y}%</span></div>'
                 }
             }]
           }));
     };

     function feature_importance(){

     Highcharts.chart('bar_chart', {
         chart: {
             type: 'bar'
         },
         title: {
             text: 'Recommendations for improving your score',
             style: {
               fontSize: "25px"
             }
         },
         xAxis: {
             categories: ['Verb Count',
                          'Subjectivity',
                          'Words per sentence',
                          'Adjective Count',
                          'Sentence Count',
                          'Polarity',
                          'Link Count'],
              labels: {
                style: {
                  fontSize: "15px"
                }
              }
         },
         yAxis: {
             min: 0,
             max: 10,
             title: {
                 text: 'Feature Importance (%)',
                 align: 'high',
                 style: {
                   fontSize: "20px"
                 }
             },
             labels: {
                 overflow: 'justify',
                 style: {
                   fontSize: "15px"
                 }
             }
         },
         tooltip: {
             formatter: function () {
                         console.log(this);
                     if(this.point.fullCategory)
                         txt = ' ' + this.point.fullCategory;
                     return txt;
                 }
         },
         plotOptions: {
             bar: {
                 dataLabels: {
                     enabled: true,
                     align: "right"
                 }
             }
         },

         credits: {
             enabled: false
         },
         series: [{
         		showInLegend: false,
             data: [{y: 6.4,
                      fullCategory: "Higher verb counts are correlated with a higher probability for victory!<br> Remember, a petition is a call to action."},
                    {y: 5.7,
                      fullCategory: "Higher levels of subjectiveness are correlated with a higher probability for victory!<br> Successful petitions relate to their audience by expressing their personal opinions about the topic."},
                    {y: 5.6,
                      fullCategory: "Successful petitions are correlated with a specific formula for words per sentence.<br> Keeping it short in both the title and overview but let 'em have it in the letter body!"},
                    {y: 5.2,
                      fullCategory: "Higher adjective counts are correlated with higher probability for victory!<br> Be descriptive!"},
                    {y: 4.7,
                      fullCategory: "Higher sentence counts in the letter body are correlated with higher probability for victory.<br> Let people know that you're planning on giving the target of the petition an earful!"},
                    {y: 4.3,
                      fullCategory: "Successful petitions are correlated with a specific formula for polarity (a measure of how positive/negative your text is).<br> Stay positive in the letter body when writing to your target but, in the overview, a bit of negativity helps motivate people to action."},
                    {y: 3,
                      fullCategory: "A healthy amount of citation (including url links) in the overview is correlated with higher probability for victory.<br> But beware, inserting links anywhere else will cost you!"}
                    ]
         }]
     });

     };


// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });

    if (class_prob){

      // This function forces the visualizations to wait until the page they're on is in view
      $(function () {
        var $window = $(window),
            didScroll = false,
            skillsTop = $('#results').offset().top - 40;

        $window.on('scroll', function () {
            didScroll = true;
        });

        setInterval(function () {
            if (didScroll) {
                didScroll = false;
                if ($window.scrollTop() >= skillsTop) {

                    // Run custom js visualizations
                    probability_needle(class_prob);
                    feature_importance();

                }
            }
        }, 250);

        });

    }

});

// Highlight the top nav as scrolling occurs
$('body').scrollspy({
    target: '.navbar-fixed-top'
})

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});
