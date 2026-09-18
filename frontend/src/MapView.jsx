import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";


function createNumberIcon(number) {
  return L.divIcon({
    className: "number-marker",
    html: `<div>${number}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
}


function FitBounds({ pois }) {
  const map = useMap();

  useEffect(() => {
    if (!pois || pois.length === 0) return;

    const bounds = pois.map((poi) => [
      poi.lat,
      poi.lon,
    ]);

    map.fitBounds(bounds, {
      padding: [40, 40],
    });

  }, [pois, map]);

  return null;
}


function RoadRoute({ pois, setRoute }) {

  useEffect(() => {

    if (!pois || pois.length < 2) {
      return;
    }

    const getRoute = async () => {

      try {

        // OSRM expects:
        // longitude,latitude;longitude,latitude

        const coordinates = pois
          .map((poi) => `${poi.lon},${poi.lat}`)
          .join(";");


        const url =
          `https://router.project-osrm.org/route/v1/driving/${coordinates}` +
          `?overview=full&geometries=geojson`;


        const response = await fetch(url);

        if (!response.ok) {
          throw new Error("Routing service failed");
        }


        const data = await response.json();


        if (
          data.code === "Ok" &&
          data.routes &&
          data.routes.length > 0
        ) {

          const route =
            data.routes[0].geometry.coordinates.map(
              ([lon, lat]) => [lat, lon]
            );

          setRoute(route);

        }

      } catch (error) {

        console.error(
          "Unable to get road route:",
          error
        );

        // Fallback to straight-line route
        setRoute(
          pois.map((poi) => [
            poi.lat,
            poi.lon,
          ])
        );
      }
    };


    getRoute();

  }, [pois, setRoute]);


  return null;
}


function MapView({ pois = [] }) {

  const [route, setRoute] = useState([]);


  const defaultCenter = [
    31.2304,
    121.4737,
  ];


  const center =
    pois.length > 0
      ? [pois[0].lat, pois[0].lon]
      : defaultCenter;


  return (

    <div className="map-container">

      <MapContainer
        center={center}
        zoom={12}
        scrollWheelZoom={true}
        style={{
          width: "100%",
          height: "500px",
        }}
      >

        <TileLayer
  attribution='&copy; OpenStreetMap contributors'
  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
/>

        <FitBounds pois={pois} />


        {/* GET ACTUAL ROAD ROUTE */}

        <RoadRoute
          pois={pois}
          setRoute={setRoute}
        />


        {/* ROAD ROUTE */}

        {route.length > 1 && (

          <Polyline
            positions={route}
            pathOptions={{
              color: "#2563eb",
              weight: 5,
              opacity: 0.85,
            }}
          />

        )}


        {/* NUMBERED POI MARKERS */}

        {pois.map((poi, index) => (

          <Marker
            key={poi.id || index}
            position={[
              poi.lat,
              poi.lon,
            ]}
            icon={createNumberIcon(index + 1)}
          >

            <Popup>

              <div>

                <strong>
                  {index + 1}. {poi.name}
                </strong>

                <p>
                  {poi.description}
                </p>

              </div>

            </Popup>

          </Marker>

        ))}

      </MapContainer>

    </div>
  );
}


export default MapView;