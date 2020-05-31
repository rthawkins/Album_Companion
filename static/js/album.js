
$('#submit-button').click(function() {
  $('#submit-button').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Analyzing...').addClass('disabled');
});

$.getJSON(`/album/${selected_album}`,
    function (data) {
        var tr;
        for (var i = 0; i < data.length; i++) {
            tr = $('<tr class="active"/>');
            tr.append("<td> "+ data[i].track+"</td>");
            tr.append("<td> <a href='/"+ data[i].sp_id + "'> " + data[i].title + "</td>");
            $('#album_table').append(tr);
        }
    });

  Plotly.d3.json(`/album/${selected_album}`, function(data){

    // arrays for plotting selected states
    chart_track = [];
    chart_energy = [];
    chart_mood = [];
    chart_unique = [];
    hover_vibe = [];

    // populate arrays differently, controlling for if the user is looking at all states, highlighting a state, or isolating a state
    data.forEach(d => {
        chart_track.push(d.track);
        chart_energy.push(d.energy);
        chart_mood.push(d.mood);
        chart_unique.push(d.uniqueness * 10);
        hover_vibe.push(d.title)});

    var trace1 = {
        x: chart_track,
        y: chart_energy,
        hovertemplate: '%{text}',
        text: hover_vibe,
        marker: {
            color: '#ae68d9',
            size: 6
          },
          line: {
            color: '#ae68d9',
            width: 1
          },
        name: 'Energy',
        mode: 'lines+markers',
        type: 'scatter'
      };

    var trace2 = {
        x: chart_track,
        y: chart_mood,
        hovertemplate: '%{text}',
        text: hover_vibe,
                marker: {
            color: '#d9c468',
            size: 6
          },
          line: {
            color: '#d9c468',
            width: 1
          },
        name: 'Mood',
        mode: 'lines+markers',
        type: 'scatter'
      };

    var trace3 = {
        x: chart_mood,
        y: chart_energy,
        hovertemplate: '',
        text: hover_vibe,
        marker: {
            size: chart_unique
        },
        name: 'Album Tracks',
        mode: 'markers',
        type: 'scatter'
      };

    var song_highlight_track = {
        x: [s_mood],
        y: [s_energy],
        hovertemplate: '',
        text: hover_vibe[s_tracknum-1],
        name: 'This Song',
        mode: 'markers',
        type: 'scatter',
        marker: {color: '#d9a868',
        size: chart_unique[s_tracknum-1], line: {
            color: 'black', width: 2
        }}
      };

    var song_highlight_mood = {
        x: [s_tracknum],
        y: [s_mood],
        hovertemplate: 'This Song',
        text: hover_vibe[s_tracknum-1],
        name: 'Mood',
        mode: 'markers',
        type: 'scatter',
        marker: {color: '#d9a868',size: 7, line: {
            color: 'black', width: 2
        }}
      };

    var song_highlight_energy = {
        x: [s_tracknum],
        y: [s_energy],
        hovertemplate: 'This Song',
        text: hover_vibe[s_tracknum-1],
        name: 'Energy',
        mode: 'markers',
        type: 'scatter',
        marker: {color: '#d9a868',size: 7, line: {
            color: 'black', width: 2
        }}
      };
    
    var vibe_chart = [trace1,trace2,song_highlight_mood,song_highlight_energy];
    var track_chart = [trace3, song_highlight_track];

    var layout_vibe = {
                  title: 'Album Vibe',
                  titlefont: {
                        color: '#f2f0f0',
                        size: 14
                  },
                  showlegend: false,
                  xaxis: {
                    title: false,
                    titlefont: {
                        color: '#f2f0f0',
                        size: 10
                        },
                    showgrid: false,
                    zeroline: true,
                    linecolor: 'white',
                    ticks: 'outside',
                    tickfont: {color: '#f2f0f0',
                    size: 10
                }
                  },
                  yaxis: {
                    linecolor: 'white',
                    gridwidth: 2,
                    gridcolor: '#E1E1E1',
                    tickvals: [0,.5,1], 
                    range: [0,1],
                    tickfont: {color: '#f2f0f0',
                    size: 10
                },
                  },
                  margin: {
                    l: 50,
                    r: 50,
                    b: 50,
                    t: 50
                  },
                  width: 290,
                  height: 290,
                  paper_bgcolor: 'rgba(0, 0, 0,0)',
                  plot_bgcolor: 'rgba(0, 0, 0,0)',
                  hovermode: 'closest'
                };

    var layout_track = {
        title: 'Album Track Quadrants',
        titlefont: {
                color: '#f2f0f0',
                size: 14
        },
        showlegend: false,
        xaxis: {
            title: 'Negative   < - >   Positive',
            titlefont: {
                color: '#f2f0f0',
                size: 11
                },
            showgrid: true,
            zeroline: true,
            linecolor: 'white',
            ticks: 'outside',
            tickfont: {color: '#f2f0f0',
                    size: 10
                },
            tickvals: [0,.5,1], 
            range: [0,1],
        },
        yaxis: {
            title: 'Slow   < - >   Energetic',
            titlefont: {
                color: '#f2f0f0',
                size: 11
                },
            linecolor: 'white',
            gridwidth: 2,
            gridcolor: '#E1E1E1',
            tickvals: [0,.5,1], 
            range: [0,1],
            tickfont: {color: '#f2f0f0',
            size: 10
        },
        },
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50
        },
        width: 290,
        height: 290,
        paper_bgcolor: 'rgba(0, 0, 0,0)',
        plot_bgcolor: 'rgba(0, 0, 0,0)',
        hovermode: 'closest'
        };

        Plotly.newPlot('vibe_chart', vibe_chart, layout_vibe,{displayModeBar: false});
        Plotly.newPlot('track_chart', track_chart, layout_track,{displayModeBar: false});

});