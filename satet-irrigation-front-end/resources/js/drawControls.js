// Drawing
function drawControls() {
  const drawnItems = new L.FeatureGroup();
  map.addLayer(drawnItems);
  map.on(L.Draw.Event.CREATED, (event) => drawnItems.addLayer(event.layer));

  return new L.Control.Draw({
    edit: {
      featureGroup: drawnItems,
      poly: {
        allowIntersection: false,
      },
    },
    draw: {
      polygon: {
        allowIntersection: false,
        showArea: true,
      },
    },
  });
}

let controls = drawControls();

$("#add-field").on("click", function () {
  const clicked = $(this).data("clicked");
  if ($(this).data("clicked")) {
    $(this).removeClass("button-cancel");
    $(this).html("+ yeni sahə əlavə edin");
    map.removeControl(controls);
  } else {
    $(this).addClass("button-cancel");
    $(this).html("- ləğv et");

    controls.addTo(map);
  }

  $(this).data("clicked", clicked === undefined ? true : !clicked);
});

map.on("draw:created", function (e) {
  $("#add-field").trigger("click");
});
