require(["esri/request", "esri/portal/Portal", "esri/portal/PortalQueryParams"],
    function(esriRequest, Portal, PortalQueryParams){
      
      LayerRegex = {
          Clouds_05UTC: new RegExp('Clouds_05UTC'),
          Clouds_08UTC: new RegExp('Clouds_08UTC'),
          Clouds_11UTC: new RegExp('Clouds_11UTC'),
          Clouds_14UTC: new RegExp('Clouds_14UTC'),
          Clouds_17UTC: new RegExp('Clouds_17UTC'),

          Thunderstorm_05UTC: new RegExp('Thunderstorm_05UTC'),
          Thunderstorm_08UTC: new RegExp('Thunderstorm_08UTC'),
          Thunderstorm_11UTC: new RegExp('Thunderstorm_11UTC'),
          Thunderstorm_14UTC: new RegExp('Thunderstorm_14UTC'),
          Thunderstorm_17UTC: new RegExp('Thunderstorm_17UTC'),

          HorizontalWind_05UTC: new RegExp('HorizontalWind_05UTC'),
          HorizontalWind_08UTC: new RegExp('HorizontalWind_08UTC'),
          HorizontalWind_11UTC: new RegExp('HorizontalWind_11UTC'),
          HorizontalWind_14UTC: new RegExp('HorizontalWind_14UTC'),
          HorizontalWind_17UTC: new RegExp('HorizontalWind_17UTC'),

          VerticalWind_05UTC: new RegExp('VerticalWind_05UTC'),
          VerticalWind_08UTC: new RegExp('VerticalWind_08UTC'),
          VerticalWind_11UTC: new RegExp('VerticalWind_11UTC'),
          VerticalWind_14UTC: new RegExp('VerticalWind_14UTC'),
          VerticalWind_17UTC: new RegExp('VerticalWind_17UTC'),

          Icing_05UTC: new RegExp('Icing_05UTC'),
          Icing_08UTC: new RegExp('Icing_08UTC'),
          Icing_11UTC: new RegExp('Icing_11UTC'),
          Icing_14UTC: new RegExp('Icing_14UTC'),
          Icing_17UTC: new RegExp('Icing_17UTC'),
      };
      
      var LayerIDs = {};

      let theFile = "3DSIGWXconfig.yml"   
      

      var portal = new Portal("https://zhaw.maps.arcgis.com");
      portal.load().then(() => {
          const queryParams = new PortalQueryParams({
              query: "owner: tschatim_student AND type: Scene Service",
              //query: "tag: 3D-Sig WX AND type: Scene Service",
              sortField: "numViews",
              sortOrder: "desc",
              num: 100
            });
          portal.queryItems(queryParams).then((result) =>{
              let LayerNames = result.results
              LayerNames.forEach(item => {
                  for(var key in LayerRegex) {
                      var regex = LayerRegex[key];
                      if (regex.test(item.title)){
                          LayerIDs[key] = item.id
                      }
                  }
              })
          });
          this.LayerIDs = LayerIDs
          
      });

      // Request JSON data of ArcGIS Online Portal
      //let portal_url = "https://tiles.arcgis.com/tiles/9N9SahQkXAzBgwts/arcgis/rest/services/?f=pjson";   // URL to Organisation REST Services
      //let portal_url = "https://zhaw.maps.arcgis.com/sharing/rest/content/items/";   // URL to Organisation REST Services
      
      /*esriRequest(portal_url, {
        responseType: "json"
      }).then(function(response){
        // The requested data
        let PortalJSON = response.data;
        let LayerNames = PortalJSON.services
        LayerNames.forEach(item => {
          for(var key in LayerRegex) {
              var regex = LayerRegex[key];
              if (regex.test(item.name)){
                  LayerIDs[key] = item.serviceItemId
                  //console.log(item.serviceItemId)
              }
          }
        })
      });*/
  

      /*let PortalJSON = response.data;
        let LayerNames = PortalJSON.services
        LayerNames.forEach(item => {
            
          if (regex.test(item.name)){
            console.log(item.serviceItemId)
          }
          
        })*/
    },
)