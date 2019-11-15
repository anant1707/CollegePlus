 google.charts.load("current", {packages:["corechart"]});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Task', 'Hours per Day'],
          ['Eat',      2],
          ['Work',     11],
          ]);

        var options = {
          title: 'My Daily Activities',
          pieHole: 0.4,
          width:400,
          hegiht:500,
        };

        var chart = new google.visualization.PieChart(document.getElementById('donutchart'));
        chart.draw(data, options);
      }