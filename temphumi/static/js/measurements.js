function setChartSize(chart, newsize) {
  chart.canvas.parentNode.style.height = (newsize.width >500
   ? newsize.width * 0.5 : 1*newsize.width) + 'px';
}

function chartConfig(xAxisLabel, yAxisLabels) {
  var datasets = [];
  var yAxes = [];
  yAxisLabels.forEach((yAxis) => {
    datasets.push({
      label: yAxis.label,
      yAxisID: yAxis.id,
      backgroundColor: '#000000',
      borderColor: yAxis.color,
      data: [],
      fill: false,
    });
    yAxes.push({
      id: yAxis.id,
      scaleLabel: {
        display: true,
        labelString: yAxis.label,
      },
      position: yAxis.position,
      ticks: { fontColor: yAxis.color },
    });
  });
  return {
    type: 'line',
    data: {
      labels: [],
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onResize: setChartSize,
      tooltips: {
        mode: 'index',
        intersect: false,
      },
      hover: {
        mode: 'nearest',
        intersect: true
      },
      scales: {
        xAxes: [{
          type: 'time',
          unit: 'hour',
          time: {
            displayFormats: {
              'hour': 'M-DD H'
            }
          }
        }],
        yAxes: yAxes
      }
    }
  };
}

/* lines arrays contain Char.js axis attributes. */
var graphs = [
  {gn: 'power',
   lines: [
     {id: 'power',  label: 'Power [W]', color: '#ff0000', position: 'left'},
     {id: 'energy', label: 'Energy [kWh]', color: '#11cc11', position: 'right'},
   ]},
  {gn: 'temp',
   lines: [
     {id: 'temp', label: 'Temperature [deg C]', color: '#ff0000', position: 'left'},
     {id: 'humi', label: 'Humidity [%]', color: '#111177', position: 'right'},
   ]}
];

var configs = {};
var interval = 3600 * 24;
var startTime = 0;
var endTime = 0;

var prevBtn = document.getElementById('prevBtn');
var nextBtn = document.getElementById('nextBtn');
function showRange(tStart, tEnd) {
  startTime = tStart;
  endTime = tEnd;
  fetch('measurements/' + tStart + ',' + tEnd)
  .then(function(response) {
    return response.json();
  })
  .then(function(jsonResponse) {
     var data = {};
     graphs.forEach((graph) => {
       graph.lines.forEach((line) => {data[line.id] = []});
     });
     jsonResponse.data.forEach((d) => {
       var dt = moment(new Date(d.dt * 1000));
       data.temp.push({x: dt, y: d.t});
       data.humi.push({x: dt, y: d.h});
       data.power.push({x: dt, y: d.p});
       data.energy.push({x: dt, y: d.e});
     });
     graphs.forEach((graph) => {
       var datasets = configs[graph.gn].data.datasets;
       for(var i=0; i < graph.lines.length; ++i) {
         datasets[i].data = data[graph.lines[i].id];
       }
       window.charts[graph.gn].update();
     });
     prevBtn.disabled = !jsonResponse.has_prev;
     nextBtn.disabled = !jsonResponse.has_more;
  });
}

function showNow() {
  var t = Math.floor(Date.now() / 1000);
  showRange(t - interval, t);
}

window.onload = function() {
   window.charts= {};
   graphs.forEach((graph) => {
      configs[graph.gn] = chartConfig('Time', graph.lines);
      var ctx = document.getElementById(graph.gn + '_graph').getContext('2d');
      window.charts[graph.gn] = new Chart(ctx, configs[graph.gn]);
      setChartSize(window.charts[graph.gn],
                   window.charts[graph.gn].canvas.parentNode.getBoundingClientRect());
   });
   showNow();
}

document.getElementById('currentBtn').addEventListener('click', showNow);

prevBtn.addEventListener('click', 
  function() { showRange(startTime - interval, endTime - interval); });

nextBtn.addEventListener('click', 
  function() { showRange(startTime + interval, endTime + interval); });
