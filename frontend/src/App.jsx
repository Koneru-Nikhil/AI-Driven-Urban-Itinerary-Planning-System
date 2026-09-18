import { useState } from "react";
import "./App.css";
import MapView from "./MapView";


// ============================================================
// DEMO FALLBACK DATA
// Used when Gemini API is unavailable / quota exceeded
// ============================================================

const demoShanghaiResult = {
  success: true,

  itinerary:
    "Shanghai Postal Museum -> Waibaidu Bridge -> Shanghai Peace Hotel -> The Bund -> Wu Zhong Market -> Yuyuan Road -> M50 Art District",

  overall_reason:
    "This curated itinerary offers an enchanting blend of historic landmarks, vibrant culinary culture, and avant-garde art across Shanghai.",

  pois: [
    {
      order: 1,
      id: "7977",
      name: "Shanghai Postal Museum",
      lat: 31.2443923087,
      lon: 121.4848007947,
      description:
        "Explore the historic Shanghai Postal Museum and discover the city's rich communication and architectural heritage."
    },

    {
      order: 2,
      id: "12973",
      name: "Waibaidu Bridge",
      lat: 31.2433137205,
      lon: 121.4901655755,
      description:
        "Visit the iconic Waibaidu Bridge, a historic steel bridge offering beautiful views of the Suzhou Creek and Shanghai skyline."
    },

    {
      order: 3,
      id: "13094",
      name: "Shanghai Peace Hotel",
      lat: 31.2392035526,
      lon: 121.4891282174,
      description:
        "Experience the historic Peace Hotel and its famous Art Deco architecture, reflecting the glamour of old Shanghai."
    },

    {
      order: 4,
      id: "12959",
      name: "The Bund",
      lat: 31.2377704249,
      lon: 121.4906033011,
      description:
        "Walk along The Bund and admire its historic European-style buildings alongside the modern Pudong skyline."
    },

    {
      order: 5,
      id: "13208",
      name: "Wu Zhong Market",
      lat: 31.2113226173,
      lon: 121.4463725345,
      description:
        "Explore Wu Zhong Market for an authentic local food experience and a taste of Shanghai's everyday culinary culture."
    },

    {
      order: 6,
      id: "13048",
      name: "Yuyuan Road",
      lat: 31.2252752103,
      lon: 121.4473996046,
      description:
        "Walk along historic Yuyuan Road, known for its local atmosphere, shops, cafes and restaurants."
    },

    {
      order: 7,
      id: "13991",
      name: "M50 Art District",
      lat: 31.2481310296,
      lon: 121.4493668872,
      description:
        "Explore M50 Art District, a creative area filled with contemporary galleries, street art and converted industrial spaces."
    }
  ]
};


function App() {

  const [city, setCity] = useState("shanghai");

  const [interests, setInterests] = useState("");

  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);

  const [error, setError] = useState("");

  const [demoMode, setDemoMode] = useState(false);


  // ============================================================
  // Generate itinerary
  // ============================================================

  const generateItinerary = async () => {

    if (!interests.trim()) {

      setError("Please enter your interests.");

      return;
    }


    setLoading(true);

    setError("");

    setResult(null);

    setDemoMode(false);


    try {

      // --------------------------------------------------------
      // Call Flask API
      // --------------------------------------------------------

      const response = await fetch(
        "http://127.0.0.1:5000/api/generate",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            city: city,

            query:
              `I am interested in ${interests}. ` +
              `Plan a one day itinerary.`,
          }),
        }
      );


      const data = await response.json();


      // --------------------------------------------------------
      // API SUCCESS
      // --------------------------------------------------------

      if (response.ok && data.success) {

        setResult(data);

        return;
      }


      // --------------------------------------------------------
      // API FAILED
      // Use local demo fallback
      // --------------------------------------------------------

      console.warn(
        "Gemini/API unavailable. Using demo itinerary.",
        data.error
      );


      if (city === "shanghai") {

        setResult(demoShanghaiResult);

        setDemoMode(true);

      } else {

        throw new Error(
          data.error ||
          "Failed to generate itinerary."
        );
      }


    } catch (err) {

      console.error(err);


      // --------------------------------------------------------
      // Network error / Gemini error
      // --------------------------------------------------------

      if (city === "shanghai") {

        console.warn(
          "Using Shanghai demo itinerary."
        );


        setResult(demoShanghaiResult);

        setDemoMode(true);

        setError("");

      } else {

        setError(
          err.message ||
          "Unable to connect to the ITINERA API."
        );
      }


    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="app">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="header">

        <h1>
          AI Urban Itinerary Planner
        </h1>

        <p>
          Personalized travel planning powered by ITINERA
        </p>

      </header>


      <main className="container">


        {/* ====================================================
            INPUT CARD
        ==================================================== */}

        <section className="input-card">

          <h2>
            Plan Your Trip
          </h2>


          {/* DESTINATION */}

          <label>
            Destination
          </label>


          <select
            value={city}
            onChange={(e) =>
              setCity(e.target.value)
            }
          >

            <option value="shanghai">
              Shanghai
            </option>

            <option value="beijing">
              Beijing
            </option>

            <option value="hangzhou">
              Hangzhou
            </option>

            <option value="qingdao">
              Qingdao
            </option>

            <option value="shenzhen">
              Shenzhen
            </option>

            <option value="changsha">
              Changsha
            </option>

            <option value="wuhan">
              Wuhan
            </option>

          </select>


          {/* INTERESTS */}

          <label>
            Interests
          </label>


          <textarea
            value={interests}
            onChange={(e) =>
              setInterests(e.target.value)
            }
            placeholder="Example: history, art, restaurants, shopping..."
          />


          {/* GENERATE BUTTON */}

          <button
            onClick={generateItinerary}
            disabled={loading}
          >

            {loading
              ? "Generating..."
              : "Generate Itinerary"}

          </button>


          {/* ERROR */}

          {error && (

            <div className="error">

              {error}

            </div>

          )}

        </section>


        {/* ====================================================
            RESULTS
        ==================================================== */}

        {result && (

          <section className="results">


            {/* =================================================
                DEMO NOTICE
            ================================================= */}

            {demoMode && (

              <div
                style={{
                  background: "#fff7ed",
                  border: "1px solid #fed7aa",
                  color: "#9a3412",
                  padding: "12px 16px",
                  borderRadius: "10px",
                  marginBottom: "20px",
                  textAlign: "center",
                  fontSize: "14px",
                }}
              >

                <strong>
                  Demo Mode
                </strong>

                <br />

                Showing a previously generated ITINERA
                itinerary because the AI service is
                temporarily unavailable.

              </div>

            )}


            {/* =================================================
                MAP
            ================================================= */}

            <div className="map-card">

              <h2>
                🗺️ Your Route
              </h2>


              <MapView
                pois={result.pois}
              />

            </div>


            {/* =================================================
                SUMMARY
            ================================================= */}

            <div className="result-header">

              <h2>
                Your Itinerary
              </h2>


              <p>
                {result.overall_reason}
              </p>

            </div>


            {/* =================================================
                ROUTE SUMMARY
            ================================================= */}

            <div className="route-summary">

              <strong>
                Route
              </strong>


              <span>
                {result.itinerary}
              </span>

            </div>


            {/* =================================================
                POI LIST
            ================================================= */}

            <div className="itinerary-list">

              {result.pois.map(
                (poi, index) => (

                  <div
                    className="poi-card"
                    key={poi.id || index}
                  >


                    {/* NUMBER */}

                    <div className="poi-number">

                      {index + 1}

                    </div>


                    {/* CONTENT */}

                    <div className="poi-content">

                      <h3>
                        {poi.name}
                      </h3>


                      <p>
                        {poi.description}
                      </p>


                      <span>

                        📍{" "}
                        {Number(poi.lat).toFixed(5)}
                        {", "}
                        {Number(poi.lon).toFixed(5)}

                      </span>

                    </div>

                  </div>

                )
              )}

            </div>

          </section>

        )}

      </main>

    </div>

  );
}


export default App;