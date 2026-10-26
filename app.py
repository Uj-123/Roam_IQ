import streamlit as st
import os
import json
import requests
from dotenv import load_dotenv
from google import genai


# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in .env file.")
    st.stop()


# Gemini client
client = genai.Client(api_key=api_key)


# -----------------------------------
# LIVE WEATHER
# -----------------------------------

def get_live_weather(destination):

    try:

        # Find destination coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": destination,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return None

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # Get live weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "relative_humidity_2m,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 3,
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_data = weather_response.json()

        return {
            "location": location,
            "country_code": location.get("country_code"),
            "current": weather_data["current"],
            "daily": weather_data["daily"]
        }


    except Exception:

        return None

def get_weather_description(code):
    weather_conditions = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌦️",
        53: "Moderate drizzle 🌦️",
        55: "Dense drizzle 🌧️",
        61: "Slight rain 🌦️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Light snow 🌨️",
        73: "Moderate snow 🌨️",
        75: "Heavy snow ❄️",
        80: "Rain showers 🌦️",
        81: "Moderate rain showers 🌧️",
        82: "Heavy rain showers ⛈️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with hail ⛈️",
        99: "Severe thunderstorm with hail ⛈️"
    }

    return weather_conditions.get(
        code,
        "Weather condition unavailable"
    )
# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="TripMate AI",
    page_icon="🌍",
    layout="wide"
)


# -----------------------------------
# LIVE CURRENCY
# -----------------------------------

def get_currency_rate(country_code):

    try:

        currency_map = {

            "US": ("USD", "$", "US Dollar"),

            "GB": ("GBP", "£", "British Pound"),

            "FR": ("EUR", "€", "Euro"),
            "DE": ("EUR", "€", "Euro"),
            "IT": ("EUR", "€", "Euro"),
            "ES": ("EUR", "€", "Euro"),

            "JP": ("JPY", "¥", "Japanese Yen"),

            "KR": ("KRW", "₩", "South Korean Won"),

            "CN": ("CNY", "¥", "Chinese Yuan"),

            "TH": ("THB", "฿", "Thai Baht"),

            "SG": ("SGD", "S$", "Singapore Dollar"),

            "AU": ("AUD", "A$", "Australian Dollar"),

            "CA": ("CAD", "C$", "Canadian Dollar"),

            "AE": ("AED", "د.إ", "UAE Dirham"),

            "CH": ("CHF", "CHF", "Swiss Franc"),

            "MY": ("MYR", "RM", "Malaysian Ringgit"),

            "ID": ("IDR", "Rp", "Indonesian Rupiah"),

            "VN": ("VND", "₫", "Vietnamese Dong"),

            "NP": ("NPR", "रू", "Nepalese Rupee")
        }


        if country_code not in currency_map:

            return None


        currency_code, symbol, currency_name = currency_map[country_code]


        url = (
            f"https://api.frankfurter.dev/v2/"
            f"rate/INR/{currency_code}"
        )


        response = requests.get(
            url,
            timeout=10
        )


        data = response.json()


        return {

            "currency_code": currency_code,

            "symbol": symbol,

            "name": currency_name,

            "rate": data["rate"],

            "date": data["date"]
        }


    except Exception:

        return None


# -----------------------------------
# HEADER
# -----------------------------------

st.title("🌍 TripMate AI")

st.subheader(
    "Your AI-powered travel companion"
)

st.write(
    "Get important travel information for your destination "
    "in one place."
)

st.divider()


# -----------------------------------
# TRAVEL INPUT
# -----------------------------------

destination = st.text_input(
    "📍 Where do you want to travel?",
    placeholder="Example: Paris, France"
)


# -----------------------------------
# LIVE WEATHER + CURRENCY
# -----------------------------------

if destination:

    live_weather = get_live_weather(destination)


    if live_weather:

        current = live_weather["current"]


        # =========================
        # LIVE WEATHER
        # =========================

        st.subheader("🌦️ Live Weather")


        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "🌡️ Temperature",
                f"{current['temperature_2m']} °C"
            )


        with col2:

            st.metric(
                "🥵 Feels Like",
                f"{current['apparent_temperature']} °C"
            )


        with col3:

            st.metric(
                "💧 Humidity",
                f"{current['relative_humidity_2m']}%"
            )


        with col4:

            st.metric(
                "💨 Wind",
                f"{current['wind_speed_10m']} km/h"
            )


        st.subheader("📅 3-Day Weather Forecast")

        daily = live_weather["daily"]

        for i in range(len(daily["time"])):
            forecast_date = daily["time"][i]
            min_temp = daily["temperature_2m_min"][i]
            max_temp = daily["temperature_2m_max"][i]
            rain_chance = daily["precipitation_probability_max"][i]

            st.write(
                f"**{forecast_date}** | "
                f"Min: {min_temp}°C | "
                f"Max: {max_temp}°C | "
                f"Rain chance: {rain_chance}%"
            )

        st.subheader("🧳 Weather-Based Travel Advice")

        for i in range(len(daily["time"])):
            max_temp = daily["temperature_2m_max"][i]
            rain_chance = daily["precipitation_probability_max"][i]

            advice = []

            if max_temp >= 35:
                advice.append("Carry light cotton clothes and sunscreen.")
            elif max_temp >= 28:
                advice.append("Wear light clothes and stay hydrated.")
            else:
                advice.append("Carry a light jacket if needed.")

            if rain_chance >= 60:
                advice.append("Carry an umbrella or raincoat.")
            elif rain_chance >= 30:
                advice.append("Keep a small umbrella with you.")

            st.write(f"**{daily['time'][i]}**")

            for tip in advice:
                st.write(f"- {tip}")

        st.subheader("🧳 Packing Checklist")

        packing_items = [
            "Clothes",
            "Comfortable shoes",
            "Toiletries",
            "Phone charger",
            "Travel documents",
            "Water bottle"
        ]

        if daily["temperature_2m_max"][0] >= 30:
            packing_items.extend(["Sunscreen", "Sunglasses"])

        if daily["precipitation_probability_max"][0] >= 30:
            packing_items.append("Umbrella or raincoat")

        for item in packing_items:
            st.checkbox(item, key=f"weather_packing_{item}")

        # =========================
        # SMART LIVE CURRENCY
        # =========================

        country_code = live_weather.get("country_code")

        currency = get_currency_rate(country_code)


        if currency:

            st.divider()

            st.subheader("💱 Live Currency")


            amount = st.number_input(
                "💰 Enter amount in INR",
                min_value=100,
                value=10000,
                step=500
            )


            converted_amount = amount * currency["rate"]


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "🇮🇳 Indian Rupees",
                    f"₹{amount:,.0f}"
                )


            with col2:

                st.metric(
                    f"💱 {currency['name']}",
                    f"{currency['symbol']}{converted_amount:,.2f}"
                )


            with col3:

                st.metric(
                    "📊 Exchange Rate",
                    f"1 INR = {currency['rate']:.4f}"
                )


            st.caption(
                f"Rate date: {currency['date']} • "
                "Reference exchange rate; actual bank/card rates may differ."
            )


# -----------------------------------
# TRIP DURATION
# -----------------------------------

days = st.number_input(
    "🗓️ How many days?",
    min_value=1,
    max_value=30,
    value=3
)


# -----------------------------------
# PLAN TRIP
# -----------------------------------

if st.button(
    "✈️ Plan My Trip",
    type="primary"
):


    if not destination:

        st.warning(
            "Please enter a destination."
        )


    else:

        prompt = f"""
You are TripMate AI, an expert travel planning assistant.

The traveler is visiting:
Destination: {destination}
Trip duration: {days} days
Traveler type: First-time visitor

Create a detailed, practical and well-organized travel guide.

The goal of TripMate AI is to provide the traveler with
the important information they would otherwise have to
search across many different websites.

Provide the following sections:

1. 🌍 DESTINATION OVERVIEW
- What the destination is famous for
- Best time to visit
- General travel experience
- Important things a first-time visitor should know

2. 🌦️ WEATHER & CLIMATE
- Typical weather by season
- Temperature range when appropriate
- Rain/snow considerations
- Best season for visiting
- Clearly state that actual weather should be checked
  using a live weather source

3. 👕 WHAT TO WEAR
- Clothing recommendations by season
- Comfortable footwear
- Cultural/religious dress considerations
- Special clothing requirements if applicable

4. 🗺️ TOP PLACES TO VISIT
Give at least 8 important places.
For each place include:
- Name
- Why it is worth visiting
- What you can do there
- Approximate time needed

5. 🍜 FOOD & LOCAL CUISINE
Give at least 8 foods/dishes to try.
For each:
- Name
- What it is
- Why it is popular
- Important dietary notes if relevant

6. 💰 BUDGET
Give approximate ranges for:
- Accommodation
- Food
- Local transportation
- Attractions
- Daily spending

Give budget, mid-range and comfortable travel options.
Clearly mention that prices vary by season and location.

7. 🚇 TRANSPORTATION
Explain:
- Airport/major arrival options
- Public transportation
- Metro/train/bus where applicable
- Taxi/ride-hailing
- Useful transport cards/apps
- Tips for first-time travelers

8. 🛂 VISA & DOCUMENTS
Explain generally:
- Passport
- Visa considerations
- Travel insurance
- Important documents
- Entry requirements

Do NOT invent visa rules.
Tell the traveler to verify current requirements
from official government/embassy sources.

9. 🎒 PACKING CHECKLIST
Create a practical checklist including:
- Clothes
- Shoes
- Electronics
- Chargers/adapters
- Documents
- Medicines
- Toiletries
- Weather-specific items
- Other destination-specific items

10. 🎎 LOCAL CULTURE & ETIQUETTE
Explain:
- Important local customs
- Greeting etiquette
- Dining etiquette
- Photography etiquette
- Religious/cultural considerations
- Things tourists should avoid

11. 🗣️ USEFUL LOCAL PHRASES
Give at least 8 useful phrases.
For each include:
- English meaning
- Local language
- Easy pronunciation

12. 📱 INTERNET & CONNECTIVITY
Explain:
- SIM/eSIM options
- Wi-Fi availability
- Useful apps
- Internet restrictions if applicable

13. ⚠️ SAFETY & COMMON MISTAKES
Explain:
- Common tourist mistakes
- Areas/situations where travelers should be careful
- Common scams if relevant
- Emergency considerations

14. 🗓️ {days}-DAY ITINERARY
Create a realistic day-by-day itinerary.
For each day include:
- Morning
- Afternoon
- Evening
- Main places
- Food suggestion
- Approximate pace

15. 💡 FIRST-TIME TRAVELER TIPS
Give at least 10 practical tips that someone
visiting this destination for the first time should know.

IMPORTANT:
- Be detailed but easy to understand.
- Prefer useful practical information over generic statements.
- Do not hallucinate exact facts.
- Clearly label information that can change over time.
- Do not present estimated prices as exact prices.
- Do not claim live weather or live currency rates.
- Do not make unsupported claims.

VERY IMPORTANT:

Return your answer ONLY as valid JSON.

Use exactly these keys:

{{
  "overview": "",
  "weather": "",
  "clothing": "",
  "places": "",
  "food": "",
  "budget": "",
  "transport": "",
  "documents": "",
  "packing": "",
  "culture": "",
  "phrases": "",
  "connectivity": "",
  "safety": "",
  "itinerary": "",
  "tips": ""
}}

Do not use markdown code fences.
Do not add any text before or after the JSON.
"""


        # -----------------------------------
        # GEMINI RESPONSE
        # -----------------------------------

        with st.spinner(
            "🤖 TripMate AI is planning your trip..."
        ):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )


                try:

                    travel_data = json.loads(
                        response.text
                    )


                    # =========================
                    # SUCCESS MESSAGE
                    # =========================

                    st.success(
                        f"✅ Your {days}-day {destination} "
                        "travel guide is ready!"
                    )


                    st.divider()


                    # =========================
                    # TRIP HEADER
                    # =========================

                    st.title(
                        f"🌍 {destination}"
                    )

                    st.caption(
                        f"Your personalized {days}-day AI travel guide"
                    )


                    # Quick overview cards

                    col1, col2, col3 = st.columns(3)


                    with col1:

                        st.metric(
                            "🗓️ Trip Duration",
                            f"{days} Days"
                        )


                    with col2:

                        st.metric(
                            "📍 Destination",
                            destination
                        )


                    with col3:

                        st.metric(
                            "🤖 AI Guide",
                            "Ready"
                        )


                    st.divider()


                    # =========================
                    # DESTINATION OVERVIEW
                    # =========================

                    with st.expander(
                        "🌍 Destination Overview",
                        expanded=True
                    ):

                        st.write(
                            travel_data.get(
                                "overview",
                                "Overview unavailable."
                            )
                        )


                    # =========================
                    # WEATHER + CLOTHING
                    # =========================

                    col1, col2 = st.columns(2)


                    with col1:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "🌦️ Weather & Climate"
                            )

                            st.write(
                                travel_data.get(
                                    "weather",
                                    "Weather information unavailable."
                                )
                            )


                    with col2:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "👕 What to Wear"
                            )

                            st.write(
                                travel_data.get(
                                    "clothing",
                                    "Clothing information unavailable."
                                )
                            )


                    # =========================
                    # PLACES + FOOD
                    # =========================

                    st.divider()


                    col1, col2 = st.columns(2)


                    with col1:

                        with st.expander(
                            "🗺️ Places to Visit",
                            expanded=True
                        ):

                            st.write(
                                travel_data.get(
                                    "places",
                                    "Places information unavailable."
                                )
                            )


                    with col2:

                        with st.expander(
                            "🍜 Food to Try",
                            expanded=True
                        ):

                            st.write(
                                travel_data.get(
                                    "food",
                                    "Food information unavailable."
                                )
                            )


                    # =========================
                    # BUDGET + TRANSPORT
                    # =========================

                    st.divider()


                    col1, col2 = st.columns(2)


                    with col1:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "💰 Budget"
                            )

                            st.write(
                                travel_data.get(
                                    "budget",
                                    "Budget information unavailable."
                                )
                            )


                    with col2:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "🚇 Transportation"
                            )

                            st.write(
                                travel_data.get(
                                    "transport",
                                    "Transport information unavailable."
                                )
                            )


                    # =========================
                    # DOCUMENTS + PACKING
                    # =========================

                    st.divider()


                    col1, col2 = st.columns(2)


                    with col1:

                        with st.expander(
                            "🛂 Documents & Visa",
                            expanded=False
                        ):

                            st.write(
                                travel_data.get(
                                    "documents",
                                    "Document information is currently unavailable."
                                )
                            )


                    with col2:

                        with st.expander(
                            "🎒 Packing Checklist",
                            expanded=True
                        ):

                            st.write(
                                travel_data.get(
                                    "packing",
                                    "Packing information unavailable."
                                )
                            )


                    # =========================
                    # CULTURE + PHRASES
                    # =========================

                    st.divider()


                    col1, col2 = st.columns(2)


                    with col1:

                        with st.expander(
                            "🎎 Culture & Etiquette",
                            expanded=False
                        ):

                            st.write(
                                travel_data.get(
                                    "culture",
                                    "Culture information unavailable."
                                )
                            )


                    with col2:

                        with st.expander(
                            "🗣️ Useful Local Phrases",
                            expanded=False
                        ):

                            st.write(
                                travel_data.get(
                                    "phrases",
                                    "Phrase information unavailable."
                                )
                            )


                    # =========================
                    # CONNECTIVITY + SAFETY
                    # =========================

                    st.divider()


                    col1, col2 = st.columns(2)


                    with col1:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "📱 Internet & Connectivity"
                            )

                            st.write(
                                travel_data.get(
                                    "connectivity",
                                    "Connectivity information unavailable."
                                )
                            )


                    with col2:

                        with st.container(
                            border=True
                        ):

                            st.subheader(
                                "⚠️ Safety"
                            )

                            st.write(
                                travel_data.get(
                                    "safety",
                                    "Safety information unavailable."
                                )
                            )


                    # =========================
                    # ITINERARY
                    # =========================

                    st.divider()


                    st.header(
                        "🗓️ Suggested Itinerary"
                    )


                    st.write(
                        travel_data.get(
                            "itinerary",
                            "Itinerary information unavailable."
                        )
                    )


                    # =========================
                    # FIRST-TIME TRAVELER TIPS
                    # =========================

                    st.divider()


                    st.header(
                        "💡 First-Time Traveler Tips"
                    )


                    st.info(
                        travel_data.get(
                            "tips",
                            "Travel tips unavailable."
                        )
                    )


                    # =========================
                    # FOOTER
                    # =========================

                    st.divider()


                    st.caption(
                        "🤖 TripMate AI — "
                        "Everything you need before you travel."
                    )


                except json.JSONDecodeError:

                    st.error(
                        "AI returned an unexpected format."
                    )

                    st.write(
                        response.text
                    )


            except Exception as e:

                st.error(
                    f"Something went wrong while "
                    f"processing your trip: {e}"
                )