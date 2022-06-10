
require(["esri/config","esri/Map", "esri/views/MapView", "esri/views/SceneView", "esri/widgets/Home", "esri/layers/MapImageLayer", "esri/layers/WMSLayer", 
    "esri/portal/Portal", "esri/portal/PortalItem", "esri/widgets/Expand", "esri/widgets/Slice", "esri/analysis/SlicePlane", "esri/widgets/Legend",
    "esri/widgets/TimeSlider", "esri/layers/FeatureLayer", "esri/renderers/SimpleRenderer", "esri/layers/SceneLayer", "esri/symbols/PictureMarkerSymbol",
    "esri/symbols/PointSymbol3D", "esri/smartMapping/renderers/location", "esri/widgets/BasemapGallery", "esri/core/Error", "esri/widgets/ElevationProfile",
    "esri/widgets/Search", "esri/renderers/ClassBreaksRenderer", "esri/core/watchUtils", "esri/geometry/Point", "esri/request", "esri/intl"], 
    function (esriConfig,Map, MapView, SceneView, Home, MapImageLayer, WMSLayer, Portal, PortalItem, Expand, Slice, SlicePlane, Legend, TimeSlider, FeatureLayer,
              SimpleRenderer, SceneLayer, PictureMarkerSymbol, PointSymbol3D, locationRendererCreator, BasemapGallery, Error, ElevationProfile, Search,
              ClassBreaksRenderer, watchUtils, Point, esriRequest, intl) {
    
    // Set API Key
    esriConfig.apiKey = "AAPKd15383d1b7c74b25ab3b099ebf3eb05fHSycCRGH9iBCVlUpWNazVJzMB5HEd5Ljkl1UK-2r-zpgFl2Bjss8xmhl4ATA0AbC";
    
    intl.setLocale("en-GB");  // Change to English

    // Connect to the ArcGIS Online Portal
    var portal = new Portal("https://zhaw.maps.arcgis.com");
    
    //console.log("Layer IDs: ", LayerIDs)

    // Assign some Buttons and HTML Elements to variables 
    const switchButton = document.getElementById("switch-btn"); // Button to Switch between 2D and 3D view
    const heightSelectButton = document.getElementById("waypointHeightSubmit");
    const addFlightPathButton = document.getElementById("AddPath")
    const delFlightPathButton = document.getElementById("DeletePath")
    const LayerViewFilterDistanceSlider = document.getElementById("FilterDistanceSlider")
    const WarningDiv = document.getElementById("WarningDiv")
    const DateDiv = document.getElementById("DateDiv")

    // Configuring app for creating Views later
    const appConfig = {
      mapView: null,
      sceneView: null,
      activeView: null,
      container: "viewDiv" // use same container for views
    };

    var initialViewParams2D = {
      zoom: 8,
      center: [8.231819, 46.798466],
      container: appConfig.container,
      viewingMode: "local",
    };

    var initialViewParams3D = {
      zoom: 8,
      center: [8.231819, 46.798466],
      container: appConfig.container,
      viewingMode: "local",
    };


    // Add Layers and Defining Symbols and Renderers for different Layers

    let empty_layer_id = "0e7c2ea4b7bb400da412366ec33d01be"   // Layer ID of empty Point Scene Layer
    let Empty_SceneLayer = new SceneLayer({
      title: `Cloud Cover Layer`,
      portalItem: {
        id: empty_layer_id
      },
      id: "Empty Scene Layer",
    });

    const CloudSymbol2 = {
      type: "point-3d",  // autocasts as new ObjectSymbol3DLayer()
      symbolLayers: [{
        type: "object",
        width: 1120,    // diameter of the object from east to west in meters 1120
        height: 400,  // height of object in meters 455
        depth: 1620,   // diameter of the object from north to south in meters 1620
        resource: { href: "http://localhost:8000/3D_symbols/Cloud/cumulus_cloud.glb"}
      }]
    };
    
    /*
    const CloudSymbol2 = {
      type: "picture-marker",  
      url: "https://zhaw.maps.arcgis.com/sharing/rest/content/items/a00c73edffb8496b80f64208b8832897/data",
      width: "100px",
      height: "100px"
    };*/
    
    let CloudRenderer2 = new SimpleRenderer({
      symbol: CloudSymbol2,
      visualVariables: [
        {
          type: "color",
          field: "CloudClassification", 
          stops: [{ value: 0, color: "white" , label: "0 Oktas"}, { value: 8, color: "#525252" , label: "8 Oktas"}]
        },
        {
          type: "opacity",
          field: "CloudClassification", 
          stops: [{ value: 0, opacity: 0.0 , label: "0 Oktas"}, { value: 1, opacity: 0.4 , label: "1 Oktas"}, { value: 8, opacity: .8 , label: "8 Oktas"}]
        }
      ]
    })
    

    let CloudRenderer = new ClassBreaksRenderer({
      //type: "class-breaks",
      field: "CloudClassification",
      classBreakInfos: [
        // 5 knots
        {minValue: 0.0,  maxValue: 0.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 138, height: 300, depth: 200, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/cloud2.glb"}}]}}, 
        {minValue: 1.0,  maxValue: 1.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 138, height: 300, depth: 200, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/one_eighth.glb"}}]}}, 
        {minValue: 2.0,  maxValue: 2.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 276, height: 300, depth: 400, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/two_eighth.glb"}}]}}, 
        {minValue: 3.0,  maxValue: 3.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 414, height: 300, depth: 600, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/three_eighth.glb"}}]}}, 
        {minValue: 4.0,  maxValue: 4.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 552, height: 300, depth: 800, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/four_eighth.glb"}}]}}, 
        {minValue: 5.0,  maxValue: 5.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 690, height: 300, depth: 1000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/five_eighth.glb"}}]}}, 
        {minValue: 6.0,  maxValue: 6.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 827, height: 300, depth: 1200, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/six_eighth.glb"}}]}}, 
        {minValue: 7.0,  maxValue: 7.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 965, height: 300, depth: 1400, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/seven_eighth.glb"}}]}}, 
        {minValue: 8.0,  maxValue: 8.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 1250, height: 300, depth: 1700, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Cloud/eight_eighth.glb"}}]}}
      ],
      //label: "Cloud Coverage in Oktas",
      //title: " Clouds",
      visualVariables: [
        {
          type: "color",
          field: "CloudClassification", 
          stops: [{ value: 0, color: "white" , label: "0 Oktas"}, { value: 8, color: "#525252" , label: "8 Oktas"}]
        },
        {
          type: "opacity",
          field: "CloudClassification", 
          stops: [{ value: 0, opacity: 0.0 , label: "0 Oktas"}, { value: 1, opacity: 0.4 , label: "1 Oktas"}, { value: 8, opacity: .8 , label: "8 Oktas"}]
        }
      ]
    });
    

    let CloudLayer05UTC = new SceneLayer({
      //title: `Cloud Cover Layer ${time}`,
      title: `Cloud Cover Layer`,
      portalItem: {
        ... ("Clouds_05UTC" in LayerIDs ? {id: LayerIDs["Clouds_05UTC"]} : {id: empty_layer_id}),
        //id: "50665dbb301c4dfa81e1a525cd6de7f5", // 05UTC Clouds Layer
      },
      renderer: CloudRenderer2,
      id: "CLC",
    });
    CloudLayer05UTC.outFields=["*"];  // Used for Time Queries with the timeSlider

    let CloudLayer08UTC = new SceneLayer({
      //title: `Cloud Cover Layer ${time}`,
      title: `Cloud Cover Layer`,
      portalItem: {
        //id: "311e12381a5a46a3803fe84ca9a6785a",   // 08UTC Clouds Layer 
        ... ("Clouds_08UTC" in LayerIDs ? {id: LayerIDs["Clouds_08UTC"]} : {id: empty_layer_id}),
      },
      renderer: CloudRenderer2,
      id: "CLC",
    });
    CloudLayer08UTC.outFields=["*"];  // Used for Time Queries with the timeSlider

    let CloudLayer11UTC = new SceneLayer({
      //title: `Cloud Cover Layer ${time}`,
      title: `Cloud Cover Layer`,
      portalItem: {
        //id: "81c91ca0ed694df39b16a72b96dd4bb9",   // 11UTC Clouds Layer 
        ... ("Clouds_11UTC" in LayerIDs ? {id: LayerIDs["Clouds_11UTC"]} : {id: empty_layer_id}),
      },
      renderer: CloudRenderer2,
      id: "CLC",
    });
    CloudLayer11UTC.outFields=["*"];  // Used for Time Queries with the timeSlider

    let CloudLayer14UTC = new SceneLayer({
      //title: `Cloud Cover Layer ${time}`,
      title: `Cloud Cover Layer`,
      portalItem: {
        //id: "d252a1b68ea7486f94c687b8ddc79cce",   // 14UTC Clouds Layer
        ... ("Clouds_14UTC" in LayerIDs ? {id: LayerIDs["Clouds_14UTC"]} : {id: empty_layer_id}), 
      },
      renderer: CloudRenderer2,
      id: "CLC",
    });
    CloudLayer14UTC.outFields=["*"];  // Used for Time Queries with the timeSlider

    let CloudLayer17UTC = new SceneLayer({
      //title: `Cloud Cover Layer ${time}`,
      title: `Cloud Cover Layer`,
      portalItem: {
        //id: "8cdf34a2c4ea42beb81f2fa63a80283c",   // 17UTC Clouds Layer
        ... ("Clouds_17UTC" in LayerIDs ? {id: LayerIDs["Clouds_17UTC"]} : {id: empty_layer_id}), 
      },
      renderer: CloudRenderer2,
      id: "CLC",
    });
    CloudLayer17UTC.outFields=["*"];  // Used for Time Queries with the timeSlider



    let HorizontalWindRenderer = new ClassBreaksRenderer({
      //type: "class-breaks",
      // attribute of interest - Earthquake magnitude
      field: "WindItem",
      classBreakInfos: [
        // 5 knots
        {minValue: 0.0,  maxValue: 0.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,      resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 1.0,  maxValue: 1.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,     resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 2.0,  maxValue: 2.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,     resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 3.0,  maxValue: 3.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 4.0,  maxValue: 4.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 5.0,  maxValue: 5.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 6.0,  maxValue: 6.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 7.0,  maxValue: 7.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_05knots.glb" },material: {color: "black"}}]}},

        // 10 knots
        {minValue: 8.0,  maxValue: 8.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,      resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 9.0,  maxValue: 9.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,     resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}},
        {minValue: 10.0,  maxValue: 10.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 11.0,  maxValue: 11.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 12.0,  maxValue: 12.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 13.0,  maxValue: 13.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 14.0,  maxValue: 14.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 15.0,  maxValue: 15.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_10knots.glb" },material: {color: "black"}}]}}, 

        // 20 knots
        {minValue: 16.0,  maxValue: 16.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 17.0,  maxValue: 17.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 18.0,  maxValue: 18.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 19.0,  maxValue: 19.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 20.0,  maxValue: 20.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 21.0,  maxValue: 21.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}},
        {minValue: 22.0,  maxValue: 22.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 23.0,  maxValue: 23.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_20knots.glb" },material: {color: "black"}}]}}, 

        // 30 knots
        {minValue: 24.0,  maxValue: 24.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 25.0,  maxValue: 25.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 26.0,  maxValue: 26.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 27.0,  maxValue: 27.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 28.0,  maxValue: 28.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 29.0,  maxValue: 29.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 30.0,  maxValue: 30.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 31.0,  maxValue: 31.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_30knots.glb" },material: {color: "black"}}]}}, 

        // 40 knots
        {minValue: 32.0,  maxValue: 32.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}},
        {minValue: 33.0,  maxValue: 33.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 34.0,  maxValue: 34.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 35.0,  maxValue: 35.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 36.0,  maxValue: 36.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 37.0,  maxValue: 37.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 38.0,  maxValue: 38.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 39.0,  maxValue: 39.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_40knots.glb" },material: {color: "black"}}]}}, 

        // 50 knots
        {minValue: 40.0,  maxValue: 40.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 41.0,  maxValue: 41.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 42.0,  maxValue: 42.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 43.0,  maxValue: 43.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}},
        {minValue: 44.0,  maxValue: 44.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 45.0,  maxValue: 45.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 46.0,  maxValue: 46.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 47.0,  maxValue: 47.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_50knots.glb" },material: {color: "black"}}]}}, 

        // 60 knots
        {minValue: 48.0,  maxValue: 48.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 49.0,  maxValue: 49.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 50.0,  maxValue: 50.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 51.0,  maxValue: 51.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 52.0,  maxValue: 52.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 53.0,  maxValue: 53.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 54.0,  maxValue: 54.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}},
        {minValue: 55.0,  maxValue: 55.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_60knots.glb" },material: {color: "black"}}]}}, 

        // 70 knots
        {minValue: 56.0,  maxValue: 56.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 57.0,  maxValue: 57.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 58.0,  maxValue: 58.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 59.0,  maxValue: 59.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 60.0,  maxValue: 60.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 61.0,  maxValue: 61.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 62.0,  maxValue: 62.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 63.0,  maxValue: 63.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_70knots.glb" },material: {color: "black"}}]}}, 

        // 80 knots
        {minValue: 64.0,  maxValue: 64.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 65.0,  maxValue: 65.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}},
        {minValue: 66.0,  maxValue: 66.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 67.0,  maxValue: 67.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 68.0,  maxValue: 68.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 69.0,  maxValue: 69.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 70.0,  maxValue: 70.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 71.0,  maxValue: 71.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_80knots.glb" },material: {color: "black"}}]}}, 

        // 90 knots
        {minValue: 72.0,  maxValue: 72.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 73.0,  maxValue: 73.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 74.0,  maxValue: 74.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 75.0,  maxValue: 75.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 76.0,  maxValue: 76.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}},
        {minValue: 77.0,  maxValue: 77.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 78.0,  maxValue: 78.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 79.0,  maxValue: 79.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_90knots.glb" },material: {color: "black"}}]}}, 

        // 100 knots
        {minValue: 80.0,  maxValue: 80.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 0,    resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 81.0,  maxValue: 81.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 45,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 82.0,  maxValue: 82.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 90,   resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 83.0,  maxValue: 83.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 135,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 84.0,  maxValue: 84.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 180,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 85.0,  maxValue: 85.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 225,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 86.0,  maxValue: 86.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 270,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_100knots.glb" },material: {color: "black"}}]}}, 
        {minValue: 87.0,  maxValue: 87.9, symbol: {type: "point-3d", symbolLayers: [{type: "object",width: 300, height: 150, depth: 2000, heading: 315,  resource: { href: "http://localhost:8000/3D_symbols/Wind_Barbs_Objects/barb_1000knots.glb" },material: {color: "black"}}]}},
      ],
      visualVariables: [
        {
          type: "color",
          field: "Windspeed", 
          // Color Ramp: 
          stops: [{ value: 0, color: "#ffe3aa" , label: ""}, { value: 25, color: "#ffc655" , label: ""}, { value: 50, color: "#ff7100" , label: ""},
          { value: 75, color: "#ff0000" , label: ""}, { value: 100, color: "#801164" , label: ""}]
        },
      ],
    });
    let HorizontalWindLayerPopup = {
      title: HorizontalWindPopup(),
      outFields: ["*"],
      content: [
        {
          type: "fields",
          fieldInfos: [
            {
              fieldName: "Windspeed",
              label: "Windspeed [kts] ",
              format: {
                places:2
              }
            },
            {
              fieldName: "WindDirection",
              label: "Wind Direction"
            },
            {
              fieldName: "LayerLevel",
              label: "Layer Level"
            },
          ]
        }
      ]
    };
    function HorizontalWindPopup(feature){ 
      return "Latitude: {latitude},\nLongitude: {longitude},\nHeight: {Z}"; 
    }

    let HorizontalWindLayer05UTC = new SceneLayer({
      title: `Horizontal Wind Layer`,
      portalItem: {
        //id: "77bc61fcda5c4e288c5b937d721f2ff3",
        ... ("HorizontalWind_05UTC" in LayerIDs ? {id: LayerIDs["HorizontalWind_05UTC"]} : {id: empty_layer_id}),
      },
      renderer: HorizontalWindRenderer,
      id: "HorizontalWind",
      legendEnabled: false,
      popupTemplate: HorizontalWindLayerPopup,
    });

    let HorizontalWindLayer08UTC = new SceneLayer({
      title: `Horizontal Wind Layer`,
      portalItem: {
        //id: "17e64db2d8914680b1c9179a27e9b9da",
        ... ("HorizontalWind_08UTC" in LayerIDs ? {id: LayerIDs["HorizontalWind_08UTC"]} : {id: empty_layer_id}),        
      },
      renderer: HorizontalWindRenderer,
      id: "HorizontalWind",
      legendEnabled: false,
      popupTemplate: HorizontalWindLayerPopup,
    });

    let HorizontalWindLayer11UTC = new SceneLayer({
      title: `Horizontal Wind Layer`,
      portalItem: {
        //id: "d6e8f2d07a8f489a9de38708389d7cfb",
        ... ("HorizontalWind_11UTC" in LayerIDs ? {id: LayerIDs["HorizontalWind_11UTC"]} : {id: empty_layer_id}),        
      },
      renderer: HorizontalWindRenderer,
      id: "HorizontalWind",
      legendEnabled: false,
      popupTemplate: HorizontalWindLayerPopup,
    });

    let HorizontalWindLayer14UTC = new SceneLayer({
      title: `Horizontal Wind Layer`,
      portalItem: {
        //id: "d478f2cce3c5453cad581dd07490c6b0",
        ... ("HorizontalWind_14UTC" in LayerIDs ? {id: LayerIDs["HorizontalWind_14UTC"]} : {id: empty_layer_id}),        
      },
      renderer: HorizontalWindRenderer,
      id: "HorizontalWind",
      legendEnabled: false,
      popupTemplate: HorizontalWindLayerPopup,
    });

    let HorizontalWindLayer17UTC = new SceneLayer({
      title: `Horizontal Wind Layer`,
      portalItem: {
        //id: "52c3a1d5538d4ec4a8d3316c9a9ee3fa",
        ... ("HorizontalWind_17UTC" in LayerIDs ? {id: LayerIDs["HorizontalWind_17UTC"]} : {id: empty_layer_id}),        
      },
      renderer: HorizontalWindRenderer,
      id: "HorizontalWind",
      legendEnabled: false,
      popupTemplate: HorizontalWindLayerPopup,
    });
    


    let VerticalWindRenderer = new SimpleRenderer({
      symbol: {
        type: "point-3d",
        symbolLayers: [{
          type: "object",
          width: 1120,    // diameter of the object from east to west in meters 1120
          height: 10,     // height of object in meters 455
          depth: 1620,    // diameter of the object from north to south in meters 1620
          resource: { primitive: "cube" },
          opacity: 0.05,
        }],
      },
      visualVariables: [
        {
          type: "color",
          field: "W", 
          // Color Ramp: Blue and Red Extremes 1
          stops: [{ value: -6.0, color: "#10305e" , label: "< -6.0 m/s"}, { value: -3, color: "#10305e" , label: ""}, { value: 0, color: "#ffffff" , label: "0 m/s"},
          { value: 3, color: "#a53217" , label: ""}, { value: 6.0, color: "#a53217" , label: "> 6.0 m/s"}]
        },
      ],
      opacity: .1,
    });
    

    let VerticalWindLayer05UTC = new SceneLayer({
      title: `Vertical Wind Layer`,
      portalItem: {
        //id: "38460bc5b9d04b1a9af1b2f775f6ddf6", 
        ... ("VerticalWind_05UTC" in LayerIDs ? {id: LayerIDs["VerticalWind_05UTC"]} : {id: empty_layer_id}),
      },
      renderer: VerticalWindRenderer,
      id: "VerticalWind",
    });

    let VerticalWindLayer08UTC = new SceneLayer({
      title: `Vertical Wind Layer`,
      portalItem: {
        //id: "b34c1f22d14d4d51bb6325dd00639558",
        ... ("VerticalWind_08UTC" in LayerIDs ? {id: LayerIDs["VerticalWind_08UTC"]} : {id: empty_layer_id}),
      },
      renderer: VerticalWindRenderer,
      id: "VerticalWind",
    });

    let VerticalWindLayer11UTC = new SceneLayer({
      title: `Vertical Wind Layer`,
      portalItem: {
        //id: "c058655dfbaa49f5af6e06a986766aac", 
        ... ("VerticalWind_11UTC" in LayerIDs ? {id: LayerIDs["VerticalWind_11UTC"]} : {id: empty_layer_id}),
      },
      renderer: VerticalWindRenderer,
      id: "VerticalWind",
    });

    let VerticalWindLayer14UTC = new SceneLayer({
      title: `Vertical Wind Layer`,
      portalItem: {
        //id: "0956e341ddf7491c9c386a691704d0aa", 
        ... ("VerticalWind_14UTC" in LayerIDs ? {id: LayerIDs["VerticalWind_14UTC"]} : {id: empty_layer_id}),
      },
      renderer: VerticalWindRenderer,
      id: "VerticalWind",
    });

    let VerticalWindLayer17UTC = new SceneLayer({
      title: `Vertical Wind Layer`,
      portalItem: {
        //id: "16fa4b7caf2f4076a047f6f44cd8af3e",
        ... ("VerticalWind_17UTC" in LayerIDs ? {id: LayerIDs["VerticalWind_17UTC"]} : {id: empty_layer_id}),
      },
      renderer: VerticalWindRenderer,
      id: "VerticalWind",
    });



    let ThunderstormRenderer = new ClassBreaksRenderer({
      field: "StormClassification",
      classBreakInfos: [
        {
          minValue: 1.0,  // 
          maxValue: 1.9,  // 
          symbol: {
            type: "point-3d",
            symbolLayers: [{
              type: "object",
              width: 1120,    // diameter of the object from east to west in meters 1120
              height: 320,  // height of object in meters 322
              depth: 1620,   // diameter of the object from north to south in meters 1620
              resource: { primitive: "cube" }, material: {color: "rgba(222, 179, 62, 0.25)"},/*{ color: "#deb33e" },*/
              opacity: 0.2,
            }],
          },
          label: "Moderate 500-1000 [J/kg]"
        },{
          minValue: 2.0,  // 
          maxValue: 2.9,  // 
          symbol: {
            type: "point-3d",
            symbolLayers: [{
              type: "object",
              width: 1120,    // diameter of the object from east to west in meters 1120
              height: 320,  // height of object in meters 322
              depth: 1620,   // diameter of the object from north to south in meters 1620
              resource: { primitive: "cube" }, material: {color: "rgba(227, 144, 20, 0.55)"},/*{ color: "#e39014" },*/
              opacity: 0.2,
            }],
          },
          label: "Strong 1000-2000 [J/kg]"
        },{
          minValue: 3.0,  // 
          maxValue: 3.9,  // 
          symbol: {
            type: "point-3d",
            symbolLayers: [{
              type: "object",
              width: 1120,    // diameter of the object from east to west in meters 1120
              height: 320,  // height of object in meters 322
              depth: 1620,   // diameter of the object from north to south in meters 1620
              resource: { primitive: "cube" }, material: {color: "rgba(227, 96, 20, 0.65)"},/*{ color: "#e36014" },*/
              opacity: 0.2,
            }],
          },
          label: "Very Strong 2000-3000 [J/kg]"
        },{
          minValue: 4.0,  // 
          maxValue: 4.9,  // 
          symbol: {
            type: "point-3d",
            symbolLayers: [{
              type: "object",
              width: 1120,    // diameter of the object from east to west in meters 1120
              height: 320,  // height of object in meters 322
              depth: 1620,   // diameter of the object from north to south in meters 1620
              resource: { primitive: "cube" }, material: {color: "rgba(245, 66, 149, 0.85)"},/*{ color: "#e31414" },*/
              opacity: 0.2,
            }],
          },
          label: "Extreme \t 3000+ [J/kg]"
        },
      ],
      
      /*visualVariables: [
        {
          type: "color",
          field: "StormClassification", 
          // Color Ramp: Red and Gray 3
          stops: [{ value: 0, color: "#ffffff" , label: "Weak"}, { value: 1, color: "#deb33e" , label: "Moderate"}, { value: 2, color: "#e39014" , label: "Strong"},
          { value: 3, color: "#e36014" , label: "Very Strong"}, { value: 4, color: "#e31414" , label: "Extreme"}]
        },
      ]*/
    });

    let ThunderstormLayer05UTC = new SceneLayer({
      title: `Thunderstorm Layer`,
      portalItem: {
        //id: "aa82d05f6ae54138be9f508983ce3561",      // 09 UTC  
        ... ("Thunderstorm_05UTC" in LayerIDs ? {id: LayerIDs["Thunderstorm_05UTC"]} : {id: empty_layer_id}),
      },
      renderer: ThunderstormRenderer,
      id: "Thunderstorm",
    });

    let ThunderstormLayer08UTC = new SceneLayer({
      title: `Thunderstorm Layer`,
      portalItem: {
        //id: "db5b8d7e042c446fa709be4b9d0eae27",   // 11 UTC     
        ... ("Thunderstorm_08UTC" in LayerIDs ? {id: LayerIDs["Thunderstorm_08UTC"]} : {id: empty_layer_id}),
      },
      renderer: ThunderstormRenderer,
      id: "Thunderstorm",
    });

    let ThunderstormLayer11UTC = new SceneLayer({
      title: `Thunderstorm Layer`,
      portalItem: {
        //id: "8c4bd22c4e054bf5a8b25962bb2ac53a",    // 15 UTC    
        ... ("Thunderstorm_11UTC" in LayerIDs ? {id: LayerIDs["Thunderstorm_11UTC"]} : {id: empty_layer_id}),
      },
      renderer: ThunderstormRenderer,
      id: "Thunderstorm",
    });

    let ThunderstormLayer14UTC = new SceneLayer({
      title: `Thunderstorm Layer`,
      portalItem: {
        //id: "391ada5f41dc45768180f90e6f981175",    // 17 UTC  
        ... ("Thunderstorm_14UTC" in LayerIDs ? {id: LayerIDs["Thunderstorm_14UTC"]} : {id: empty_layer_id}),
      },
      renderer: ThunderstormRenderer,
      id: "Thunderstorm",
    });

    let ThunderstormLayer17UTC = new SceneLayer({
      title: `Thunderstorm Layer`,
      portalItem: {
        //id: "391ada5f41dc45768180f90e6f981175",      
        ... ("Thunderstorm_17UTC" in LayerIDs ? {id: LayerIDs["Thunderstorm_17UTC"]} : {id: empty_layer_id}),
      },
      renderer: ThunderstormRenderer,
      id: "Thunderstorm",
    });



    let IcingRenderer = new SimpleRenderer({
      symbol: {
        type: "point-3d",
        symbolLayers: [{
          type: "object",
          width: 1120,    // diameter of the object from east to west in meters 1120
          height: 322,   // height of object in meters 322
          depth: 1620,   // diameter of the object from north to south in meters 1620
          resource: { primitive: "cube" }, material: {color: "rgba(250, 250, 5, 1)"},
        }],
      },
    })

    let IcingLayer05UTC = new SceneLayer({
      title: `Icing Layer`,
      portalItem: {
        //id: "ce224abdc1c64ca481849f0fbdb4e1fd", 
        ... ("Icing_05UTC" in LayerIDs ? {id: LayerIDs["Icing_05UTC"]} : {id: empty_layer_id}),       
      },
      renderer: IcingRenderer,
      id: "Icing",
    });

    let IcingLayer08UTC = new SceneLayer({
      title: `Icing Layer`,
      portalItem: {
        //id: "5c1188ccd10f4a9eaa8b5bc5705595c0",
        ... ("Icing_08UTC" in LayerIDs ? {id: LayerIDs["Icing_08UTC"]} : {id: empty_layer_id}),        
      },
      renderer: IcingRenderer,
      id: "Icing",
    });

    let IcingLayer11UTC = new SceneLayer({
      title: `Icing Layer`,
      portalItem: {
        //id: "6f494b46cebd487c98fdefdecfad95a0",
        ... ("Icing_11UTC" in LayerIDs ? {id: LayerIDs["Icing_11UTC"]} : {id: empty_layer_id}),        
      },
      renderer: IcingRenderer,
      id: "Icing",
    });

    let IcingLayer14UTC = new SceneLayer({
      title: `Icing Layer`,
      portalItem: {
        //id: "455a91b0be8645b9b3d024957f156712",        // Pending: Change to actual Layer
        ... ("Icing_14UTC" in LayerIDs ? {id: LayerIDs["Icing_14UTC"]} : {id: empty_layer_id}),
      },
      renderer: IcingRenderer,
      id: "Icing",
    });

    let IcingLayer17UTC = new SceneLayer({
      title: `Icing Layer`,
      portalItem: {
        //id: "4d0893e5562b43af81f8fba233dfbefe",
        ... ("Icing_17UTC" in LayerIDs ? {id: LayerIDs["Icing_17UTC"]} : {id: empty_layer_id}),        
      },
      renderer: IcingRenderer,
      id: "Icing",
    });


     
    
    let WaypointsFeatureLayerCreated = false
    var FlightPathPoints;
    function createWaypointsFeatureLayer(features){
      FlightPathPoints = new FeatureLayer ({
        id: "FlightPathFL",
        fields: [
          {
            name: "ObjectID",
            alias: "ObjectID",
            type: "oid"
          }, {
            name: "type",
            alias: "Type",
            type: "string"
          }, {
            name: "place",
            alias: "Place",
            type: "string"
          }],
          objectIdField: "ObjectID", // inferred from fields array if not specified
          geometryType: "point", // geometryType and spatialReference are inferred from the first feature
                                // in the source array if they are not specified.
          source: [features],  
          renderer: {
            type: "simple",  // autocasts as new SimpleRenderer()
            symbol: {
              type: "point-3d",  // autocasts as new SimpleMarkerSymbol()
              symbolLayers: [{
                type: "object",  // autocasts as new PathSymbol3DLayer()
                width: 500,    // width of the sphere in meters
                resource: { primitive: "sphere" },
                material: { color: "red" }
              }],
              }
          },
          spatialReference: appConfig.activeView.spatialReference,
          legendEnabled: false,

          hasZ: true, 
          outFields: ["*"]
      });
      appConfig.activeView.map.add(FlightPathPoints);
    }
    
    let PathFeatureLayerCreated = false
    var FlightPath;
    function createPathFeatureLayer(features){
      FlightPath = new FeatureLayer ({
        id: "WaypointsFL",
        fields: [
          {
            name: "ObjectID",
            alias: "ObjectID",
            type: "oid"
          }, {
            name: "type",
            alias: "Type",
            type: "string"
          }, {
            name: "place",
            alias: "Place",
            type: "string"
          }],
          objectIdField: "ObjectID", // inferred from fields array if not specified
          geometryType: "polyline", // geometryType and spatialReference are inferred from the first feature
                                // in the source array if they are not specified.
          renderer: {
            type: "simple",  // autocasts as new SimpleRenderer()
            symbol: {
              type: "line-3d",  // autocasts as new SimpleMarkerSymbol()
              symbolLayers: [{
                type: "path",  // autocasts as new PathSymbol3DLayer()
                profile: "circle",
                width: 200,    // width of the tube in meters
                material: { color: "red"}
              }],
            }
          },
          spatialReference: appConfig.activeView.spatialReference,
          source: [features],  //  an array of graphics with geometry and attributes
          legendEnabled: false,
          hasZ: true,
          outFields: ["*"]
      });
      appConfig.activeView.map.add(FlightPath);
    }

    /*
    let ICAO = new TileLayer({
        url: "https://tiles.arcgis.com/tiles/9N9SahQkXAzBgwts/arcgis/rest/services/luftfahrtkarten_icao_total_50_2056_tif/MapServer",
    });*/
    

    // Create Map instance
    const map = new Map({
      basemap: "arcgis-topographic",  // Basemap layer service
      ground: "world-elevation",      // Elevation service
    });


    // Create 3D view and and set active
    appConfig.sceneView = createView(initialViewParams3D, "3d");
    appConfig.sceneView.map = map;
    appConfig.activeView = appConfig.sceneView;

    // Add Layers to the active View
    appConfig.activeView.map.add(CloudLayer05UTC)
    appConfig.activeView.map.add(CloudLayer08UTC)
    appConfig.activeView.map.add(CloudLayer11UTC)
    appConfig.activeView.map.add(CloudLayer14UTC)
    appConfig.activeView.map.add(CloudLayer17UTC)
    appConfig.activeView.map.add(HorizontalWindLayer05UTC)
    appConfig.activeView.map.add(HorizontalWindLayer08UTC)
    appConfig.activeView.map.add(HorizontalWindLayer11UTC)
    appConfig.activeView.map.add(HorizontalWindLayer14UTC)
    appConfig.activeView.map.add(HorizontalWindLayer17UTC)
    appConfig.activeView.map.add(VerticalWindLayer05UTC)
    appConfig.activeView.map.add(VerticalWindLayer08UTC)
    appConfig.activeView.map.add(VerticalWindLayer11UTC)
    appConfig.activeView.map.add(VerticalWindLayer14UTC)
    appConfig.activeView.map.add(VerticalWindLayer17UTC)
    appConfig.activeView.map.add(ThunderstormLayer05UTC)
    appConfig.activeView.map.add(ThunderstormLayer08UTC)
    appConfig.activeView.map.add(ThunderstormLayer11UTC)
    appConfig.activeView.map.add(ThunderstormLayer14UTC)
    appConfig.activeView.map.add(ThunderstormLayer17UTC)
    appConfig.activeView.map.add(IcingLayer05UTC)
    appConfig.activeView.map.add(IcingLayer08UTC)
    appConfig.activeView.map.add(IcingLayer11UTC)
    appConfig.activeView.map.add(IcingLayer14UTC)
    appConfig.activeView.map.add(IcingLayer17UTC)
    appConfig.activeView.on("layerview-create", (event) => {
      if (event.layer.id === "CLC" && document.getElementById("CLCLayer").checked === false) {
        CloudLayer05UTC.visible = false;
        CloudLayer08UTC.visible = false;
        CloudLayer11UTC.visible = false;
        CloudLayer14UTC.visible = false;
        CloudLayer17UTC.visible = false;
      }
      if (event.layer.id === "HorizontalWind" && document.getElementById("HorizontalWindLayer").checked === false) {
        HorizontalWindLayer05UTC.visible = false;
        HorizontalWindLayer08UTC.visible = false;
        HorizontalWindLayer11UTC.visible = false;
        HorizontalWindLayer14UTC.visible = false;
        HorizontalWindLayer17UTC.visible = false;
      }
      if (event.layer.id === "VerticalWind" && document.getElementById("VerticalWindLayer").checked === false) {
        VerticalWindLayer05UTC.visible = false;
        VerticalWindLayer08UTC.visible = false;
        VerticalWindLayer11UTC.visible = false;
        VerticalWindLayer14UTC.visible = false;
        VerticalWindLayer17UTC.visible = false;

        /*// Query for the minimal Windspeed in the vertical Wind Layer (to changing the renderer's visual variable min/max values)
        let minVerticalWind = {
          onStatisticField: "W", 
          outStatisticFieldName: "minW",
          statisticType: "min"
        }
        let query = VerticalWindLayer.createQuery();
        query.outStatistics = [ minVerticalWind ];
        VerticalWindLayer.queryFeatures(query)
          .then(function(response){
             let stats = response.features[0].attributes;
             console.log("output stats:", stats);
          });*/
      }
      if (event.layer.id === "Thunderstorm" && document.getElementById("ThunderstormLayer").checked === false) {
        ThunderstormLayer05UTC.visible = false;
        ThunderstormLayer08UTC.visible = false;
        ThunderstormLayer11UTC.visible = false;
        ThunderstormLayer14UTC.visible = false;
        ThunderstormLayer17UTC.visible = false;
      }
      if (event.layer.id === "Icing" && document.getElementById("IcingLayer").checked === false) {
        IcingLayer05UTC.visible = false;
        IcingLayer08UTC.visible = false;
        IcingLayer11UTC.visible = false;
        IcingLayer14UTC.visible = false;
        IcingLayer17UTC.visible = false;
      }
    });


    // Get Date from Layers
    HorizontalWindLayer05UTC.when(function(){
      let VisualisationDate = HorizontalWindLayer05UTC.portalItem.description
      DateDiv.innerHTML = VisualisationDate
    })
    
    /*let MapLayerList = new Array(appConfig.activeView.map.layers.items)
    MapLayerList = MapLayerList[0]
    let DateList = []
    for( var i = 0; i <= MapLayerList.length-1; i++){    
      var item = MapLayerList[i].portalItem     
      console.log(item)       
      DateList.push(item.description)
    }
    */

    // create 2D view, won't initialize until container is set
    initialViewParams2D.container = null;
    initialViewParams2D.map = map;
    appConfig.mapView = createView(initialViewParams2D, "2d");


    // Switch the view between 2D and 3D each time the button is clicked
    switchButton.addEventListener("click", () => {
      switchView();
    });
    
    

    // Switches the view from 2D to 3D and vice versa
    function switchView() {
      let is3D = appConfig.activeView.type === "3d";
      if (is3D){
        var spatialRef3D = appConfig.sceneView.spatialReference
      };

      if (is3D) {
        // if the input view is a SceneView, set the viewpoint on the
        // mapView instance. Set the container on the mapView and flag
        // it as the active view
        
        appConfig.mapView.viewpoint = appConfig.activeView.viewpoint.clone();
        appConfig.activeView.container = null;
        appConfig.mapView.container = appConfig.container;
        appConfig.activeView = appConfig.mapView;

        // Change view of UI Elements and add to activeView
        layerListExpand.view = appConfig.activeView
        homeBtn.view = appConfig.activeView
        BasemapExpand.view = appConfig.activeView
        BasemapGallery.view = appConfig.activeView
        FlightPathExpand.view = appConfig.activeView
        PathProfileExpand.view = appConfig.activeView
        InfoExpand.view = appConfig.activeView
        PreferencesExpand.view = appConfig.activeView
        appConfig.activeView.ui.add(searchWidget, {position: "top-right"});
        appConfig.activeView.ui.add(layerListExpand, "top-right");
        appConfig.activeView.ui.add(homeBtn, "top-left");
        appConfig.activeView.ui.add(BasemapExpand, "top-left");
        appConfig.activeView.ui.add(CloudFilterExpand, "top-right");
        appConfig.activeView.ui.add(FlightPathExpand, "top-right");
        appConfig.activeView.ui.add(PathProfileExpand, "top-right");
        appConfig.activeView.ui.add(PreferencesExpand, "top-right");
        appConfig.activeView.ui.add(InfoExpand, "bottom-right");
        appConfig.activeView.ui.add(legend, "bottom-right")

        // Remove 3D-Layers
        appConfig.mapView.map.remove(CloudLayer05UTC);
        appConfig.mapView.map.remove(CloudLayer08UTC);
        appConfig.mapView.map.remove(CloudLayer11UTC);
        appConfig.mapView.map.remove(CloudLayer14UTC);
        appConfig.mapView.map.remove(CloudLayer17UTC);
        appConfig.mapView.map.remove(HorizontalWindLayer05UTC);
        appConfig.mapView.map.remove(HorizontalWindLayer08UTC);
        appConfig.mapView.map.remove(HorizontalWindLayer11UTC);
        appConfig.mapView.map.remove(HorizontalWindLayer14UTC);
        appConfig.mapView.map.remove(HorizontalWindLayer17UTC);
        appConfig.mapView.map.remove(VerticalWindLayer05UTC);
        appConfig.mapView.map.remove(VerticalWindLayer08UTC);
        appConfig.mapView.map.remove(VerticalWindLayer11UTC);
        appConfig.mapView.map.remove(VerticalWindLayer14UTC);
        appConfig.mapView.map.remove(VerticalWindLayer17UTC);
        appConfig.mapView.map.remove(ThunderstormLayer05UTC);
        appConfig.mapView.map.remove(ThunderstormLayer08UTC);
        appConfig.mapView.map.remove(ThunderstormLayer11UTC);
        appConfig.mapView.map.remove(ThunderstormLayer14UTC);
        appConfig.mapView.map.remove(ThunderstormLayer17UTC);
        appConfig.mapView.map.remove(IcingLayer05UTC);
        appConfig.mapView.map.remove(IcingLayer08UTC);
        appConfig.mapView.map.remove(IcingLayer11UTC);
        appConfig.mapView.map.remove(IcingLayer14UTC);
        appConfig.mapView.map.remove(IcingLayer17UTC);
        switchButton.value = "3D";

      } else {
        appConfig.sceneView.viewpoint = appConfig.activeView.viewpoint.clone();
        appConfig.activeView.container = null;
        appConfig.sceneView.container = appConfig.container;
        appConfig.activeView = appConfig.sceneView; 

        // Change view of UI Elements and add to activeView
        layerListExpand.view = appConfig.activeView
        homeBtn.view = appConfig.activeView
        BasemapExpand.view = appConfig.activeView
        BasemapGallery.view = appConfig.activeView
        FlightPathExpand.view = appConfig.activeView
        PathProfileExpand.view = appConfig.activeView
        InfoExpand.view = appConfig.activeView
        PreferencesExpand.view = appConfig.activeView
        appConfig.activeView.ui.add(searchWidget, {position: "top-right"});
        appConfig.activeView.ui.add(layerListExpand, "top-right");
        appConfig.activeView.ui.add(homeBtn, "top-left");
        appConfig.activeView.ui.add(BasemapExpand, "top-left");
        appConfig.activeView.ui.add(CloudFilterExpand, "top-right");
        appConfig.activeView.ui.add(FlightPathExpand, "top-right");
        appConfig.activeView.ui.add(PathProfileExpand, "top-right");
        appConfig.activeView.ui.add(PreferencesExpand, "top-right");
        appConfig.activeView.ui.add(InfoExpand, "bottom-right");
        appConfig.activeView.ui.add(legend, "bottom-right")
        // Add 3D-Layers
        appConfig.activeView.map.add(CloudLayer05UTC)
        appConfig.activeView.map.add(CloudLayer08UTC)
        appConfig.activeView.map.add(CloudLayer11UTC)
        appConfig.activeView.map.add(CloudLayer14UTC)
        appConfig.activeView.map.add(CloudLayer17UTC)
        appConfig.activeView.map.add(HorizontalWindLayer05UTC)
        appConfig.activeView.map.add(HorizontalWindLayer08UTC)
        appConfig.activeView.map.add(HorizontalWindLayer11UTC)
        appConfig.activeView.map.add(HorizontalWindLayer14UTC)
        appConfig.activeView.map.add(HorizontalWindLayer17UTC)
        appConfig.mapView.map.add(VerticalWindLayer05UTC);
        appConfig.mapView.map.add(VerticalWindLayer08UTC);
        appConfig.mapView.map.add(VerticalWindLayer11UTC);
        appConfig.mapView.map.add(VerticalWindLayer14UTC);
        appConfig.mapView.map.add(VerticalWindLayer17UTC);
        appConfig.mapView.map.add(ThunderstormLayer05UTC);
        appConfig.mapView.map.add(ThunderstormLayer08UTC);
        appConfig.mapView.map.add(ThunderstormLayer11UTC);
        appConfig.mapView.map.add(ThunderstormLayer14UTC);
        appConfig.mapView.map.add(ThunderstormLayer17UTC);
        appConfig.mapView.map.add(IcingLayer05UTC);
        appConfig.mapView.map.add(IcingLayer08UTC);
        appConfig.mapView.map.add(IcingLayer11UTC);
        appConfig.mapView.map.add(IcingLayer14UTC);
        appConfig.mapView.map.add(IcingLayer17UTC);
        switchButton.value = "2D";        
      }
    }

    // Convenience function for creating either a 2D or 3D view dependant on the type parameter
    function createView(params, type) {
      var view;
      if (type === "2d") {
        view = new MapView(params);
        return view;
      } else {
        view = new SceneView(params);
      }
      return view;
    }


    // Get all LayerViews as soon as they are created
    let CloudLayerView05UTC = null;
    let CloudLayerView08UTC = null;
    let CloudLayerView11UTC = null;
    let CloudLayerView14UTC = null;
    let CloudLayerView17UTC = null;
    let activeCloudLayer = null;
    let activeCloudLayerView = null;
    let IcingLayerView05UTC = null
    let IcingLayerView08UTC = null
    let IcingLayerView11UTC = null
    let IcingLayerView14UTC = null
    let IcingLayerView17UTC = null
    let activeIcingLayer = null;
    let activeIcingLayerView = null;
    let VerticalWindLayerView05UTC = null
    let VerticalWindLayerView08UTC = null
    let VerticalWindLayerView11UTC = null
    let VerticalWindLayerView14UTC = null
    let VerticalWindLayerView17UTC = null
    let activeVerticalWindLayer = null;
    let activeVerticalWindLayerView = null;
    let HorizontalWindLayerView05UTC = null
    let HorizontalWindLayerView08UTC = null
    let HorizontalWindLayerView11UTC = null
    let HorizontalWindLayerView14UTC = null
    let HorizontalWindLayerView17UTC = null
    let activeHorizontalWindLayer = null;
    let activeHorizontalWindLayerView = null;
    let ThunderstormLayerView05UTC = null
    let ThunderstormLayerView08UTC = null
    let ThunderstormLayerView11UTC = null
    let ThunderstormLayerView14UTC = null
    let ThunderstormLayerView17UTC = null
    let activeThunderstormLayer = null;
    let activeThunderstormLayerView = null;

    appConfig.activeView.whenLayerView(CloudLayer05UTC).then((lv) => {
      CloudLayerView05UTC = lv
    });
    appConfig.activeView.whenLayerView(CloudLayer08UTC).then((lv) => {
      CloudLayerView08UTC = lv
    });
    appConfig.activeView.whenLayerView(CloudLayer08UTC).then((lv) => {
      CloudLayerView11UTC = lv
    });
    appConfig.activeView.whenLayerView(CloudLayer08UTC).then((lv) => {
      CloudLayerView14UTC = lv
    });
    appConfig.activeView.whenLayerView(CloudLayer08UTC).then((lv) => {
      CloudLayerView17UTC = lv
    });
    appConfig.activeView.whenLayerView(IcingLayer05UTC).then((lv) => {
      IcingLayerView05UTC = lv
    });
    appConfig.activeView.whenLayerView(IcingLayer08UTC).then((lv) => {
      IcingLayerView08UTC = lv
    });
    appConfig.activeView.whenLayerView(IcingLayer11UTC).then((lv) => {
      IcingLayerView11UTC = lv
    });
    appConfig.activeView.whenLayerView(IcingLayer14UTC).then((lv) => {
      IcingLayerView14UTC = lv
    });
    appConfig.activeView.whenLayerView(IcingLayer17UTC).then((lv) => {
      IcingLayerView17UTC = lv
    });
    appConfig.activeView.whenLayerView(HorizontalWindLayer05UTC).then((lv) => {
      HorizontalWindLayerView05UTC = lv
    });
    appConfig.activeView.whenLayerView(HorizontalWindLayer08UTC).then((lv) => {
      HorizontalWindLayerView08UTC = lv
    });
    appConfig.activeView.whenLayerView(HorizontalWindLayer11UTC).then((lv) => {
      HorizontalWindLayerView11UTC = lv
    });
    appConfig.activeView.whenLayerView(HorizontalWindLayer14UTC).then((lv) => {
      HorizontalWindLayerView14UTC = lv
    });
    appConfig.activeView.whenLayerView(HorizontalWindLayer17UTC).then((lv) => {
      HorizontalWindLayerView17UTC = lv
    });
    appConfig.activeView.whenLayerView(VerticalWindLayer05UTC).then((lv) => {
      VerticalWindLayerView05UTC = lv
    });
    appConfig.activeView.whenLayerView(VerticalWindLayer08UTC).then((lv) => {
      VerticalWindLayerView08UTC = lv
    });
    appConfig.activeView.whenLayerView(VerticalWindLayer11UTC).then((lv) => {
      VerticalWindLayerView11UTC = lv
    });
    appConfig.activeView.whenLayerView(VerticalWindLayer14UTC).then((lv) => {
      VerticalWindLayerView14UTC = lv
    });
    appConfig.activeView.whenLayerView(VerticalWindLayer17UTC).then((lv) => {
      VerticalWindLayerView17UTC = lv
    });
    appConfig.activeView.whenLayerView(ThunderstormLayer05UTC).then((lv) => {
      ThunderstormLayerView05UTC = lv
    });
    appConfig.activeView.whenLayerView(ThunderstormLayer08UTC).then((lv) => {
      ThunderstormLayerView08UTC = lv
    });
    appConfig.activeView.whenLayerView(ThunderstormLayer11UTC).then((lv) => {
      ThunderstormLayerView11UTC = lv
    });
    appConfig.activeView.whenLayerView(ThunderstormLayer14UTC).then((lv) => {
      ThunderstormLayerView14UTC = lv
    });
    appConfig.activeView.whenLayerView(ThunderstormLayer17UTC).then((lv) => {
      ThunderstormLayerView17UTC = lv
    });

    // Select activeLayers and activeLayerViews depending on the selected Time
    document.getElementById("UTC05")
      .addEventListener("click", (event) => {
        updateLayers(event)
        changeBackgroundColor(event)
      })
    document.getElementById("UTC08")
      .addEventListener("click", (event) => {
        updateLayers(event)
        changeBackgroundColor(event)
      })
    document.getElementById("UTC11")
      .addEventListener("click", (event) => {
        updateLayers(event)
        changeBackgroundColor(event)
      })
    document.getElementById("UTC14")
      .addEventListener("click", (event) => {
        updateLayers(event)
        changeBackgroundColor(event)
      })
    document.getElementById("UTC17")
      .addEventListener("click", (event) => {
        updateLayers(event)
        changeBackgroundColor(event)
      })
    
    function changeBackgroundColor(timeElement) {
      elements = document.querySelectorAll("div.time-element")
      elements.forEach(item => {
        if (item.id == timeElement.target.id) {
          document.getElementById(item.id).style.backgroundColor = "grey"
        } else {
          document.getElementById(item.id).style.backgroundColor = "black"
        }
      });
      document.getElementById("TimeWarningDiv").style.visibility = "hidden"
    }

    function updateLayers(timestamp) {
      if (timestamp.target.innerHTML == "0500 UTC") {
        // Cloud Layer
        activeCloudLayer = CloudLayer05UTC
        activeCloudLayerView = CloudLayerView05UTC
        activeCloudLayer.visible = CLCLayerToggle.checked
        CloudLayer08UTC.visible = false
        CloudLayer11UTC.visible = false
        CloudLayer14UTC.visible = false
        CloudLayer17UTC.visible = false
        checkLayerExists(activeCloudLayer, CLCLayerToggle)
        // Horizontal Wind Layer
        activeHorizontalWindLayer = HorizontalWindLayer05UTC
        activeHorizontalWindLayerView = HorizontalWindLayerView05UTC
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked
        HorizontalWindLayer08UTC.visible = false
        HorizontalWindLayer11UTC.visible = false
        HorizontalWindLayer14UTC.visible = false
        HorizontalWindLayer17UTC.visible = false
        checkLayerExists(activeHorizontalWindLayer, HorizontalWindLayerToggle)
        // Vertical Wind Layer
        activeVerticalWindLayer = VerticalWindLayer05UTC
        activeVerticalWindLayerView = VerticalWindLayerView05UTC
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked
        VerticalWindLayer08UTC.visible = false
        VerticalWindLayer11UTC.visible = false
        VerticalWindLayer14UTC.visible = false
        VerticalWindLayer17UTC.visible = false
        checkLayerExists(activeVerticalWindLayer, VerticalWindLayerToggle)
        // Thunderstorm Layer
        activeThunderstormLayer = ThunderstormLayer05UTC
        activeThunderstormLayerView = ThunderstormLayerView05UTC
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked
        ThunderstormLayer08UTC.visible = false
        ThunderstormLayer11UTC.visible = false
        ThunderstormLayer14UTC.visible = false
        ThunderstormLayer17UTC.visible = false
        checkLayerExists(activeThunderstormLayer, ThunderstormLayerToggle)
        // Icing Layer
        activeIcingLayer = IcingLayer05UTC
        activeIcingLayerView = IcingLayerView05UTC
        activeIcingLayer.visible = IcingLayerToggle.checked
        IcingLayer08UTC.visible = false
        IcingLayer11UTC.visible = false
        IcingLayer14UTC.visible = false
        IcingLayer17UTC.visible = false
        checkLayerExists(activeIcingLayer, IcingLayerToggle)
      } else if (timestamp.target.innerHTML == "0800 UTC") {
        // Cloud Layer
        activeCloudLayer = CloudLayer08UTC
        activeCloudLayerView = CloudLayerView08UTC
        activeCloudLayer.visible = CLCLayerToggle.checked
        CloudLayer05UTC.visible = false
        CloudLayer11UTC.visible = false
        CloudLayer14UTC.visible = false
        CloudLayer17UTC.visible = false
        checkLayerExists(activeCloudLayer, CLCLayerToggle)
        // Horizontal Wind Layer
        activeHorizontalWindLayer = HorizontalWindLayer08UTC
        activeHorizontalWindLayerView = HorizontalWindLayerView08UTC
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked
        HorizontalWindLayer05UTC.visible = false
        HorizontalWindLayer11UTC.visible = false
        HorizontalWindLayer14UTC.visible = false
        HorizontalWindLayer17UTC.visible = false
        checkLayerExists(activeHorizontalWindLayer, HorizontalWindLayerToggle)
        // Vertical Wind Layer
        activeVerticalWindLayer = VerticalWindLayer08UTC
        activeVerticalWindLayerView = VerticalWindLayerView08UTC
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked
        VerticalWindLayer05UTC.visible = false
        VerticalWindLayer11UTC.visible = false
        VerticalWindLayer14UTC.visible = false
        VerticalWindLayer17UTC.visible = false
        checkLayerExists(activeVerticalWindLayer, VerticalWindLayerToggle)
        // Thunderstorm Layer
        activeThunderstormLayer = ThunderstormLayer08UTC
        activeThunderstormLayerView = ThunderstormLayerView08UTC
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked
        ThunderstormLayer05UTC.visible = false
        ThunderstormLayer11UTC.visible = false
        ThunderstormLayer14UTC.visible = false
        ThunderstormLayer17UTC.visible = false
        checkLayerExists(activeThunderstormLayer, ThunderstormLayerToggle)
        // Icing Layer
        activeIcingLayer = IcingLayer08UTC
        activeIcingLayerView = IcingLayerView08UTC
        activeIcingLayer.visible = IcingLayerToggle.checked
        IcingLayer05UTC.visible = false
        IcingLayer11UTC.visible = false
        IcingLayer14UTC.visible = false
        IcingLayer17UTC.visible = false
        checkLayerExists(activeIcingLayer, IcingLayerToggle)
      } else if (timestamp.target.innerHTML == "1100 UTC") {
        // Cloud Layer
        activeCloudLayer = CloudLayer11UTC
        activeCloudLayerView = CloudLayerView11UTC
        activeCloudLayer.visible = CLCLayerToggle.checked
        CloudLayer05UTC.visible = false
        CloudLayer08UTC.visible = false
        CloudLayer14UTC.visible = false
        CloudLayer17UTC.visible = false
        checkLayerExists(activeCloudLayer, CLCLayerToggle)
        // Horizontal Wind Layer
        activeHorizontalWindLayer = HorizontalWindLayer11UTC
        activeHorizontalWindLayerView = HorizontalWindLayerView11UTC
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked
        HorizontalWindLayer05UTC.visible = false
        HorizontalWindLayer08UTC.visible = false
        HorizontalWindLayer14UTC.visible = false
        HorizontalWindLayer17UTC.visible = false
        checkLayerExists(activeHorizontalWindLayer, HorizontalWindLayerToggle)
        // Vertical Wind Layer
        activeVerticalWindLayer = VerticalWindLayer11UTC
        activeVerticalWindLayerView = VerticalWindLayerView11UTC
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked
        VerticalWindLayer05UTC.visible = false
        VerticalWindLayer08UTC.visible = false
        VerticalWindLayer14UTC.visible = false
        VerticalWindLayer17UTC.visible = false
        checkLayerExists(activeVerticalWindLayer, VerticalWindLayerToggle)
        // Thunderstorm Layer
        activeThunderstormLayer = ThunderstormLayer11UTC
        activeThunderstormLayerView = ThunderstormLayerView11UTC
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked
        ThunderstormLayer05UTC.visible = false
        ThunderstormLayer08UTC.visible = false
        ThunderstormLayer14UTC.visible = false
        ThunderstormLayer17UTC.visible = false
        checkLayerExists(activeThunderstormLayer, ThunderstormLayerToggle)
        // Icing Layer
        activeIcingLayer = IcingLayer11UTC
        activeIcingLayerView = IcingLayerView11UTC
        activeIcingLayer.visible = IcingLayerToggle.checked
        IcingLayer05UTC.visible = false
        IcingLayer08UTC.visible = false
        IcingLayer14UTC.visible = false
        IcingLayer17UTC.visible = false
        checkLayerExists(activeIcingLayer, IcingLayerToggle)
      } else if (timestamp.target.innerHTML == "1400 UTC") {
        // Cloud Layer
        activeCloudLayer = CloudLayer14UTC
        activeCloudLayerView = CloudLayerView14UTC
        activeCloudLayer.visible = CLCLayerToggle.checked
        CloudLayer05UTC.visible = false
        CloudLayer08UTC.visible = false
        CloudLayer11UTC.visible = false
        CloudLayer17UTC.visible = false
        checkLayerExists(activeCloudLayer, CLCLayerToggle)
        // Horizontal Wind Layer
        activeHorizontalWindLayer = HorizontalWindLayer14UTC
        activeHorizontalWindLayerView = HorizontalWindLayerView14UTC
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked
        HorizontalWindLayer05UTC.visible = false
        HorizontalWindLayer08UTC.visible = false
        HorizontalWindLayer11UTC.visible = false
        HorizontalWindLayer17UTC.visible = false
        checkLayerExists(activeHorizontalWindLayer, HorizontalWindLayerToggle)
        // Vertical Wind Layer
        activeVerticalWindLayer = VerticalWindLayer14UTC
        activeVerticalWindLayerView = VerticalWindLayerView14UTC
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked
        VerticalWindLayer05UTC.visible = false
        VerticalWindLayer08UTC.visible = false
        VerticalWindLayer11UTC.visible = false
        VerticalWindLayer17UTC.visible = false
        checkLayerExists(activeVerticalWindLayer, VerticalWindLayerToggle)
        // Thunderstorm Layer
        activeThunderstormLayer = ThunderstormLayer14UTC
        activeThunderstormLayerView = ThunderstormLayerView14UTC
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked
        ThunderstormLayer05UTC.visible = false
        ThunderstormLayer08UTC.visible = false
        ThunderstormLayer11UTC.visible = false
        ThunderstormLayer17UTC.visible = false
        checkLayerExists(activeThunderstormLayer, ThunderstormLayerToggle)
        // Icing Layer
        activeIcingLayer = IcingLayer14UTC
        activeIcingLayerView = IcingLayerView14UTC
        activeIcingLayer.visible = IcingLayerToggle.checked
        IcingLayer05UTC.visible = false
        IcingLayer08UTC.visible = false
        IcingLayer11UTC.visible = false
        IcingLayer17UTC.visible = false
        checkLayerExists(activeIcingLayer, IcingLayerToggle)
      } else if (timestamp.target.innerHTML == "1700 UTC") {
        // Cloud Layer
        activeCloudLayer = CloudLayer17UTC
        activeCloudLayerView = CloudLayerView17UTC
        activeCloudLayer.visible = CLCLayerToggle.checked
        CloudLayer05UTC.visible = false
        CloudLayer08UTC.visible = false
        CloudLayer11UTC.visible = false
        CloudLayer14UTC.visible = false
        checkLayerExists(activeCloudLayer, CLCLayerToggle)
        // Horizontal Wind Layer
        activeHorizontalWindLayer = HorizontalWindLayer17UTC
        activeHorizontalWindLayerView = HorizontalWindLayerView17UTC
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked
        HorizontalWindLayer05UTC.visible = false
        HorizontalWindLayer08UTC.visible = false
        HorizontalWindLayer11UTC.visible = false
        HorizontalWindLayer14UTC.visible = false
        checkLayerExists(activeHorizontalWindLayer, HorizontalWindLayerToggle)
        // Vertical Wind Layer
        activeVerticalWindLayer = VerticalWindLayer17UTC
        activeVerticalWindLayerView = VerticalWindLayerView17UTC
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked
        VerticalWindLayer05UTC.visible = false
        VerticalWindLayer08UTC.visible = false
        VerticalWindLayer11UTC.visible = false
        VerticalWindLayer14UTC.visible = false
        checkLayerExists(activeVerticalWindLayer, VerticalWindLayerToggle)
        // Thunderstorm Layer
        activeThunderstormLayer = ThunderstormLayer17UTC
        activeThunderstormLayerView = ThunderstormLayerView17UTC
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked
        ThunderstormLayer05UTC.visible = false
        ThunderstormLayer08UTC.visible = false
        ThunderstormLayer11UTC.visible = false
        ThunderstormLayer14UTC.visible = false
        checkLayerExists(activeThunderstormLayer, ThunderstormLayerToggle)
        // Icing Layer
        activeIcingLayer = IcingLayer17UTC
        activeIcingLayerView = IcingLayerView17UTC
        activeIcingLayer.visible = IcingLayerToggle.checked
        IcingLayer05UTC.visible = false
        IcingLayer08UTC.visible = false
        IcingLayer11UTC.visible = false
        IcingLayer14UTC.visible = false
        checkLayerExists(activeIcingLayer, IcingLayerToggle)
      } 
    }

    // Function to check if layer exist for selected timestamp. If not add a Warning.
    function checkLayerExists(activeLayer, LayerToggle){
      if ((activeLayer.portalItem.id == empty_layer_id) & LayerToggle.checked){
        addWarning(activeLayer)
      }
      else if ((activeLayer.portalItem.id == empty_layer_id) & !LayerToggle.checked){
        deleteWarning(activeLayer)
      }
      else{
        deleteWarning(activeLayer)
      }
    }
    function addWarning(Layer) {
      WarningDiv.style.visibility = "visible";
      let WarningLayerName = Layer.id
      var innerWarningDiv = document.createElement('div');
      innerWarningDiv.className = 'warning-child';
      innerWarningDiv.id = WarningLayerName+'LayerWarning';
      innerWarningDiv.innerHTML = WarningLayerName+" Layer: NO DATA available for the selected variable and selected time!!"
      WarningDiv.appendChild(innerWarningDiv)
    }
    function deleteWarning(Layer) {
      let WarningLayerName = Layer.id
      if (!!document.getElementById(WarningLayerName+'LayerWarning')){
        document.getElementById(WarningLayerName+'LayerWarning').remove();
      }  
      if ((document.getElementsByClassName("warning-child").length == 0)){
        WarningDiv.style.visibility = "hidden";
      }    
    }


    // Select the layer to apply the LayerView Distance Filter
    let CloudsLayerViewFilterSelected = false;
    document.getElementById("CloudLayerViewFilter")
      .addEventListener("change", (event) => {
        CloudsLayerViewFilterSelected = !!event.target.checked;
        updateFilter();
        FilterWarning();
      });
    let IcingLayerViewFilterSelected = false;
    document.getElementById("IcingLayerViewFilter")
      .addEventListener("change", (event) => {
        IcingLayerViewFilterSelected = !!event.target.checked;
        updateFilter();
        FilterWarning();
      });
    let HorizontalWindLayerViewFilterSelected = false;
    document.getElementById("HorizontalWindLayerViewFilter")
      .addEventListener("change", (event) => {
        HorizontalWindLayerViewFilterSelected = !!event.target.checked;
        updateFilter();
        FilterWarning();
      });  
    let VerticalWindLayerViewFilterSelected = false;
    document.getElementById("VerticalWindLayerViewFilter")
      .addEventListener("change", (event) => {
        VerticalWindLayerViewFilterSelected = !!event.target.checked;
        updateFilter();
        FilterWarning();
      });
    let ThunderstormLayerViewFilterSelected = false;
    document.getElementById("ThunderstormLayerViewFilter")
      .addEventListener("change", (event) => {
        ThunderstormLayerViewFilterSelected = !!event.target.checked;
        updateFilter();
        FilterWarning();
      });
    
    // Watch for Camera View Position change to update the Distance LayerView Filter
    watchUtils.watch(appConfig.activeView, "navigating", () => {
      // Get the new extent of the view only when view is stationary.
      //if (appConfig.activeView.extent) {
        updateFilter()
        //updateCloudOrientation()
      //}
    });

    // Event Listener for Filter Distance Slider in Preferences Menu
    let LayerViewFilterDistance = 20;
    LayerViewFilterDistanceSlider.addEventListener("change", (event) => {  
      LayerViewFilterDistance = event.target.value;
      updateFilter()
    });
     

    function updateFilter() {
      // Get current Camera Position
      var cam = appConfig.activeView.camera.position
      var cam_long = appConfig.activeView.camera.position.longitude;
      var cam_lat = appConfig.activeView.camera.position.latitude
      var cam_Z = appConfig.activeView.camera.position.z
      // the position is autocast as new Point()
       let camera_point = new Point({
        latitude: cam_lat,
        longitude: cam_long,
        z: cam_Z,
        hasZ: true
      });

      const featureFilter = {
        // autocasts to FeatureFilter
        geometry: camera_point,
        spatialRelationship: "disjoint",
        distance: LayerViewFilterDistance,
        units: "kilometers"
      };
    
      if (activeCloudLayerView) {
        if (CloudsLayerViewFilterSelected) {
          if (activeCloudLayerView.filter) {
            let filter_clone = activeCloudLayerView.filter.clone()
            filter_clone.geometry = featureFilter.geometry
            filter_clone.spatialRelationship = featureFilter.spatialRelationship
            filter_clone.distance = featureFilter.distance
            filter_clone.units = featureFilter.units
            activeCloudLayerView.filter = filter_clone
          } else {
            activeCloudLayerView.filter = featureFilter;
          }
        } 
      }
      if (activeIcingLayerView) {
        if (IcingLayerViewFilterSelected) {
          if (activeIcingLayerView.filter) {
            let filter_clone = activeIcingLayerView.filter.clone()
            filter_clone.geometry = featureFilter.geometry
            filter_clone.spatialRelationship = featureFilter.spatialRelationship
            filter_clone.distance = featureFilter.distance
            filter_clone.units = featureFilter.units
            activeIcingLayerView.filter = filter_clone
          } else {
            activeIcingLayerView.filter = featureFilter;
          }
        } 
      }
      if (activeHorizontalWindLayerView) {
        if (HorizontalWindLayerViewFilterSelected) {
          if (activeHorizontalWindLayerView.filter) {
            let filter_clone = activeHorizontalWindLayerView.filter.clone()
            filter_clone.geometry = featureFilter.geometry
            filter_clone.spatialRelationship = featureFilter.spatialRelationship
            filter_clone.distance = featureFilter.distance
            filter_clone.units = featureFilter.units
            activeHorizontalWindLayerView.filter = filter_clone
          } else {
            activeHorizontalWindLayerView.filter = featureFilter;
          }
        } 
      }
      if (activeVerticalWindLayerView) {
        if (VerticalWindLayerViewFilterSelected) {
          if (activeVerticalWindLayerView.filter) {
            let filter_clone = activeVerticalWindLayerView.filter.clone()
            filter_clone.geometry = featureFilter.geometry
            filter_clone.spatialRelationship = featureFilter.spatialRelationship
            filter_clone.distance = featureFilter.distance
            filter_clone.units = featureFilter.units
            activeVerticalWindLayerView.filter = filter_clone
          } else {
            activeVerticalWindLayerView.filter = featureFilter;
          }
        } 
      }
      if (activeThunderstormLayerView) {
        if (ThunderstormLayerViewFilterSelected) {
          if (activeThunderstormLayerView.filter) {
            let filter_clone = activeThunderstormLayerView.filter.clone()
            filter_clone.geometry = featureFilter.geometry
            filter_clone.spatialRelationship = featureFilter.spatialRelationship
            filter_clone.distance = featureFilter.distance
            filter_clone.units = featureFilter.units
            activeThunderstormLayerView.filter = filter_clone
          } else {
            activeThunderstormLayerView.filter = featureFilter;
          }
        } 
      }
    }


    // Flight Path Function to create a flight path based on Waypoints added by the user
    FlightPathPointsLon = []
    FlightPathPointsLat = []
    WaypointHeights = []
    ActiveWaypointObjID = ""
    previousHeight = document.getElementById("waypointHeight").value

    appConfig.activeView.on("click", function(event) {
      // Overwrite default click-for-popup behavior of Point feature layer to display own popup
      if (event.button == 2 && addFlightPathEnabled) {
        appConfig.activeView.popup.autoOpenEnabled = false;
      
        // Get the coordinates of the click on the view
        lat = Math.round(event.mapPoint.latitude * 1000) / 1000;
        lon = Math.round(event.mapPoint.longitude * 1000) / 1000;

        // Add Points coordinates to FlightPathPoints Array
        FlightPathPointsLon.push(lon)
        FlightPathPointsLat.push(lat)
        
        appConfig.activeView.popup.open({
          title: "Waypoint Coordinates: [" + lon + ", " + lat +"]",   // Set the popup's title to the coordinates of the location
          location: event.mapPoint,                                   // Set the location of the popup to the clicked location
          content: setContentInfo(),   // Numeric Field to enter the desired Waypoint height
        });

        // Create new Point and Path Features
        HeightInput = document.getElementById("waypointHeight").value
        WaypointHeights.push(HeightInput)
        //HeightInput = 3000
        

        let Waypoint = {
          type: "point",
          longitude: lon,
          latitude: lat,
          z: HeightInput,
        }

        let newPoint = {
          addFeatures: [{
            geometry: Waypoint,
            attributes: {
              ObjectID: FlightPathPointsLat.length-1,
            }
          }],
        }

        let PathPolyline = {
          type: "polyline",  
          hasZ: true,
          paths: [
            [FlightPathPointsLon.slice(-2)[0], FlightPathPointsLat.slice(-2)[0], WaypointHeights[WaypointHeights.length-2]],
            [lon, lat, HeightInput],
          ]
        }
        console.log(WaypointHeights)
        //console.log("Path Polyline ", PathPolyline)
        let newPath = {
          addFeatures: [{
            geometry: PathPolyline,
            symbol: {
              type: "simple-line",  // autocasts as SimpleLineSymbol()
              color: [100, 119, 40],
              width: 10
            },
            attributes: {
              ObjectID: FlightPathPointsLat.length-1,
            }
          }]
        };
        // Create new FlightPath Feature Layer the first time the function is called
        if (!PathFeatureLayerCreated) {
          createPathFeatureLayer(PathPolyline)
          PathFeatureLayerCreated = true
        }
        // Create new FlightPathPoints Feature Layer the first time the function is called
        if (!WaypointsFeatureLayerCreated) {
          createWaypointsFeatureLayer(Waypoint)
          WaypointsFeatureLayerCreated = true
        }

        // Update FlightPathPoints and FlightPath Feature Layers with new Point and Path
        FlightPathPoints.applyEdits(newPoint)
        FlightPath.applyEdits(newPath)
        
        // Set the active Waypoint to the last added
        previousActiveWaypointObjID = ActiveWaypointObjID
        ActiveWaypointObjID = FlightPathPointsLat.length+1

        previousHeight = HeightInput
        
        appConfig.activeView.popup.dockEnabled = true,
        appConfig.activeView.popup.collapsed = false,
        appConfig.activeView.popup.dockOptions = {position: "auto"}
      }
    });

    // Function to setup the content of the popup window when adding a Waypoint to the view
    function setContentInfo() {
      var popupDiv = document.createElement("div");
      popupDiv.style.display = "block"
      var heightInput = document.createElement("input")
      heightInput.type = "number"
      heightInput.value = "3000"
      heightInput.id = "waypointHeight"
      var labelDiv = document.createElement("label")
      labelDiv.innerHTML = "Waypoint Height (between 1 and 10000 m):"
      labelDiv.for = "waypointHeight"
      var submitHeight = document.createElement("input")
      submitHeight.type = "submit"
      submitHeight.value = "change"
      submitHeight.id = "waypointHeightSubmit"
      popupDiv.appendChild(labelDiv)
      popupDiv.appendChild(heightInput)
      popupDiv.appendChild(submitHeight)
      return popupDiv
    }

    // Update Waypoint Height, when changed in the popup window and submitted by the "change" button
    document.addEventListener('click', (event) =>{
      if(event.target && event.target.id== 'waypointHeightSubmit'){
        // Get new Height Input Value
        HeightInput = document.getElementById("waypointHeight").value
        WaypointHeights.splice(WaypointHeights.length-1,1)
        WaypointHeights.push(HeightInput)

        // Update Feature Layers
        updateWaypointAttributes = {
          updateFeatures: [{
            attributes: {
              ObjectID: ActiveWaypointObjID,
            },
            geometry : {
              type: "point",
              longitude: lon,
              latitude: lat,
              z: HeightInput,
          }
          }]
        },
        FlightPathPoints.applyEdits(updateWaypointAttributes)
        updatePathAttributes = {
          updateFeatures: [{
            attributes: {
              ObjectID: ActiveWaypointObjID,
            },
            geometry : {
              type: "polyline",
              paths: [
                [FlightPathPointsLon.slice(-2)[0], FlightPathPointsLat.slice(-2)[0], WaypointHeights[WaypointHeights.length-2]],
                [lon, lat, HeightInput],
              ]
          }
          }]
        }
        FlightPath.applyEdits(updatePathAttributes)
        previousHeight = HeightInput
      }
    });
      
      

    // Click event handler for Flight Path menu: 
    //    - Add Flight Path
    //    - Delete Flight Path
    //    - Edit Flight Path
    addFlightPathEnabled = false
    document.getElementById("FlightPath").addEventListener("click", (event) => {
      const FlightPathButton = event.target.getAttribute("data-FlightPath-button"); 
      // Add Flight Path
      if (FlightPathButton == "Add") {
        addFlightPathEnabled = !addFlightPathEnabled
      }
      // Delete Flight Path
      if (FlightPathButton == "Delete") {
        FlightPathPoints.queryFeatures({
          where: "1=1",
          outFields: ["*"],
          returnGeometry: true
        }).then((results) => {
          if (results.features.length > 0) {
            const deleteEdits = results.features
            FlightPathPoints.applyEdits({
              deleteFeatures: deleteEdits
            })
          }
        });
        FlightPath.queryFeatures({
          where: "1=1",
          outFields: ["*"],
          returnGeometry: true
        }).then((results) => {
          if (results.features.length > 0) {
            const deleteEdits = results.features
            FlightPath.applyEdits({
              deleteFeatures: deleteEdits
            })
          }
        });
        FlightPathPointsLon = []
        FlightPathPointsLat = []
        PathFeatureLayerCreated = false
        WaypointsFeatureLayerCreated = false
      }
      // Edit Flight Path
      if (FlightPathButton == "Edit") {
      }
      // Change style of the Flight Path Menu Buttons
      if (!(FlightPathButton == "Delete")) {
        element = document.querySelectorAll("div.FlightPath-item[data-FlightPath-button='"+FlightPathButton+"']");
        if (document.getElementById(element[0].id).style.backgroundColor == "grey"){
          document.getElementById(element[0].id).style.backgroundColor = "black"
        }  else{
          document.getElementById(element[0].id).style.backgroundColor = "grey"
        }
      }
    });


    // Edit Flight Path Function
    appConfig.activeView.on("layerview-create", (event) => {
      if (event.layer.id === "WaypointsFL") {
        appConfig.activeView.on("click", (event) => {
          // Only include graphics from Waypoints FeatureLayer
          const opts = {
            include: FlightPathPoints
          }
          appConfig.activeView.hitTest(event, opts).then((response) => {
            // check if a feature is returned from the WaypointsLayer
            if (response.results.length) {
              const graphic = response.results[0].graphic;
              console.log(graphic)
            }
          });
        });
      }
    });

    const FlightPathExpand = new Expand({
      view: appConfig.activeView,
      content: document.getElementById("FlightPath"),
      expandIconClass: "esri-icon-polyline",
      title: "FlightPath",
    });


    const PathProfileExpand = new Expand({
      view: appConfig.activeView,
      content: document.getElementById("PathProfile"),
      expandIconClass: "esri-icon-elevation-profile",
      title: "PathProfile",
    });
    
    const elevationProfile2 = new ElevationProfile({
    container: "ElevationDiv",
    view: appConfig.activeView,
    //input: FlightPath.source,
    profiles: [{
        // displays elevation values from Map.ground
        type: "ground", //autocasts as new ElevationProfileLineGround()
        color: "#61d4a4",
        title: "Ground elevation"
    }, {
        // displays elevation values from the input line graphic
        type: "input", //autocasts as new ElevationProfileLineInput()
        color: "#f57e42",
        title: "Line elevation"
    }, /*{
        // displays elevation values from a SceneView
        type: "view", //autocasts as new ElevationProfileLineView()
        color: "#8f61d4",
        title: "View elevation",
        // by default ground and all layers are used to compute elevation, but
        // you can define which elements should be included/excluded from the computation
        //exclude: [map.ground]
    }*/]
  });
  

    
      

    // Add Legend to active View
    const legend = new Legend({view: appConfig.activeView});
    

    // Home Button Initialization
    const homeBtn = new Home({
      view: appConfig.activeView
    });
    appConfig.activeView.ui.add(homeBtn, "top-left");


    // Basemape Widget Initialization
    const basemapGallery = new BasemapGallery({
      view: appConfig.activeView,
      container: document.getElementById("BasemapGallery")
    });

    const BasemapExpand = new Expand({
      view: appConfig.activeView,
      content: document.getElementById("BasemapGallery"),
      expandIconClass: "esri-icon-basemap",
      title: "Basemap",
    });

    // close the expand whenever a basemap is selected
    basemapGallery.watch("activeBasemap", () => {
      const mobileSize =
        appConfig.activeView.heightBreakpoint === "xsmall" ||
        appConfig.activeView.widthBreakpoint === "xsmall";
      BasemapExpand.collapse();
    });

    // Add the expand instance to the View
    appConfig.activeView.ui.add(BasemapExpand, "top-left");


    // Time Slider widget initialization (!!Not Working in the current Prototype!!)
    /*const timeSlider = new TimeSlider({
      container: "timeSlider",
      viewModel: {
        view: appConfig.activeView,
        mode: "instant",
        fullTimeExtent: {
          start: new Date(2022, 01, 03),
          end: new Date(2022, 01, 04)
        },
        timeExtent: {
          start: new Date("2022-02-03T05:00"),
          end: new Date("2022-02-03T05:00")
        }
      }
      //timeVisible: true, // show the time stamps on the timeslider
      //loop: true
    });
    // Add hourly intervals starting from the beginning of the TimeSlider.
    timeSlider.stops = {
      interval: {
        value: 1,
        unit: "hours"
      }
    };
    //appConfig.activeView.ui.add(timeSlider, "bottom-leading");
    
    var options = {year: 'numeric', month: 'numeric', day: 'numeric' };
    timeExtentStart = timeSlider.timeExtent.start
    let formatted_date = timeExtentStart.getDate() + "." + (timeExtentStart.getMonth() + 1) + "." + timeExtentStart.getFullYear() + " " + timeExtentStart.getHours()+":00:00"

    //console.log("Time '"+ timeSlider.timeExtent.start.getDay()+"."+timeSlider.timeExtent.start.getMonth()+"."+timeSlider.timeExtent.start.getYear()+"."+timeSlider.timeExtent.start.getHours()+"'")
    //console.log("Time '"+ formatted_date+"'")
    //console.log("Time Attribute: ", CloudLayer.getField("time"))

    timeSlider.watch("timeExtent", () => {
      if (activeCloudLayerView) { 
        activeCloudLayerView.filter = {
          //where: "time IN (TIMESTAMP '02/03/2022 07:00:00')",
          where: "time = TIMESTAMP '2022-02-03 06:00:00'",
          //where: "time = DATE '2022-02-03'",
          //where: "CloudClassification = 8",
          //timeExtent: timeSlider.timeExtent
        }
      }
    });*/
    

  
    
    // Assign Checkbox objects to variables
    const CLCLayerToggle = document.getElementById("CLCLayer");
    const HorizontalWindLayerToggle = document.getElementById("HorizontalWindLayer")
    const VerticalWindLayerToggle = document.getElementById("VerticalWindLayer")
    const ThunderstormLayerToggle = document.getElementById("ThunderstormLayer")
    const IcingLayerToggle = document.getElementById("IcingLayer")


    // Change Layer Visibility when checkbox is activated/deactivated
    CLCLayerToggle.addEventListener("change", () => {
      if (activeCloudLayer) {
        activeCloudLayer.visible = CLCLayerToggle.checked;  // If Checkbox is activated --> Visibility = True
        if ((activeCloudLayer.portalItem.id == empty_layer_id) & CLCLayerToggle.checked){
          addWarning(activeCloudLayer)
        }
        else if ((activeCloudLayer.portalItem.id == empty_layer_id) & !CLCLayerToggle.checked){
          deleteWarning(activeCloudLayer)
        }
      }
    });
    HorizontalWindLayerToggle.addEventListener("change", () => {
      if (activeHorizontalWindLayer) {
        activeHorizontalWindLayer.visible = HorizontalWindLayerToggle.checked;  // If Checkbox is activated --> Visibility = True
        if ((activeHorizontalWindLayer.portalItem.id == empty_layer_id) & HorizontalWindLayerToggle.checked){
          addWarning(activeHorizontalWindLayer)
        }
        else if ((activeHorizontalWindLayer.portalItem.id == empty_layer_id) & !HorizontalWindLayerToggle.checked){
          deleteWarning(activeHorizontalWindLayer)
        }
      }
    });
    VerticalWindLayerToggle.addEventListener("change", () => {
      if (activeVerticalWindLayer) {
        activeVerticalWindLayer.visible = VerticalWindLayerToggle.checked;  // If Checkbox is activated --> Visibility = True
        if ((activeVerticalWindLayer.portalItem.id == empty_layer_id) & VerticalWindLayerToggle.checked){
          addWarning(activeVerticalWindLayer)
        }
        else if ((activeVerticalWindLayer.portalItem.id == empty_layer_id) & !VerticalWindLayerToggle.checked){
          deleteWarning(activeVerticalWindLayer)
        }
      }
    });
    ThunderstormLayerToggle.addEventListener("change", () => {
      if (activeThunderstormLayer) {
        activeThunderstormLayer.visible = ThunderstormLayerToggle.checked;  // If Checkbox is activated --> Visibility = True
        if ((activeThunderstormLayer.portalItem.id == empty_layer_id) & ThunderstormLayerToggle.checked){
          addWarning(activeThunderstormLayer)
        }
        else if ((activeThunderstormLayer.portalItem.id == empty_layer_id) & !ThunderstormLayerToggle.checked){
          deleteWarning(activeThunderstormLayer)
        }
      }
    });
    IcingLayerToggle.addEventListener("change", () => {
      if (activeIcingLayer) {
        activeIcingLayer.visible = IcingLayerToggle.checked;  // If Checkbox is activated --> Visibility = True
        if ((activeIcingLayer.portalItem.id == empty_layer_id) & IcingLayerToggle.checked){
          addWarning(activeIcingLayer)
        }
        else if ((activeIcingLayer.portalItem.id == empty_layer_id) & !IcingLayerToggle.checked){
          deleteWarning(activeIcingLayer)
        }
      }
    });

    // Add Expand object to accomodate Layer Checkboxes 
    layerListExpand = new Expand({
      expandIconClass: "esri-icon-layers",  
      title: "Layers",
      view: appConfig.activeView,
      content: document.getElementById("layerToggle")
    });
    
    



    // Cloud Classification Filter
    const CloudFilterExpand = new Expand({
      view: appConfig.activeView,
      content: document.getElementById("LayerFilter"),
      expandIconClass: "esri-icon-filter",
      group: "top-right"
    });

    // Click event handler for Filter Reset
    var ResetFilters = false
    document.getElementById("LayerFilterReset").addEventListener("change", () => {
      ResetFilters = document.getElementById("LayerFilterReset").checked;  // If Checkbox is activated --> Reset Filters when expand closed
    });
    

    // Click event handler for Cloud Filter choices
    document.getElementById("cloudsFilterWrapper").addEventListener("click", filterCloudValues);

    // Cloud Filter Event Handler Function
    let cloudFilterArray = [];
    let reset = false;
    function filterCloudValues(event) {
      const selectedCloudClassification = event.target.getAttribute("data-cloud-classification");   // Get Okta Value from current Click on Cloud Filter Div

      // Add Okta Value to List with all Filter Values if not already included. Otherwise the Value is removed from the array.
      if (!(cloudFilterArray.includes(selectedCloudClassification))) {
        cloudFilterArray.push(selectedCloudClassification)            
      } 
      else {
        reset = true
        for( var i = 0; i <= cloudFilterArray.length; i++){                      
          if ( cloudFilterArray[i] === selectedCloudClassification) { 
              cloudFilterArray.splice(i, 1); 
              i--; 
          }
        }
      }
      // Check for null values in Filter Array. If true delete null values.
      for( var i = 0; i <= cloudFilterArray.length; i++){                      
        if ( cloudFilterArray[i] === null) { 
            cloudFilterArray.splice(i, 1); 
            i--; 
        }
      }
      // Refresh Filter Query in CloudLayerView with updated Filter Values
      if (activeCloudLayerView) {
        if (activeCloudLayerView.filter) {
          let filter_clone = activeCloudLayerView.filter.clone()
          filter_clone.where = "CloudClassification IN ("+cloudFilterArray+")" 
          activeCloudLayerView.filter = filter_clone
        } else {
          activeCloudLayerView.filter = {
              where: "CloudClassification IN ("+cloudFilterArray+")"    
          }
        } 
      }
      // Clicked filter value background color reset, if previously selected.
      if (reset) {
        element = document.querySelectorAll("div.cloud-item[data-cloud-classification='"+selectedCloudClassification+"']");
        document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of clicked elements to black
        reset = false                
      }
      // Set background color to grey for selected filter values
      cloudFilterArray.forEach(item => {
        element = document.querySelectorAll("div.cloud-item[data-cloud-classification='"+item+"']");  // Get every active div Filter element 
        if (element.length > 0) {
          document.getElementById(element[0].id).style.backgroundColor = "grey"                         // Change Background color of active filter element
        }
      });
      // FilterWarning function call
      FilterWarning()
    }
    // Cloud Filter Reset when Expand is closed
    CloudFilterExpand.watch("expanded", () => {
      if (!CloudFilterExpand.expanded & ResetFilters) {
        activeCloudLayerView.filter = null;
        cloudFilterArray.forEach(item => {
          element = document.querySelectorAll("div.cloud-item[data-cloud-classification='"+item+"']");
          document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of Filter elements to black                
        });
        cloudFilterArray = [];
      }
    });


    // Click event handler for VerticalWind Filter choices
    document.getElementById("verticalWindFilterWrapper").addEventListener("click", filterVerticalWindValues);

    // Vertical Wind Filter Event Handler Function
    let VerticalWindFilterArray = [];
    let resetVerticalWindFilter = false;
    function filterVerticalWindValues(event) {
      const selectedVerticalWindLevel = event.target.getAttribute("data-vertical-layer");   // Get Layer Number from current Click on VerticalWind Filter Div

      // Add VerticalWind Level to List with all Filter Values if not already included. Otherwise the Value is removed from the array.
      if (!(VerticalWindFilterArray.includes(selectedVerticalWindLevel))) {
        VerticalWindFilterArray.push(selectedVerticalWindLevel)            
      } 
      else {
        resetVerticalWindFilter = true
        for( var i = 0; i <= VerticalWindFilterArray.length; i++){                      
          if ( VerticalWindFilterArray[i] === selectedVerticalWindLevel) { 
              VerticalWindFilterArray.splice(i, 1); 
              i--; 
          }
        }
      }
      // Check for null values in Filter Array. If true delete null values.
      for( var i = 0; i <= VerticalWindFilterArray.length; i++){                      
        if ( VerticalWindFilterArray[i] === null) { 
            VerticalWindFilterArray.splice(i, 1); 
            i--; 
        }
      }
      // Refresh Filter Query in VerticalWindLayerView with updated Filter Values
      if (activeVerticalWindLayerView) {
        if (activeVerticalWindLayerView.filter) {
          let filter_clone = activeVerticalWindLayerView.filter.clone()
          filter_clone.where = "LayerLevel IN ("+VerticalWindFilterArray+")" 
          activeVerticalWindLayerView.filter = filter_clone
        } else {
          activeVerticalWindLayerView.filter = {
              where: "LayerLevel IN ("+VerticalWindFilterArray+")"    
          }
        }
      }
      if (activeHorizontalWindLayerView) {
        if (activeHorizontalWindLayerView.filter) {
          let filter_clone = activeHorizontalWindLayerView.filter.clone()
          filter_clone.where = "LayerLevel IN ("+VerticalWindFilterArray+")" 
          activeHorizontalWindLayerView.filter = filter_clone
        } else {
          activeHorizontalWindLayerView.filter = {
              where: "LayerLevel IN ("+VerticalWindFilterArray+")"    
          }
        }
      }
      // Clicked filter value background color reset, if previously selected.
      if (resetVerticalWindFilter) {
        element = document.querySelectorAll("div.verticalWind-item[data-vertical-layer='"+selectedVerticalWindLevel+"']");
        document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of clicked elements to black
        resetVerticalWindFilter = false                
      }
      // Set background color to grey for selected filter values
      VerticalWindFilterArray.forEach(item => {
        element = document.querySelectorAll("div.verticalWind-item[data-vertical-layer='"+item+"']");  // Get every active div Filter element 
        if (element.length > 0) {
          document.getElementById(element[0].id).style.backgroundColor = "grey"                         // Change Background color of active filter element
        }
      });
      // FilterWarning function call
      FilterWarning()

    }
    // VerticalWind Filter Reset when Expand is closed
    CloudFilterExpand.watch("expanded", () => {
      if (!CloudFilterExpand.expanded & ResetFilters) {
        activeVerticalWindLayerView.filter = null;
        activeHorizontalWindLayerView.filter = null;
        VerticalWindFilterArray.forEach(item => {
          element = document.querySelectorAll("div.verticalWind-item[data-vertical-layer='"+item+"']");
          document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of Filter elements to black                
        });
        VerticalWindFilterArray = [];
      }
    });


    // Click event handler for Thunderstorm Filter choices
    document.getElementById("ThunderstormFilterWrapper").addEventListener("click", filterThunderstormValues);

    // Thunderstorm Filter Event Handler Function
    let ThunderstormFilterArray = [];
    let resetThunderstormFilter = false;
    function filterThunderstormValues(event) {
      const selectedThunderstormClassification = event.target.getAttribute("data-thunderstorm-classification");   // Get Thunderstorm Filter Value from current Click on Thunderstorm Filter Div

      // Add Thunderstorm Classification Value to List with all Filter Values if not already included. Otherwise the Value is removed from the array.
      if (!(ThunderstormFilterArray.includes(selectedThunderstormClassification))) {
        ThunderstormFilterArray.push(selectedThunderstormClassification)            
      } 
      else {
        resetThunderstormFilter = true
        for( var i = 0; i <= ThunderstormFilterArray.length; i++){                      
          if ( ThunderstormFilterArray[i] === selectedThunderstormClassification) { 
              ThunderstormFilterArray.splice(i, 1); 
              i--; 
          }
        }
      }
      // Check for null values in Filter Array. If true delete null values.
      for( var i = 0; i <= ThunderstormFilterArray.length; i++){                      
        if ( ThunderstormFilterArray[i] === null) { 
            ThunderstormFilterArray.splice(i, 1); 
            i--; 
        }
      }
      // Refresh Filter Query in ThunderstormLayerView with updated Filter Values
      if (activeThunderstormLayerView) {
        if (activeThunderstormLayerView.filter) {
          let filter_clone = activeThunderstormLayerView.filter.clone()
          filter_clone.where = "StormClassification IN ("+ThunderstormFilterArray+")" 
          activeThunderstormLayerView.filter = filter_clone
        } else {
            activeThunderstormLayerView.filter = {
              where: "StormClassification IN ("+ThunderstormFilterArray+")"    
          }
        }
      }
      // Clicked filter value background color reset, if previously selected.
      if (resetThunderstormFilter) {
        element = document.querySelectorAll("div.thunderstorm-item[data-thunderstorm-classification='"+selectedThunderstormClassification+"']");
        document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of clicked elements to black
        resetThunderstormFilter = false                
      }
      // Set background color to grey for selected filter values
      ThunderstormFilterArray.forEach(item => {
        element = document.querySelectorAll("div.thunderstorm-item[data-thunderstorm-classification='"+item+"']");  // Get every active div Filter element 
        if (element.length > 0) {
          document.getElementById(element[0].id).style.backgroundColor = "grey"                         // Change Background color of active filter element
        }
      });

      // FilterWarning function call
      FilterWarning()

    }
    // VerticalWind Filter Reset when Expand is closed
    CloudFilterExpand.watch("expanded", () => {
      if (!CloudFilterExpand.expanded & ResetFilters) {
        activeThunderstormLayerView.filter = null;
        ThunderstormFilterArray.forEach(item => {
          element = document.querySelectorAll("div.thunderstorm-item[data-thunderstorm-classification='"+item+"']");
          document.getElementById(element[0].id).style.backgroundColor = "black"  // Reset Background Color of Filter elements to black                
        });
        ThunderstormFilterArray = [];
      }
    });

    function FilterWarning() {
      let FilterCounter = 0

      if (document.getElementById("CloudLayerViewFilter").checked || document.getElementById("HorizontalWindLayerViewFilter").checked || document.getElementById("VerticalWindLayerViewFilter").checked ||
          document.getElementById("ThunderstormLayerViewFilter").checked || document.getElementById("IcingLayerViewFilter").checked){
          FilterCounter += 1
      }
      if (activeCloudLayerView){
        let CloudLayerViewFilterObj = activeCloudLayerView.filter;
        if (CloudLayerViewFilterObj) {
          if (CloudLayerViewFilterObj.hasOwnProperty("where")) {
            if (!(activeCloudLayerView.filter.where == "CloudClassification IN ()")){
              FilterCounter += 1
            }
          }
        }
      }
      if (activeThunderstormLayerView){
        let ThunderstormLayerViewFilterObj = activeThunderstormLayerView.filter;
        if (ThunderstormLayerViewFilterObj) {
          if (ThunderstormLayerViewFilterObj.hasOwnProperty("where")) {
            if (!(activeThunderstormLayerView.filter.where == "StormClassification IN ()")){
              FilterCounter += 1
            }
          }
        }
      }
      if (activeHorizontalWindLayerView){
        let HorizontalWindLayerViewFilterObj = activeHorizontalWindLayerView.filter;
        if (HorizontalWindLayerViewFilterObj) {
          if (HorizontalWindLayerViewFilterObj.hasOwnProperty("where")) {
            if (!(activeHorizontalWindLayerView.filter.where == "LayerLevel IN ()")){
              FilterCounter += 1
            }
          }
        }
      } 
      if (activeVerticalWindLayerView){
        let VerticalWindLayerViewFilterObj = activeVerticalWindLayerView.filter;
        if (VerticalWindLayerViewFilterObj) {
          if (VerticalWindLayerViewFilterObj.hasOwnProperty("where")) {
            if (!(activeVerticalWindLayerView.filter.where == "LayerLevel IN ()")){
              FilterCounter += 1
            }
          }
        }
      }
      if (FilterCounter >0){
        document.getElementById("FilterWarningDiv").style.visibility = "visible"
      } else {
        document.getElementById("FilterWarningDiv").style.visibility = "hidden"
      }
    };


    // Blinking symbols
    window.setInterval(updateRenderer, 2000)
    
    lastState = false;
    function updateRenderer() {
      if (activeIcingLayer & activeThunderstormLayer) {
        renderer_icing = activeIcingLayer.renderer.clone();
        renderer_thunderstorm = activeThunderstormLayer.renderer.clone();
        color_icing = renderer_icing.symbol.symbolLayers.items[0];
        color_thunderstorm_verystrong = renderer_thunderstorm.classBreakInfos[3];
        color_thunderstorm_extreme = renderer_thunderstorm.classBreakInfos[4];
        if (lastState) {
          color_icing.material.color = "rgba(250, 250, 5, .35)";
          color_thunderstorm_verystrong.symbol.symbolLayers.items[0].material.color = "rgba(250, 151, 2, .15)";
          color_thunderstorm_extreme.symbol.symbolLayers.items[0].material.color = "rgba(250, 2, 2, .15)";
        } else {
          color_icing.material.color = "rgba(250, 250, 5, 1)";
          color_thunderstorm_verystrong.symbol.symbolLayers.items[0].material.color = "rgba(250, 151, 2, .55)";
          color_thunderstorm_extreme.symbol.symbolLayers.items[0].material.color = "rgba(250, 2, 2, .8)";
        }
        activeIcingLayer.renderer = renderer_icing;
        if (activeThunderstormLayerView) {
          if (activeThunderstormLayerView.filter) {
            thunderstorm_where = activeThunderstormLayerView.filter.where
            /*if ((thunderstorm_where == "StormClassification IN (3)") || (thunderstorm_where == "StormClassification IN (4)") ||
                (thunderstorm_where == "StormClassification IN (3,4)") || (thunderstorm_where == "StormClassification IN (4,3)")) {*/
              if ((thunderstorm_where.search("3") != -1) || (thunderstorm_where.search("4") != -1)) {
                activeThunderstormLayer.renderer = renderer_thunderstorm;
              }
          }
        }
        
        lastState = !lastState
      }
    }

   
    const PreferencesExpand = new Expand({
      view: appConfig.activeView,
      expandIconClass: "esri-icon-settings",
      content: document.getElementById("PreferencesDiv"),
      title: "Preferences",
    });



    // Info Div about the 3D-SigWX Webapp
    const InfoExpand = new Expand({
      view: appConfig.activeView,
      expandIconClass: "esri-icon-description",
      title: "3DSIGWXInfo",
    });

    // Search Widget
    const searchWidget = new Search({
      view: appConfig.activeView,
    });

    // Add Widget expand instances to the View
    appConfig.activeView.ui.add(searchWidget, {position: "top-right"});
    appConfig.activeView.ui.add(layerListExpand, "top-right");
    appConfig.activeView.ui.add(CloudFilterExpand, "top-right");
    appConfig.activeView.ui.add(FlightPathExpand, "top-right");
    appConfig.activeView.ui.add(PathProfileExpand, "top-right");
    appConfig.activeView.ui.add(PreferencesExpand, "top-right");
    appConfig.activeView.ui.add(InfoExpand, "bottom-right");
    appConfig.activeView.ui.add(legend, "bottom-right");

    appConfig.activeView.ui.add(document.getElementById("WebappHeader", "manual"))
    appConfig.activeView.ui.add(document.getElementById("DateDiv", "manual"))
    appConfig.activeView.ui.add(document.getElementById("TimeDiv", "manual"))
    appConfig.activeView.ui.add(document.getElementById("TimeStops", "manual"))
    appConfig.activeView.ui.add(document.getElementById("WarningDiv", "manual"))
    appConfig.activeView.ui.add(document.getElementById("TimeWarningDiv", "manual"))
    appConfig.activeView.ui.add(document.getElementById("FilterWarningDiv", "manual"))
    

});
