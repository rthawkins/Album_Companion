
$('[data-toggle="tooltip"]').tooltip();

$.getJSON(`/album/${selected_album}/lyrics`,
function (myWords) {

      // set the dimensions and margins of the graph
var margin = {top: 0, right: 0, bottom: 0, left: 0},
width = 300 - margin.left - margin.right,
height = 350 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.selectAll("#wordchart,#wordchartmobile").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform",
      "translate(" + margin.left + "," + margin.top + ")");

// Constructs a new cloud layout instance. It run an algorithm to find the position of words that suits your requirements
// Wordcloud features that are different from one word to the other must be here
var layout = d3.layout.cloud()
.size([width, height])
.words(myWords.map(function(d) { return {text: d.word, size:d.size}; }))
.padding(5)        //space between words
// .rotate(function() { return ~~(Math.random() * 2) * 90; })
.fontSize(function(d) { return d.size * 3; })      // font size of words
.on("end", draw);
layout.start();

// This function takes the output of 'layout' above and draw the words
// Wordcloud features that are THE SAME from one word to the other can be here
function draw(words) {
svg
.append("g")
  .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
  .selectAll("text")
    .data(words)
  .enter().append("text")
    .style("font-size", function(d) { return d.size; })
    .style("fill", "#116aa6")
    .attr("text-anchor", "middle")
    .style("font-family", "Verdana")
    .attr("transform", function(d) {
      return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
    })
    .text(function(d) { return d.text; })
}
    });

$.getJSON(`/album/${selected_album}/lyrics`,
  function(data) {
  total_words = d3.sum(data,d => d.size);
  let tr_themes = $("<tr><td><b>Drugs</b></td><td>"+ ((d3.sum(data.filter(d => d.category == 'Drug'),d => d.size)/ total_words)*100).toFixed(1)+"%</td></tr>"
  +"<tr><td><b>Nature</b></td><td>"+ ((d3.sum(data.filter(d => d.category == 'Nature'),d => d.size)/ total_words)*100).toFixed(1)+"%</td></tr>"
  +"<tr><td><b>Politics</b></td><td>"+ ((d3.sum(data.filter(d => d.category == 'Political'),d => d.size)/ total_words)*100).toFixed(1)+"%</td></tr>"
  +"<tr><td><b>Romance</b></td><td>"+ ((d3.sum(data.filter(d => d.category == 'Romance'),d => d.size)/ total_words)*100).toFixed(1)+"%</td></tr>"
  +"<tr><td><b>Spirituality</b></td><td>"+ ((d3.sum(data.filter(d => d.category == 'Spiritual'),d => d.size)/ total_words)*100).toFixed(1)+"%</td></tr>");
  // Remove features
  tr_themes.appendTo("#themes","#themes_mobile");
  }
  );

$.getJSON(`/album/${selected_album}`,
    function (data) {
        var tr;
        for (var i = 0; i < data.length; i++) {
            tr = $('<tr/>');
            tr.append("<td> "+ data[i].track+"</td>");
            tr.append("<td> <a href='/song/"+ data[i].sp_id + "'> " + data[i].title + "</td>");
            $('#album_table').append(tr);
            tr.appendTo("#album_table, #album_table_mobile");
        }

      var data_source = data.filter(data => data.duration > 1 && data.speechiness <.8);

      let tr_summary = $("<tr><td><i>Representative</i></td><td><a href='/song/" + _.minBy(data_source, 'uniqueness').sp_id + "'> " +  _.minBy(data_source, 'uniqueness').title + "</td></tr>"
      +"<tr><td><i>Unique</i></td><td><a href='/song/" + _.maxBy(data_source, 'uniqueness').sp_id + "'> " + _.maxBy(data_source, 'uniqueness').title + "</td></tr>"
      +"<tr><td><i>Energetic</i></td><td><a href='/song/" + _.maxBy(data_source, 'energy').sp_id + "'> " + _.maxBy(data_source, 'energy').title + "</td></tr>"
      +"<tr><td><i>Slow</i></td><td><a href='/song/" + _.minBy(data_source, 'energy').sp_id + "'> " + _.minBy(data_source, 'energy').title + "</td></tr>"
      +"<tr><td><i>Positive</i></td><td><a href='/song/" + _.maxBy(data_source, 'mood').sp_id + "'> " + _.maxBy(data_source, 'mood').title + "</td></tr>"
      +"<tr><td><i>Negative</i></td><td><a href='/song/" + _.minBy(data_source, 'mood').sp_id + "'> " + _.minBy(data_source, 'mood').title + "</td></tr>"
      +"<tr><td><i>Danceable</i></td><td><a href='/song/" + _.maxBy(data_source, 'danceability').sp_id + "'> " + _.maxBy(data_source, 'danceability').title + "</td></tr>"
      +"<tr><td><i>Lexically Diverse</i></td><td><a href='/song/" + _.maxBy(data_source, 'msttr').sp_id + "'> " + _.maxBy(data_source, 'msttr').title + "</td></tr>"
      +"<tr><td><i>Wordy</i></td><td><a href='/song/" + _.maxBy(data_source, 'lexical_depth').sp_id + "'> " + _.maxBy(data_source, 'lexical_depth').title + "</td></tr>"
      +"<tr><td><i>Lyrically Cliche</i></td><td><a href='/song/" + _.maxBy(data_source, 'cliche_word_perc').sp_id + "'> " + _.maxBy(data_source, 'cliche_word_perc').title + "</td></tr>")

      // let track_attributes = $(`<tr><td><b>Time Signature</b></td><td>${data.time_signature}/4</td><td><span></span></td></tr>`
      // +`<tr><td><b>Key</b></td><td>${data.key} ${data.mode}</td><td><span></span></td></tr>`
      // +`<tr><td><b>Energy</b></td><td>${data.energy_des} (${data.energy})</td><td><span class="barchart-energy"></span></td></tr>`
      // +`<tr><td><i class="fa fa-info-circle" title="Average of musical valence and lyrical sentiment"></i><b> Overall Mood</b></td><td>${data.mood_des} (${data.mood})</td><td><span class="barchart-mood"></span></td></tr>`
      // +`<tr><td><i class="fa fa-info-circle" title="How positive the song <i>sounds</i>, according to Spotify"></i><b> Musical Valence</b></td><td>${data.valence_des} (${data.mus_valence})</td><td><span class="barchart-valence"></span></td></tr>`
      // +`<tr><td><i class="fa fa-info-circle" title="Based on language sentiment analysis by <a href="https://www.nltk.org/index.html" target="_blank">NLTK</a>, scaled to the Spotify 0-1 value range"></i><b> Lyrical Sentiment</b></td><td>${data.lyr_valence_des} (${data.lyr_valence})</td><td><span class="barchart-lyrics"></span></td></tr>`
      // +`<tr><td><b>Danceability</b></td><td>${data.dance_des} (${data.danceability})</td><td><span class="barchart-dance"></span></td></tr>`
      // +`<tr><td><i class="fa fa-info-circle" title="Represents how lyrically diverse the songs are. Calculated as the number of unique words out of the total words. The average pop song is around 55%."></i><b> Lexical Diversity</b></td><td id="diverse"></td><td></td></tr>`
      // +`<tr><td><i class="fa fa-info-circle" title="Percentage of words containing baby, love, feel, boy/girl, happy/sad, and heart. The average pop song is around 4%."></i><b> Lyrical Cliche</b></td><td id="cliche"></td><td></td></tr>`);

      tr_summary.appendTo("#album_highlights_mobile, #album_highlights");
      // Track attributes for the future
      // track_attributes.appendTo("#album_highlights_mobile, #album_highlights");

// Charting total album attributes
      function meanVal(value) {
        return d3.mean(data, function(d) {return d [value] })
    }

    function text_value(value) {
      if(value>.8){var description="Very High";}
      else if(value>.6){var description="High";}
      else if(value>.4){var description="Neutral";}
      else if(value>.2){var description="Low";}
      else{var description="Very Low";}
      return description
    }

    function pos_neg(value) {
      if(value>.8){var description="Very Positive";}
      else if(value>.6){var description="Positive";}
      else if(value>.4){var description="Neutral";}
      else if(value>.2){var description="Negative";}
      else{var description="Very Negative";}
      return description
    }
    var album_energy = meanVal('energy').toFixed(3);
    var album_energy_desc = text_value(album_energy);
    var album_mood = meanVal('mood').toFixed(3);
    var album_mood_desc = pos_neg(album_mood);
    var album_mus_valence = meanVal('mus_valence').toFixed(3);
    var album_mus_valence_desc = pos_neg(album_mus_valence);
    var album_lyr_valence = meanVal('lyr_valence').toFixed(3);
    var album_lyr_valence_desc = pos_neg(album_lyr_valence);
    var album_dance = meanVal('danceability').toFixed(3);
    var album_dance_desc = text_value(album_dance);
    var album_ttr = (meanVal('msttr')*100).toFixed(1);
    var album_lexicaldepth = meanVal('lexical_depth').toFixed(0);
    var album_cliche = d3.sum(data,d => d.cliche_total_words);
    var album_total_words = d3.sum(data,d => d.lexical_depth);
    var cliche_perc = ((album_cliche/album_total_words)*100).toFixed(1);
    var upbeat_perc = ((data.filter(data => data.energy > .5 && data.mood >.5).length / data.length)*100).toFixed(0);
    var chill_perc = ((data.filter(data => data.energy < .5 && data.mood >.5).length / data.length)*100).toFixed(0);
    var aggr_perc = ((data.filter(data => data.energy > .5 && data.mood <.5).length / data.length)*100).toFixed(0);
    var somber_perc = ((data.filter(data => data.energy < .5 && data.mood <.5).length / data.length)*100).toFixed(0);
    


    let tr_album_stats = $("<tr><td><b>Upbeat Tracks</b></td><td>" + upbeat_perc + "%</td></tr>"
      +"<tr><td><b>Chill Tracks</b></td><td>" + chill_perc + "%</td></tr>"
      +"<tr><td><b>Aggressive/Cathartic Tracks</b></td><td>" + aggr_perc + "%</td></tr>"
      +"<tr><td><b>Somber Tracks</b></td><td>" + somber_perc + "%</td></tr>"
      +"<tr><td><b>Danceability</b></td><td>" + album_dance_desc + "</td></tr>"
      + '<tr><td><i class="fa fa-info-circle" title="Represents the quantity of lyrics per song. Calculated as the number of lexical words (n, adv, adj, v) per song. Avg: 109"></i><b> Lexical Richness</b></td><td>' + album_lexicaldepth + " per song</td></tr>"
      +'<tr><td><i class="fa fa-info-circle" title="Represents how lyrically diverse the songs are. Calculated as the number of unique words out of the total words. Avg: 55.8%"></i><b> Lexical Diversity</b></td><td>' + album_ttr + "%</td></tr>"
      +'<tr><td><i class="fa fa-info-circle" title="Percentage of words containing baby, love, feel, boy/girl, happy/sad, and heart. Avg: 4%"></i><b> Cliche Pop Words</b></td><td>' + cliche_perc + "%</td></tr>")
      tr_album_stats.appendTo("#album-stats,#album-stats-mobile");
    });

  Plotly.d3.json(`/album/${selected_album}`, function(data){

    // arrays for plotting selected states
    chart_track = [];
    chart_energy = [];
    chart_mood = [];
    chart_unique = [];
    hover_vibe = [];
    song_links = [];

    // populate arrays differently, controlling for if the user is looking at all states, highlighting a state, or isolating a state
    data.forEach(d => {
        chart_track.push(d.track);
        chart_energy.push(d.energy);
        chart_mood.push(d.mood);
        chart_unique.push(d.uniqueness * 10);
        song_links.push("/song/"+d.sp_id);
        hover_vibe.push(d.title)});

    var vibe_chart_trace = {
        x: chart_track,
        y: chart_energy,
        hovertemplate: '<b>%{text}</b><br>Energy: %{y:.2f}<br>Mood: %{marker.color:.2f}<extra></extra>',
        text: hover_vibe,
        marker: {
        color: chart_mood, cmin: 0, cmax: 1,
          colorscale: [
            ['0.0', '#a11d33'],
            ['0.1', '#b21e35'],
            ['0.2', '#c71f37'],
            ['0.3', '#f26a8d'],
            ['0.4', '#000000'],
            ['0.5', '#000000'],
            ['0.6', '#000000'],
            ['0.7', '#05668d'],
            ['0.8', '#028090'],
            ['0.9', '#00a896'],
            ['1.0', '#02c39a']],
            size: 10, symbol: 'diamond'
          },
          line: {
            color: '#000000',
            width: 1
          },
        title: false,
        mode: 'lines+markers',
        type: 'scatter'
      };

    var track_chart_trace = {
        x: chart_mood,
        y: chart_energy,
        hovertemplate: '<b>%{text}</b><br>Energy: %{y:.2f}<br>Mood: %{x:.2f}<extra></extra>',
        text: hover_vibe,
        marker: {
            size: chart_unique, line: {
              color: 'black', width: 2
          }
        },
        name: 'Album Tracks',
        mode: 'markers',
        type: 'scatter'
      };

    var song_highlight_track = {
        x: [s_mood],
        y: [s_energy],
        hovertemplate: '<b>%{text}</b><br>Energy: %{y:.2f}<br>Mood: %{x:.2f}<extra></extra>',
        text: [hover_vibe[s_tracknum-1]],
        name: 'This Song',
        mode: 'markers',
        type: 'scatter',
        marker: {color: '#d9a868',
        size: chart_unique[s_tracknum-1], line: {
            color: 'black', width: 2
        }}
      };

    var song_highlight_vibe = {
        x: [s_tracknum],
        y: [s_energy],
        hovertemplate: '<b>%{text}</b><br>Energy: %{y:.2f}<br>Mood: %{marker.color:.2f}<extra></extra>',
        text: [hover_vibe[s_tracknum-1]],
        mode: 'markers',
        type: 'scatter',
        marker: {
          color: [chart_mood[s_tracknum-1]], cmin: 0, cmax: 1,
            colorscale: [
              ['0.0', '#a11d33'],
              ['0.1', '#b21e35'],
              ['0.2', '#c71f37'],
              ['0.3', '#f26a8d'],
              ['0.4', '#000000'],
              ['0.5', '#000000'],
              ['0.6', '#000000'],
              ['0.7', '#05668d'],
              ['0.8', '#028090'],
              ['0.9', '#00a896'],
              ['1.0', '#02c39a']],
              size: 8, symbol: 'diamond',
              line: {
            color: '#d9a868', width: 2
        }}
      };
    
    var vibe_chart_ref = [vibe_chart_trace,song_highlight_vibe];
    var track_chart_ref = [track_chart_trace, song_highlight_track];

    var layout_vibe = {
                  title: false,
                  titlefont: {
                        color: '#f2f0f0',
                        size: 14
                  },
                  showlegend: false,
                  xaxis: {
                    title: 'Tracks',
                    titlefont: {
                        color: 'black',
                        size: 8
                        },
                    showgrid: false,
                    zeroline: false,
                    linecolor: 'black',
                    dtick: 1,
                    ticks: 'outside',
                    tickfont: {color: 'black',
                    size: 10
                }
                  },
                  yaxis: {
                    title: 'Energy',
                    titlefont: {
                        color: 'black',
                        size: 11
                        },
                    linecolor: 'black',
                    gridwidth: 1,
                    gridcolor: 'black',
                    tickvals: [0,.5,1], 
                    range: [0,1],
                    tickfont: {color: 'black',
                    size: 10
                },
                  },
                  margin: {
                    l: 50,
                    r: 50,
                    b: 50,
                    t: 10
                  },
                  width: 290,
                  height: 250,
                  paper_bgcolor: 'rgba(0, 0, 0,0)',
                  plot_bgcolor: 'rgba(0, 0, 0,0)',
                  hovermode: 'closest'
                };

        var layout_vibe_mobile = {
          title: false,
          titlefont: {
                color: 'black',
                size: 14
          },
          showlegend: false,
          xaxis: {
            title: 'Tracks',
            titlefont: {
                color: '#AEAEAE',
                size: 8
                },
            showgrid: false,
            zeroline: false,
            linecolor: 'black',
            dtick: 1,
            ticks: 'outside',
            tickfont: {color: 'black',
            size: 10
        }
          },
          yaxis: {
            linecolor: 'black',
            gridwidth: 2,
            gridcolor: 'black',
            tickvals: [0,.5,1], 
            range: [0,1],
            tickfont: {color: 'black',
            size: 10
        },
          },
          margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 10
          },
          width: 290,
          height: 250,
          paper_bgcolor: 'rgba(0, 0, 0,0)',
          plot_bgcolor: 'rgba(0, 0, 0,0)',
          hovermode: 'closest'
        };

    var layout_track = {
        title: false,
        titlefont: {
                color: 'black',
                size: 14
        },
        showlegend: false,
        xaxis: {
            title: 'Mood',
            titlefont: {
                color: 'black',
                size: 11
                },
            showgrid: true,
            zeroline: true,
            gridwidth: 1,
            gridcolor: '#AEAEAE',
            linecolor: 'black',
            ticks: 'outside',
            tickfont: {color: 'black',
                    size: 10
                },
            tickvals: [.5,1], 
            range: [0,1],
        },
        yaxis: {
            title: 'Energy',
            titlefont: {
                color: 'black',
                size: 11
                },
            linecolor: 'black',
            gridwidth: 1,
            gridcolor: '#AEAEAE',
            tickvals: [0,.5,1], 
            range: [0,1],
            tickfont: {color: 'black',
            size: 10
        },
        },
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 10
        },
        width: 290,
        height: 250,
        paper_bgcolor: 'rgba(0, 0, 0,0)',
        plot_bgcolor: 'rgba(0, 0, 0,0)',
        hovermode: 'closest',
        annotations: [
          {
            x: .75,
            y: .99,
            xref: 'x',
            yref: 'y',
            text: 'Upbeat',
            font: {
              family: 'Verdana',
              size: 9,
              color: '#AEAEAE'},
            showarrow: false,
          },
          {
            x: .25,
            y: .99,
            xref: 'x',
            yref: 'y',
            text: 'Aggressive/Cathartic',
            font: {
              family: 'Verdana',
              size: 8,
              color: '#AEAEAE'},
            showarrow: false,
          },
          {
            x: .25,
            y: .05,
            xref: 'x',
            yref: 'y',
            text: 'Somber',
            font: {
              family: 'Verdana',
              size: 9,
              color: '#AEAEAE'},
            showarrow: false,
          },
          {
            x: .75,
            y: .05,
            xref: 'x',
            yref: 'y',
            text: 'Chill',
            font: {
              family: 'Verdana',
              size: 9,
              color: '#AEAEAE'},
            showarrow: false,
          },
        ]
        };

    var layout_track_mobile = {
      title: false,
      titlefont: {
              color: 'black',
              size: 14
      },
      showlegend: false,
      xaxis: {
          title: 'Mood',
          titlefont: {
              color: 'black',
              size: 11
              },
          showgrid: true,
          zeroline: true,
          gridwidth: 2,
          gridcolor: 'black',
          linecolor: 'black',
          ticks: 'outside',
          tickfont: {color: 'black',
                  size: 10
              },
          tickvals: [.5,1], 
          range: [0,1],
      },
      yaxis: {
          title: 'Energy',
          titlefont: {
              color: '#black',
              size: 11
              },
          linecolor: 'black',
          gridwidth: 2,
          gridcolor: 'black',
          tickvals: [0,.5,1], 
          range: [0,1],
          tickfont: {color: 'black',
          size: 10
      },
      },
      margin: {
          l: 50,
          r: 50,
          b: 50,
          t: 10
      },
      width: 290,
      height: 250,
      paper_bgcolor: 'rgba(0, 0, 0,0)',
      plot_bgcolor: 'rgba(0, 0, 0,0)',
      hovermode: 'closest',
      annotations: [
        {
          x: .75,
          y: .99,
          xref: 'x',
          yref: 'y',
          text: 'Upbeat',
          font: {
            family: 'Verdana',
            size: 9,
            color: '#AEAEAE'},
          showarrow: false,
        },
        {
          x: .25,
          y: .99,
          xref: 'x',
          yref: 'y',
          text: 'Aggressive/Cathartic',
          font: {
            family: 'Verdana',
            size: 8,
            color: '#AEAEAE'},
          showarrow: false,
        },
        {
          x: .25,
          y: .05,
          xref: 'x',
          yref: 'y',
          text: 'Somber',
          font: {
            family: 'Verdana',
            size: 9,
            color: '#AEAEAE'},
          showarrow: false,
        },
        {
          x: .75,
          y: .05,
          xref: 'x',
          yref: 'y',
          text: 'Chill',
          font: {
            family: 'Verdana',
            size: 9,
            color: '#AEAEAE'},
          showarrow: false,
        },
      ]
      };

        Plotly.newPlot('vibe_chart', vibe_chart_ref, layout_vibe,{displayModeBar: false});
        Plotly.newPlot('track_chart', track_chart_ref, layout_track,{displayModeBar: false});
        Plotly.newPlot('vibe_chart_mobile', vibe_chart_ref, layout_vibe,{displayModeBar: false});
        Plotly.newPlot('track_chart_mobile', track_chart_ref, layout_track,{displayModeBar: false});



        vibe_chart.on('plotly_click', function(data){
          if (data.points.length === 1) {
            var link = song_links[data.points[0].pointNumber];
            
            // Note: window navigation here.
            window.location = link;
          }
        });
        track_chart.on('plotly_click', function(data){
        if (data.points.length === 1) {
          var link = song_links[data.points[0].pointNumber];
          
          // Note: window navigation here.
          window.location = link;
          }
        });
      
});
