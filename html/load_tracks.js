$(document).ready(function()	{
    $.getJSON('geojson/legend.json', function(data) { 
        for (var i = 0; i < data.length; i++) {

            min = data[i]["min"];
            max = data[i]["max"];
            if ( min == max ) {
                text = min;
            } else {
                text = min + " - " + max;
            };
            identifier = '#c' + i;
            $(identifier).text(text);
        };

    });
});

var colors = ["orange", "brown", "red", "green", "blue"]
var style = []
var vectorSource = []
var vectorLayer = []
var drawLayers = [ new ol.layer.Tile({ source: new ol.source.OSM() }) ]

for (i=0; i<colors.length; i++) {

    // define styles
    style[i] = new ol.style.Style({ 

        stroke: new ol.style.Stroke({
            color: colors[i],
            width: 2
        })
    }
    );

    // Load geojson
    fname = 'geojson/g_'+i+'.json'
    vectorSource[i] = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        url: fname
    });

    vectorLayer[i] = new ol.layer.Vector({
        source: vectorSource[i],
        style: style[i]
    });

    drawLayers.push(vectorLayer[i]);
}


var map = new ol.Map({
    layers: drawLayers,
    target: 'map',
    controls: ol.control.defaults({
        attributionOptions: {
            collapsible: false
        }
    }),
    view: new ol.View({
        center: ol.proj.fromLonLat([8.697, 49.30]),
        zoom: 12
    })

});

/* use this code if you want to autozoom to a layer
    vl0.getSource().on("change", function(evt) {
        extent = vl0.getSource().getExtent();
        map.getView().fit(extent, map.getSize());
    });
    */


function toggle(target){

    var artz = document.getElementsByClassName('article');

    var isVis, targ;
    if (target == '') {
        isVis == true;
    } else {
        targ = document.getElementById(target);  
        isVis = targ.style.display=='block';
    };

    // hide all
    for(var i=0;i<artz.length;i++){
        artz[i].style.display = 'none';
    }

    if (target == '') { return false; };

    // toggle current
    targ.style.display = isVis?'none':'block';

    return false;
}

