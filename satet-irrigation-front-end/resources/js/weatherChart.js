function capitalize(string) {
  return string[0].toUpperCase() + string.slice(1);
}

async function getColumnData(apiParams, graphFields) {
  const jsonData = await weatherApiRequest(...apiParams);
  const graphData = prepareGraphData(jsonData, [
    "observation_time",
    ...graphFields.map(({ field }) => field),
  ]);

  return columnGraphData(graphData);
}

async function weatherChart(apiParams, graphFields) {
  const columnData = await getColumnData(apiParams, graphFields);

  const axis = graphFields.map(({ field, name }, index) => ({
    title: capitalize(name === undefined ? field : name),
    titlepos: index === 0 ? "left" : "right",
    axisonleft: index ? 0 : 1,
    dataset: [
      {
        seriesname: capitalize(name === undefined ? field : name),
        linethickness: "3",
        data: columnData[index + 1].map((value) => ({ value })),
      },
    ],
  }));

  new FusionCharts({
    type: "multiaxisline",
    renderAt: "weather-chart",
    width: "100%",
    height: "500",
    dataFormat: "json",
    dataSource: {
      chart: {
        theme: "fusion",
        caption: "Hava",
        subcaption: "Bu gün",
        labelDisplay: "Auto",
        baseFontColor: "#333333",
        baseFont: "Helvetica Neue,Arial",
        xaxisname: "Zaman",
        showvalues: "0",
        xAxisLineThickness: "1",
        xAxisLineColor: "#999999",
        legendBorderAlpha: "0",
        legendShadow: "0",
        alignCaptionWithCanvas: "0",
        drawCrossLine: "1",
      },
      categories: [
        {
          category: columnData[0].map((date) => ({
            label: new Date(date).getHours(),
          })),
        },
      ],
      axis,
    },
  }).render();
}
/*
  [
    38.6652234,
    48.8064696,
    new Date(),
    getStartOfNextDay(),
    ["temp", "humidity", "precipitation"],
  ],
  [
    { field: "temp", name: "temperature", suffix: " C" },
    { field: "humidity", name:"" suffix: "%" },
    { field: "precipitation", suffix: " mm/hr" },
  ]
*/
