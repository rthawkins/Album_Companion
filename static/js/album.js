
$('#submit-button').click(function() {
  $('#submit-button').html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Analyzing...').addClass('disabled');
});

$.getJSON(`/album/${selected_album}`,
    function (data) {
        var tr;
        for (var i = 0; i < data.length; i++) {
            tr = $('<tr/>');
            tr.append("<td> "+ data[i].track+"</td>");
            tr.append("<td> <a href='/"+ data[i].sp_id + "'> " + data[i].title + "</td>");
            $('#album_table').append(tr);
            tr.appendTo("#album_table, #album_table_mobile");
        }

      let tr_summary = $("<tr><td><i>Representative</i></td><td><a href='/" + _.minBy(data, 'uniqueness').sp_id + "'> " +  _.minBy(data, 'uniqueness').title + "</td></tr>"
      +"<tr><td><i>Unique</i></td><td><a href='/" + _.maxBy(data, 'uniqueness').sp_id + "'> " + _.maxBy(data, 'uniqueness').title + "</td></tr>"
      +"<tr><td><i>Energetic</i></td><td><a href='/" + _.maxBy(data, 'energy').sp_id + "'> " + _.maxBy(data, 'energy').title + "</td></tr>"
      +"<tr><td><i>Slow</i></td><td><a href='/" + _.minBy(data, 'energy').sp_id + "'> " + _.minBy(data, 'energy').title + "</td></tr>"
      +"<tr><td><i>Positive</i></td><td><a href='/" + _.maxBy(data, 'mood').sp_id + "'> " + _.maxBy(data, 'mood').title + "</td></tr>"
      +"<tr><td><i>Negative</i></td><td><a href='/" + _.minBy(data, 'mood').sp_id + "'> " + _.minBy(data, 'mood').title + "</td></tr>"
      +"<tr><td><i>Loud</i></td><td><a href='/" + _.maxBy(data, 'loudness').sp_id + "'> " + _.maxBy(data, 'loudness').title + "</td></tr>"
      +"<tr><td><i>Quiet</i></td><td><a href='/" + _.minBy(data, 'loudness').sp_id + "'> " + _.minBy(data, 'loudness').title + "</td></tr>")
      tr_summary.appendTo("#album_highlights_mobile, #album_highlights");
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
        song_links.push(d.sp_id);
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
            ['0.7', '#02c39a'],
            ['0.8', '#00a896'],
            ['0.9', '#028090'],
            ['1.0', '#05668d']],
            size: 8
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
          color: chart_mood, cmin: 0, cmax: 1,
            colorscale: [
              ['0.0', '#a11d33'],
              ['0.1', '#b21e35'],
              ['0.2', '#c71f37'],
              ['0.3', '#f26a8d'],
              ['0.4', '#000000'],
              ['0.5', '#000000'],
              ['0.6', '#000000'],
              ['0.7', '#02c39a'],
              ['0.8', '#00a896'],
              ['0.9', '#028090'],
              ['1.0', '#05668d']],
              size: 8,
              line: {
            color: '#d9a868', width: 2
        }}
      };
    
    var vibe_chart_ref = [vibe_chart_trace,song_highlight_vibe];
    var track_chart_ref = [track_chart_trace, song_highlight_track];

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

        var layout_vibe_mobile = {
          title: 'Album Vibe',
          titlefont: {
                color: 'black',
                size: 14
          },
          showlegend: false,
          xaxis: {
            title: false,
            titlefont: {
                color: 'black',
                size: 10
                },
            showgrid: false,
            zeroline: true,
            linecolor: 'black',
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
            title: 'Mood',
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
            title: 'Energy',
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
            text: 'Aggressive',
            font: {
              family: 'Verdana',
              size: 9,
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
      title: 'Album Track Quadrants',
      titlefont: {
              color: 'black',
              size: 14
      },
      showlegend: false,
      xaxis: {
          title: 'Negative   < - >   Positive',
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
          tickvals: [0,.5,1], 
          range: [0,1],
      },
      yaxis: {
          title: 'Slow   < - >   Energetic',
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
          t: 50
      },
      width: 290,
      height: 290,
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
          text: 'Aggressive',
          font: {
            family: 'Verdana',
            size: 9,
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
        Plotly.newPlot('vibe_chart_mobile', vibe_chart_ref, layout_vibe_mobile,{displayModeBar: false});
        Plotly.newPlot('track_chart_mobile', track_chart_ref, layout_track_mobile,{displayModeBar: false});

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
