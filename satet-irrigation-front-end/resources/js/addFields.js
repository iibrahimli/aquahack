const fieldsGeoJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        "ad": "Cay #1",
        "sahə": "0.03 hektar",
        "torpaq növü": "Gilli torpaq",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [48.807213306427, 38.665893276003885],
            [48.80577564239501, 38.66461994524073],
            [48.806869983673096, 38.66400002601615],
            [48.80847930908203, 38.66540740246324],
            [48.807213306427, 38.665893276003885],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        "ad": "Cay #3",
        "sahə": "0.042 hektar",
        "torpaq növü": "Gilli torpaq",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [48.8057541847229, 38.66451941816347],
            [48.80307197570801, 38.66244182697065],
            [48.803608417510986, 38.661168434833804],
            [48.80678415298462, 38.66394976206004],
            [48.8057541847229, 38.66451941816347],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        "ad": "Cay #2",
        "sahə": "0.033 hektar",
        "torpaq növü": "Gilli torpaq",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [48.80734205245972, 38.66596029278524],
            [48.80856513977051, 38.66552468258525],
            [48.809874057769775, 38.666797997259884],
            [48.808887004852295, 38.667300615240414],
            [48.80734205245972, 38.66596029278524],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        "ad": "Limon #1",
        "sahə": "0.06 hektar",
        "torpaq növü": "Gilli torpaq",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [48.80852222442627, 38.66534038516442],
            [48.80378007888794, 38.66120194544327],
            [48.80433797836304, 38.660615507513604],
            [48.8093376159668, 38.66430160901197],
            [48.80852222442627, 38.66534038516442],
          ],
        ],
      },
    },
  ],
};

function capitalize(string) {
  return string[0].toUpperCase() + string.slice(1);
}

function popup(info) {
  return `<div class="field-popup">\
            <ul>${Object.entries(info)
      .map(
        ([key, value]) =>
          `<li>\
                    <span class="popup-prop-label">${capitalize(
            key
          )}:</span> ${value}\
                </li>`
      )
      .join("")}\
            </ul>\
        </div>`;
}

L.geoJSON(fieldsGeoJSON, {
  onEachFeature: (feature, layer) => {
    // Labels on entities
    L.marker(layer.getBounds().getCenter(), {
      icon: L.divIcon({
        className: "map-label",
        html: feature.properties.ad,
        iconSize: [80, 20],
      }),
    }).addTo(map);

    // Html .fields-cp <li>'s
    $(".fields-cp").prepend(
      `<li class="fields-cp-field">${feature.properties.ad}</li>`
    );

    // Popup
    layer.bindPopup(popup(feature.properties));
  },
}).addTo(map);
