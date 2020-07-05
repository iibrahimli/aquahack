function getStartOfNextDay() {
  const tmrw = new Date();
  tmrw.setDate(new Date().getDate() + 1);
  tmrw.setHours(tmrw.getHours() - 1);
  return tmrw;
}

function weatherApiRequest(lat, lon, startTime, endTime, fields) {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: `https://api.climacell.co/v3/weather/forecast/hourly`,
      type: "GET",
      data: {
        lat,
        lon,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        fields,
        apikey: "OreplnqxX96dwGgTpsuYJkNJ0rvy8gEs",
      },
      success: function (data) {
        resolve(data);
      },
      error: function (error) {
        reject(error);
      },
    });
  });
}

function rainInterval(data) {
  return data.reduce((acc, hourData) => {
    if (
      hourData.precipitation > 0 ||
      hourData.precipitation_probability >= 50
    ) {
      const obj = {
        hour: new Date(hourData.observation_time.value).getHours(),
        precipitation: hourData.precipitation,
        precipitation_probability: hourData.precipitation_probability,
      };
      const lastElArr = acc[acc.length - 1];

      if (acc.length && lastElArr[lastElArr.length - 1].hour === obj.hour - 1) {
        acc[acc.length - 1].push(obj);
      } else {
        acc.push([obj]);
      }
    }

    return acc;
  }, []);
}

function prepareGraphData(dataArr, fields) {
  return dataArr.map((data) => fields.map((field) => data[field].value));
}

function columnGraphData(dataArr) {
  const columns = [];
  for (let i = 0; i < dataArr[0].length; i++) {
    columns.push(dataArr.map((row) => row[i]));
  }

  return columns;
}
