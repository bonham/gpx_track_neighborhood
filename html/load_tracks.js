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
import LayerGroup from 'ol/layer/Group';
import GeoJSON from 'ol/format/GeoJSON';
import Map from 'ol/Map';
import View from 'ol/View';
import {fromLonLat} from 'ol/proj';
import Control from 'ol/control/Control';

var colors = ['orange', 'brown', 'red', 'green', 'blue'];
var style = loadStyles(colors);
var map;
var currentLayer = null;
const DEFAULT_ZOOM = 9;

$(document).ready(function() {

  var drawLayers = [ new Tile({ source: new OSM() }) ];

  map = new Map({
    layers: drawLayers,
    target: 'map',
    view: new View({
      center: fromLonLat([8.697, 49.30]),
      zoom: DEFAULT_ZOOM,
    }),
  });
  map.addEventListener('click', hidePopups);
  map.addEventListener('rendercomplete', hideLoading);

  var olc = document.getElementsByClassName('ol-overlaycontainer')[0];
  var loaderControl = new Control({
    element: createLoaderControl(),
    target: olc,
  });
  map.addControl(loaderControl);

  // 'Guide' and 'About' buttons
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
  $(document).on('click', hidePopups);

  // Load list of track sets
  var fpath = 'geojson/datasets.json';
  $.getJSON(fpath, function(data) {

    // prepare buttons for each set (label)
    $.each(data, function(index, value){
      prepareButton(value);
    });

    // load tracks for set
    var startLabel = data[0];
    switchMap(startLabel);
    setActiveButton($('#but_' + startLabel));

  }).fail(function(jqXHR, textStatus, errorThrown) {
    console.log('Failed to load ' + fpath);
    console.log(errorThrown);
  });

  // Ios event bubbling
  $('div.container').css('cursor', 'pointer'); // make ios work

});

function createLoaderControl() {

  var outerLoadingEl = document.createElement('div');
  outerLoadingEl.classList.add('loading-outer');
  var innerLoadingEl = document.createElement('div');
  innerLoadingEl.classList.add('loading-inner');
  var loadingText = document.createTextNode('Loading ...');
  innerLoadingEl.appendChild(loadingText);
  outerLoadingEl.appendChild(innerLoadingEl);
  return outerLoadingEl;

}

function loadLegend(subdir) {
  var fpath = 'geojson/' + subdir + '/legend.json';
  $.getJSON(fpath, function(data) {
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
  }).fail(function(jqXHR, textStatus, errorThrown) {
    console.log('Failed to load ' + fpath);
    console.log(errorThrown);
  });

}
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

function createLayers(vectorSource, num) {

  var vectorLayerList = [];
  for (var i = 0; i < num; i++) {
    vectorLayerList[i] = new VectorLayer({
      source: vectorSource[i],
      style: style[i % style.length],
    });
  }
  var lgroup = new LayerGroup(
    {
      layers: vectorLayerList,
    });
  return lgroup;
};

function provideLayers(year, numTracks) {
  var vSrc = loadSource(year, numTracks);
  return createLayers(vSrc, numTracks);
}

function switchMap(year) {
  if (currentLayer != null) {
    map.removeLayer(currentLayer);
  }

  loadLegend(year);

  var fpath = 'geojson/' + year + '/numberOfTracks.json';
  var jqXHR = $.getJSON(fpath, function(data) {

    showLoading();
    var numTracks = data['numberOfTrackFiles'];
    currentLayer = provideLayers(year, numTracks);
    map.addLayer(currentLayer);

  }).fail(function(jqXHR, textStatus, errorThrown) {
    console.log('Failed to load ' + fpath);
    console.log(errorThrown);
  });
};

function showLoading() {
  $('.loading-outer').css('display', 'block');
}

function hideLoading(event) {
  $('.loading-outer').css('display', 'none');
}

function prepareButton(label){
  var buttonHtml =
    '<li><a id="but_' +
    label +
    '" class="button button-mapselect" href="#">' +
    label +
    '</a></li>';
  $(buttonHtml).insertBefore(
    '#but_guide_listelement'
  );
  $('#but_' + label).click(function(event) {
    switchMap(label);
    setActiveButton($(this));
    event.stopPropagation();
  });
};

function setActiveButton(buttonObject){
  $('.button-mapselect').css('background-color', '#25283d');
  $('.button-mapselect').css('border-color', '#888');
  buttonObject.css('background-color', '#8eb3a2');
  buttonObject.css('border-color', '#8eb3a2');
}

function hidePopups(event) {
  $('#child_1').hide();
  $('#child_2').hide();
};
