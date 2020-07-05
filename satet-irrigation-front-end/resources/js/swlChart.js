function capitalize(string) {
  return string[0].toUpperCase() + string.slice(1);
}

async function swlData(lat, lon, startTime, endTime, fields) {
  const jsonData = await weatherApiRequest(
    lat,
    lon,
    startTime,
    endTime,
    fields
  );

  Object.defineProperty(Array.prototype, "chunk_inefficient", {
    value: function (chunkSize) {
      var array = this;
      return [].concat.apply(
        [],
        array.map(function (elem, i) {
          return i % chunkSize ? [] : [array.slice(i, i + chunkSize)];
        })
      );
    },
  });

  const preparedData = prepareGraphData(jsonData, [
    "observation_time",
    ...fields,
  ]);
  const chunkedData = preparedData.chunk_inefficient(3);
  const columnChunkedData = chunkedData.map((chunk) => columnGraphData(chunk));

  const etArr = await Promise.all(
    columnChunkedData.map((set) => {
      return new Promise((resolve, reject) => {
        $.ajax({
          headers: { "Access-Control-Allow-Origin": "*" },
          url: "http://35.192.204.11:8001/api/add",
          type: "POST",
          crossDomain: true,
          dataType: "json",
          data: JSON.stringify({
            station_id: "wx8v08a8",
            datetime: set[0][1],
            temp: set[1],
            wind_speed: set[2],
            humidity: set[3],
            precip: set[4],
          }),
          success: function (data) {
            resolve(data);
          },
          error: function (error) {
            reject(error);
          },
        });
      });
    })
  );

  return etArr.map((etData) => etData.et);
}

async function swlChart(apiParams) {
  const chunkedEt = await swlData(...apiParams);
  const [, , startTime, endTime] = apiParams;
  let swl = 210;
  const graphData = [];

  for (
    let time = new Date(startTime), i = 0;
    time.getTime() < endTime.getTime();
    time.setHours(time.getHours() + 1), i++
  ) {
    console.log(time, i);
    graphData.push([time.toISOString(), swl]);
    swl -= chunkedEt[Math.floor(i / 3)];
  }

  const schema = [
    { name: "Date", type: "date", format: "%Y-%m-%dT%H:%M:%S.%LZ" },
    { name: "Nəmlik səviyyəsi", type: "number" },
  ];

  const dataStore = new FusionCharts.DataStore();
  const dataSource = {
    caption: {
      text: "Nəmlik səviyyəsi",
    },
    yaxis: {
      value: "Nəmlik səviyyəsi",
      type: "line",
      format: { suffix: "SWL" },
      referenceZone: [
        {
          label: "Target",
          valueMax: 180,
          valueMin: 120,
          style: {
            marker: {
              fill: "#12deb0",
              stroke: "#03ad87",
            },
            "marker-text": {
              fill: "#000000",
            },
            "marker:hover": {
              fill: "#12deb0",
            },
            "marker-zone:hover": {
              stroke: "#03ad87",
            },
            "marker-notch:hover": {
              stroke: "#03ad87",
            },
          },
        },
      ],
      referenceLine: [
        {
          label: "Optimal səviyyə",
          value: 145,
          style: {
            marker: {
              fill: "#03ad87",
              stroke: "#03ad87",
              "stroke-dasharray": "4 3",
            },
          },
        },
      ],
    },
  };
  dataSource.data = dataStore.createDataTable(graphData, schema);

  new FusionCharts({
    type: "timeseries",
    renderAt: "swl-chart",
    width: "100%",
    height: "500",
    dataSource: dataSource,
  }).render();
}
