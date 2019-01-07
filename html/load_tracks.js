/* Eslint directives following: */
/* global document */
var jquery = require('jquery');
var $ = jquery;
import 'ol/ol.css';
import Tile from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Map from 'ol/Map';
import View from 'ol/View';
import {fromLonLat} from 'ol/proj';

const numTracks = 5;
const startYear = '2018';
var colors = ['orange', 'brown', 'red', 'green', 'blue'];

$(document).ready(function()	{
  $.getJSON('geojson/legend.json', function(data) {
    for (var i = 0; i < data.length; i++) {

      var min = data[i]['min'];
      var max = data[i]['max'];
      var text;
      if (min === max) {
        text = min;
      } else {
        text = min + ' - ' + max;
      };
      var identifier = '#c' + i;
      $(identifier).text(text);
    };
  });

  var style = loadStyles(colors);
  var drawLayers = [ new Tile({ source: new OSM() }) ];
  var vectorSources = loadSource(startYear, numTracks);
  var vectorLayers = createLayers(vectorSources, style, numTracks);

  for (var i = 0; i < vectorLayers.length; i++) {
    drawLayers.push(vectorLayers[i]);
  }

  var map = new Map({
    layers: drawLayers,
    target: 'map',
    view: new View({
      center: fromLonLat([8.697, 49.30]),
      zoom: 12,
    }),
  });
  map.addEventListener('click', hidePopups);
});

function loadStyles(colors) {

  var style = [];
  for (var i = 0; i < colors.length; i++) {

    // define styles

    style[i] = new Style({
      stroke: new Stroke({
        color: colors[i],
        width: 2,
      }),
    });
  }
  return style;
};

function loadSource(year, num) {

  var vectorSource = [];
  for (var i = 0; i < num; i++) {

    // Load geojson
    var fname = 'geojson/' + year + '/' + 'g_' + i + '.json';
    vectorSource[i] = new VectorSource({
      format: new GeoJSON(),
      url: fname,
    });

  };
  return vectorSource;
};

function createLayers(vectorSource, style, num) {

  var vectorLayer = [];
  for (var i = 0; i < num; i++) {
    vectorLayer[i] = new VectorLayer({
      source: vectorSource[i],
      style: style[i],
    });
  }
  return vectorLayer;
};


/* use this code if you want to autozoom to a layer
    vl0.getSource().on('change', function(evt) {
        extent = vl0.getSource().getExtent();
        map.getView().fit(extent, map.getSize());
    });
    */

$('#but_guide').click(function(event) {
  $('#child_1').toggle();
  $('#child_2').hide();
  event.stopPropagation();
});
$('#but_solution').click(function(event) {
  $('#child_2').toggle();
  $('#child_1').hide();
  event.stopPropagation();
});

function hidePopups(event) {
  $('#child_1').hide();
  $('#child_2').hide();
  console.log(event);
};
$('div.container').css('cursor', 'pointer');
$(document).on('click', hidePopups);
