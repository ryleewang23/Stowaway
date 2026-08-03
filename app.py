"""
Stowaway

A mobile-friendly, AI-assisted packing application.
"""

from collections import defaultdict

from datetime import date, timedelta
import html

import streamlit as st
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox

from amazon_helper import amazon_link
from export_helpers import (
    create_csv_bytes,
    create_pdf_bytes
)
from item_helpers import (
    CATEGORY_ORDER,
    CATEGORY_ICONS,
    create_item,
    remove_duplicate_names,
    normalize_ai_items
)
from styles import apply_styles
from destination_helper import get_destination_photo

from weather import (
    search_locations,
    get_forecast,
    historical_range,
    create_weather_summary
)

from packing_logic import (
    build_list,
    trip_length
)

from ai_helper import ai_suggestions


##################################################
# PAGE SETTINGS
##################################################

st.set_page_config(
    page_title="Stowaway",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="collapsed"
)


##################################################
# DESIGN SYSTEM
##################################################

apply_styles()


##################################################
# SESSION STATE
##################################################

DEFAULT_STATE = {
    "packing_items": [],
    "trip_generated": False,
    "weather_summary": "",
    "weather_details": {},
    "location_name": "",
    "selected_location_data": None,
    "travel_tips": [],
    "generation_message": "",
    "trip_intro": "",
    "saved_start_date": None,
    "saved_end_date": None,
    "saved_packing_preference": "General essentials"
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


##################################################
# HELPER FUNCTIONS
##################################################


def render_destination_time_card(
        destination_timezone,
        destination_name):
    """
    Renders a live destination clock and compares it with
    the viewer's browser timezone.

    JavaScript's Intl API handles daylight-saving changes.
    """
    safe_timezone = html.escape(
        str(destination_timezone)
    )

    safe_name = html.escape(
        str(destination_name)
    )

    component_html = f"""
    <div id="stowaway-time-card" style="
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        border: 1px solid rgba(77, 111, 136, 0.18);
        border-radius: 16px;
        background: rgba(255,255,255,0.92);
        padding: 16px 18px;
        color: #183247;
    ">
        <div style="
            font-size: 12px;
            font-weight: 700;
            letter-spacing: .06em;
            text-transform: uppercase;
            color: #4d91b8;
            margin-bottom: 6px;
        ">
            Local time in {safe_name}
        </div>

        <div id="destination-time" style="
            font-size: 30px;
            font-weight: 750;
            line-height: 1.1;
            margin-bottom: 5px;
        ">
            Loading…
        </div>

        <div id="time-difference" style="
            font-size: 14px;
            color: #66798a;
        ">
            Comparing with your local time…
        </div>
    </div>

    <script>
        const destinationZone = "{safe_timezone}";

        function zoneOffsetMinutes(timeZone, date) {{
            const parts = new Intl.DateTimeFormat(
                "en-US",
                {{
                    timeZone: timeZone,
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hourCycle: "h23"
                }}
            ).formatToParts(date);

            const values = {{}};

            for (const part of parts) {{
                if (part.type !== "literal") {{
                    values[part.type] = part.value;
                }}
            }}

            const representedAsUtc = Date.UTC(
                Number(values.year),
                Number(values.month) - 1,
                Number(values.day),
                Number(values.hour),
                Number(values.minute),
                Number(values.second)
            );

            return (
                representedAsUtc - date.getTime()
            ) / 60000;
        }}

        function formatDifference(hours) {{
            const rounded = Math.round(
                Math.abs(hours) * 2
            ) / 2;

            if (Math.abs(hours) < 0.25) {{
                return "Same time as your current location";
            }}

            const amount = Number.isInteger(rounded)
                ? rounded.toFixed(0)
                : rounded.toFixed(1);

            return hours > 0
                ? `${{amount}} hour${{rounded === 1 ? "" : "s"}} ahead of you`
                : `${{amount}} hour${{rounded === 1 ? "" : "s"}} behind you`;
        }}

        function updateClock() {{
            const now = new Date();

            const destinationTime = new Intl.DateTimeFormat(
                "en-US",
                {{
                    timeZone: destinationZone,
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                    hour: "numeric",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true
                }}
            ).format(now);

            const userZone = Intl.DateTimeFormat()
                .resolvedOptions()
                .timeZone;

            const destinationOffset = zoneOffsetMinutes(
                destinationZone,
                now
            );

            const userOffset = zoneOffsetMinutes(
                userZone,
                now
            );

            const differenceHours = (
                destinationOffset - userOffset
            ) / 60;

            document.getElementById(
                "destination-time"
            ).textContent = destinationTime;

            document.getElementById(
                "time-difference"
            ).textContent =
                formatDifference(differenceHours)
                + ` · ${{destinationZone}}`;
        }}

        updateClock();
        setInterval(updateClock, 1000);
    </script>
    """

    components.html(
        component_html,
        height=130,
        scrolling=False
    )


def calculate_forecast_weather(
        forecast,
        start_date,
        end_date):
    """Summarizes forecast data for the selected trip dates."""
    times = forecast.get("time", [])
    highs = forecast.get("temperature_2m_max", [])
    lows = forecast.get("temperature_2m_min", [])
    precipitation = forecast.get("precipitation_sum", [])

    selected_highs = []
    selected_lows = []
    selected_rain = []

    for index, date_string in enumerate(times):
        forecast_date = date.fromisoformat(date_string)

        if start_date <= forecast_date <= end_date:
            if index < len(highs):
                selected_highs.append(highs[index])

            if index < len(lows):
                selected_lows.append(lows[index])

            if index < len(precipitation):
                selected_rain.append(precipitation[index])

    if not selected_highs:
        selected_highs = highs

    if not selected_lows:
        selected_lows = lows

    if not selected_rain:
        selected_rain = precipitation

    valid_highs = [
        value for value in selected_highs
        if value is not None
    ]

    valid_lows = [
        value for value in selected_lows
        if value is not None
    ]

    valid_rain = [
        value for value in selected_rain
        if value is not None
    ]

    average_high = (
        sum(valid_highs) / len(valid_highs)
        if valid_highs
        else 72
    )

    average_low = (
        sum(valid_lows) / len(valid_lows)
        if valid_lows
        else average_high
    )

    average_temperature = (
        average_high + average_low
    ) / 2

    total_rain = (
        sum(valid_rain)
        if valid_rain
        else 0
    )

    weather_summary = (
        f"Forecast highs around {average_high:.1f}°F "
        f"and lows around {average_low:.1f}°F. "
        f"Expected total precipitation: "
        f"{total_rain:.2f} inches."
    )

    details = {
        "type": "Live forecast",
        "average_high": round(average_high, 1),
        "average_low": round(average_low, 1),
        "rain": round(total_rain, 2)
    }

    return (
        average_temperature,
        weather_summary,
        details
    )


def weather_icon(temperature, rain_amount=0):
    """Chooses a simple weather icon using Fahrenheit."""
    if rain_amount and rain_amount >= 0.1:
        return "🌧️"

    if temperature >= 85:
        return "☀️"

    if temperature >= 65:
        return "🌤️"

    if temperature >= 45:
        return "🧥"

    return "❄️"


def make_travel_tips(
        destination,
        days,
        average_temperature,
        activities,
        weather_details):
    """Creates concise rule-based travel tips."""
    tips = [
        f"Save an offline map of {destination} before leaving your hotel."
    ]

    if days >= 7:
        tips.append(
            "Bring a laundry bag and consider doing laundry once."
        )

    if average_temperature >= 85:
        tips.append(
            "Carry water and sun protection during outdoor plans."
        )
    elif average_temperature <= 50:
        tips.append(
            "Wear layers so you can adjust between indoor and outdoor temperatures."
        )

    if weather_details.get("rain", 0) > 0:
        tips.append(
            "Keep a compact umbrella or rain jacket in your day bag."
        )

    activity_text = " ".join(activities).lower()

    if "walk" in activity_text or "sightseeing" in activity_text:
        tips.append(
            "Break in comfortable walking shoes before the trip."
        )

    if "beach" in activity_text or "swim" in activity_text:
        tips.append(
            "Bring a separate bag for wet or sandy belongings."
        )

    if "hiking" in activity_text or "trail" in activity_text:
        tips.append(
            "Download trail maps before heading out."
        )

    return tips[:4]


def reset_app():
    """Clears generated trip information."""
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value

    st.rerun()


@st.cache_data(ttl=900, show_spinner=False)
def cached_location_search(search_text):
    """
    Searches Open-Meteo for matching locations.

    Results are cached for 15 minutes so repeated searches do not
    make unnecessary API requests.
    """
    return search_locations(
        search_text,
        count=8
    )


def location_autocomplete(search_term):
    """
    Returns autocomplete choices while the user types.

    Each option is a tuple:
    - the first value is displayed in the dropdown
    - the second value is the selected location dictionary
    """
    search_term = str(search_term).strip()

    if len(search_term) < 2:
        return []

    try:
        locations = cached_location_search(search_term)
    except Exception:
        return []

    options = []

    for location in locations:
        label = location.get(
            "display_name",
            location.get("name", "Unknown location")
        )

        population = location.get("population")

        if population:
            label += f" · population {int(population):,}"

        options.append(
            (
                label,
                location
            )
        )

    return options


##################################################
# HERO
##################################################

st.markdown(
    """
    <div class="hero-card">
        <div class="brand-row">
            <div class="brand-mark">🧳</div>
            <div>
                <div class="hero-title">Stowaway</div>
                <div class="hero-subtitle">
                    Your personalized packing companion
                </div>
            </div>
        </div>
        <div class="hero-tagline">
            Weather-aware lists, smart activity suggestions, and everything
            organized in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


##################################################
# TRIP FORM
##################################################

with st.container(border=True):
    st.subheader("Plan your trip")

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        selected_location = st_searchbox(
            location_autocomplete,
            key="destination_autocomplete",
            label="📍 Where are you staying?",
            placeholder="Start typing a city, town, or destination",
            debounce=350,
            clear_on_submit=False,
            edit_after_submit="option"
        )

        if selected_location:
            location_caption_parts = []

            if selected_location.get("timezone"):
                location_caption_parts.append(
                    selected_location["timezone"]
                )

            if selected_location.get("country_code"):
                location_caption_parts.append(
                    selected_location["country_code"]
                )

            if location_caption_parts:
                st.caption(
                    " · ".join(location_caption_parts)
                )
        else:
            st.caption(
                "Suggestions appear automatically after two letters."
            )

        start_date = st.date_input(
            "Start date",
            value=date.today() + timedelta(days=7)
        )
        end_date = st.date_input(
            "End date",
            value=date.today() + timedelta(days=13)
        )


        packing_preference = st.selectbox(
            "Packing preference",
            [
                "General essentials",
                "Women's essentials",
                "Men's essentials"
            ]
        )

    with form_col2:
        \
        ai_item_count = st.slider(
            "Number of AI suggestions",
            min_value=1,
            max_value=10,
            value=5
        )

        use_ai = st.toggle(
            "Include AI suggestions",
            value=True
        )

    activities_text = st.text_area(
        "What are you planning to do?",
        placeholder=(
            "Example: hiking, visiting museums, going to nice dinners, "
            "swimming, shopping, and attending a concert"
        ),
        height=110
    )

    activities = [
        activity.strip()
        for activity in activities_text.replace(
            "\n",
            ","
        ).split(",")
        if activity.strip()
    ]

    button_col1, button_col2 = st.columns([4, 1])

    with button_col1:
        generate_button = st.button(
            "Generate packing list",
            type="primary",
            use_container_width=True
        )

    with button_col2:
        reset_button = st.button(
            "Reset",
            use_container_width=True
        )

    if reset_button:
        reset_app()


##################################################
# GENERATE PACKING LIST
##################################################

if generate_button:
    if selected_location is None:
        st.error(
            "Enter a destination and choose the correct location "
            "from the suggestions."
        )

    elif end_date < start_date:
        st.error(
            "The end date must be on or after the start date."
        )

    else:
        try:
            with st.spinner(
                "Checking weather and organizing your list..."
            ):
                location_name = selected_location.get(
                    "display_name",
                    selected_location.get("name", "Selected location")
                )

                latitude = selected_location["latitude"]
                longitude = selected_location["longitude"]

                days = trip_length(
                    start_date,
                    end_date
                )

                forecast_limit = (
                    date.today() + timedelta(days=14)
                )

                if start_date <= forecast_limit:
                    forecast = get_forecast(
                        latitude,
                        longitude
                    )

                    (
                        average_temperature,
                        weather_summary,
                        weather_details
                    ) = calculate_forecast_weather(
                        forecast,
                        start_date,
                        end_date
                    )

                else:
                    history = historical_range(
                        latitude,
                        longitude,
                        start_date.month,
                        start_date.day
                    )

                    weather_summary = (
                        create_weather_summary(history)
                    )

                    if history:
                        average_temperature = (
                            history["average_high"]
                        )

                        weather_details = {
                            "type": "Historical weather",
                            "average_high": history[
                                "average_high"
                            ],
                            "minimum_high": history[
                                "minimum_high"
                            ],
                            "maximum_high": history[
                                "maximum_high"
                            ],
                            "rain_probability": history[
                                "rain_probability"
                            ],
                            "rain": history[
                                "rain_probability"
                            ]
                        }

                    else:
                        average_temperature = 72

                        weather_details = {
                            "type": "Historical weather unavailable",
                            "average_high": 72,
                            "rain": 0
                        }

                if packing_preference == "Women's essentials":
                    sex_value = "Female"

                elif packing_preference == "Men's essentials":
                    sex_value = "Male"

                else:
                    sex_value = "General"

                standard_names = build_list(
                    destination=location_name,
                    start_date=start_date,
                    end_date=end_date,
                    sex=sex_value,
                    activities=activities,
                    average_temperature=average_temperature
                )

                generated_items = [
                    create_item(
                        name=item_name,
                        source="Standard"
                    )
                    for item_name in standard_names
                ]

                ai_status_message = ""
                trip_intro = ""

                if use_ai:
                    ai_result = ai_suggestions(
                        destination=location_name,
                        days=days,
                        weather_summary=weather_summary,
                        activities=activities,
                        sex=packing_preference,
                        existing_items=standard_names,
                        number=ai_item_count
                    )

                    generated_items.extend(
                        normalize_ai_items(
                            ai_result.get("items", [])
                        )
                    )

                    ai_status_message = ai_result.get(
                        "message",
                        ""
                    )

                    trip_intro = ai_result.get(
                        "trip_intro",
                        ""
                    )

                st.session_state.packing_items = (
                    remove_duplicate_names(
                        generated_items
                    )
                )

                st.session_state.trip_generated = True
                st.session_state.weather_summary = weather_summary
                st.session_state.weather_details = weather_details
                st.session_state.location_name = location_name
                st.session_state.selected_location_data = (
                    selected_location
                )
                st.session_state.saved_start_date = start_date
                st.session_state.saved_end_date = end_date
                st.session_state.saved_packing_preference = (
                    packing_preference
                )

                st.session_state.travel_tips = (
                    make_travel_tips(
                        destination=location_name,
                        days=days,
                        average_temperature=average_temperature,
                        activities=activities,
                        weather_details=weather_details
                    )
                )

                st.session_state.generation_message = (
                    ai_status_message
                )

                st.session_state.trip_intro = (
                    trip_intro
                )

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(
                "The trip could not be generated. "
                f"Details: {error}"
            )


##################################################
# EMPTY STATE
##################################################

if not st.session_state.trip_generated:
    st.caption(
        "Start typing your destination, choose the exact match, "
        "then enter your trip details."
    )

    overview_col1, overview_col2, overview_col3 = (
        st.columns(3)
    )

    with overview_col1:
        st.metric(
            "Weather-aware",
            "Live + historical"
        )

    with overview_col2:
        st.metric(
            "Personalized",
            "Activities + AI"
        )

    with overview_col3:
        st.metric(
            "Organized",
            "Compact categories"
        )


##################################################
# GENERATED TRIP
##################################################

else:
    location_name = st.session_state.location_name
    selected_location_data = (
        st.session_state.selected_location_data
        or {}
    )
    items = st.session_state.packing_items
    weather_details = st.session_state.weather_details
    saved_start = st.session_state.saved_start_date
    saved_end = st.session_state.saved_end_date
    saved_packing_preference = (
        st.session_state.saved_packing_preference
    )

    st.divider()

    header_col1, header_col2 = st.columns([5, 1])

    with header_col1:
        st.header(f"✈️ {location_name}")

        st.caption(
            f"{saved_start.strftime('%B %d, %Y')} – "
            f"{saved_end.strftime('%B %d, %Y')}"
        )

    with header_col2:
        if st.button(
            "New trip",
            use_container_width=True
        ):
            reset_app()

    photo_info = get_destination_photo(
        selected_location_data
    )

    if photo_info:
        st.image(
            photo_info["image_url"],
            caption=(
                f"{photo_info['caption']} · "
                f"{photo_info['source']}"
            ),
            use_container_width=True
        )

        if photo_info.get("page_url"):
            st.caption(
                "Photo source: "
                + photo_info["page_url"]
            )
    else:
        st.info(
            "A destination photo was not available "
            "for this location."
        )

    destination_timezone = (
        selected_location_data.get(
            "timezone",
            "UTC"
        )
    )

    render_destination_time_card(
        destination_timezone=destination_timezone,
        destination_name=location_name
    )

    if st.session_state.trip_intro:
        st.markdown(
            f"""
            <div class="summary-card">
                <strong>Your trip at a glance</strong><br>
                {html.escape(st.session_state.trip_intro)}
            </div>
            """,
            unsafe_allow_html=True
        )

    average_high = weather_details.get(
        "average_high",
        72
    )

    rain_value = weather_details.get(
        "rain",
        0
    )

    icon = weather_icon(
        average_high,
        rain_value
    )

    weather_col1, weather_col2, weather_col3 = (
        st.columns(3)
    )

    with weather_col1:
        st.metric(
            f"{icon} Weather",
            weather_details.get(
                "type",
                "Weather data"
            )
        )

    with weather_col2:
        st.metric(
            "Average high",
            f"{average_high}°F"
        )

    with weather_col3:
        if "rain_probability" in weather_details:
            st.metric(
                "Rain frequency",
                f"{weather_details['rain_probability']}%"
            )
        else:
            st.metric(
                "Expected rain",
                f"{rain_value} in"
            )

    st.markdown(
        f"""
        <div class="summary-card">
            <strong>Weather summary</strong><br>
            {html.escape(st.session_state.weather_summary)}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.travel_tips:
        with st.expander(
            "Smart travel tips",
            expanded=False
        ):
            for tip in st.session_state.travel_tips:
                st.markdown(
                    f"""
                    <div class="tip-card">
                        💡 {html.escape(tip)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    total_items = len(items)

    packed_items = sum(
        1 for item in items
        if item["packed"]
    )

    progress = (
        packed_items / total_items
        if total_items
        else 0
    )

    progress_col1, progress_col2 = st.columns([5, 1])

    with progress_col1:
        st.subheader("Your packing list")

    with progress_col2:
        st.write(
            f"**{packed_items}/{total_items}**"
        )

    st.progress(progress)

    if progress == 1 and total_items > 0:
        st.success(
            "Everything is packed. Have a great trip! 🎉"
        )

    grouped_items = defaultdict(list)

    for item in items:
        grouped_items[item["category"]].append(item)

    ordered_categories = CATEGORY_ORDER + sorted(
        category
        for category in grouped_items
        if category not in CATEGORY_ORDER
    )

    items_to_remove = []

    for category in ordered_categories:
        category_items = grouped_items.get(
            category,
            []
        )

        if not category_items:
            continue

        category_packed = sum(
            item["packed"]
            for item in category_items
        )

        icon = CATEGORY_ICONS.get(
            category,
            "📦"
        )

        with st.expander(
            (
                f"{icon} {category} "
                f"· {category_packed}/{len(category_items)} packed"
            ),
            expanded=category in {
                "Documents",
                "Clothing"
            }
        ):
            for item in category_items:
                item_id = item["id"]

                (
                    check_col,
                    text_col,
                    buy_col,
                    remove_col
                ) = st.columns(
                    [0.55, 4.8, 1.15, 0.8]
                )

                with check_col:
                    checked = st.checkbox(
                        "Packed",
                        value=item["packed"],
                        key=f"packed_{item_id}",
                        label_visibility="collapsed"
                    )

                    item["packed"] = checked

                with text_col:
                    escaped_name = html.escape(
                        item["name"]
                    )

                    badge = (
                        "<span class='source-badge'>AI</span>"
                        if item["source"] == "AI"
                        else ""
                    )

                    if item["packed"]:
                        item_display = (
                            f"<s><strong>{escaped_name}</strong></s>"
                        )
                    else:
                        item_display = (
                            f"<strong>{escaped_name}</strong>"
                        )

                    st.markdown(
                        item_display + badge,
                        unsafe_allow_html=True
                    )

                    if item["reason"]:
                        st.markdown(
                            (
                                "<div class='item-reason'>"
                                f"{html.escape(item['reason'])}"
                                "</div>"
                            ),
                            unsafe_allow_html=True
                        )

                with buy_col:
                    st.link_button(
                        "Shop",
                        amazon_link(
                            item_name=item["name"],
                            packing_preference=(
                                saved_packing_preference
                            ),
                            category=item["category"]
                        ),
                        use_container_width=True
                    )

                with remove_col:
                    if st.button(
                        "×",
                        key=f"remove_{item_id}",
                        help="Remove item",
                        use_container_width=True
                    ):
                        items_to_remove.append(
                            item_id
                        )

            if items_to_remove:
                st.session_state.packing_items = [
                    item
                    for item in st.session_state.packing_items
                    if item["id"] not in items_to_remove
                ]

                st.rerun()

    with st.expander(
        "Add your own item",
        expanded=False
    ):
        custom_col1, custom_col2 = st.columns(2)

        with custom_col1:
            custom_item = st.text_input(
                "Item name",
                placeholder="Example: Prescription medication"
            )

        with custom_col2:
            custom_category = st.selectbox(
                "Category",
                CATEGORY_ORDER
            )

        if st.button(
            "Add item",
            use_container_width=True
        ):
            if not custom_item.strip():
                st.warning(
                    "Enter an item name."
                )

            elif custom_item.strip().lower() in {
                item["name"].lower()
                for item in items
            }:
                st.warning(
                    "That item is already on the list."
                )

            else:
                st.session_state.packing_items.append(
                    create_item(
                        name=custom_item,
                        source="Custom",
                        reason="Added manually.",
                        category=custom_category
                    )
                )

                st.rerun()

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        st.download_button(
            "Download CSV",
            data=create_csv_bytes(
                st.session_state.packing_items
            ),
            file_name="stowaway_packing_list.csv",
            mime="text/csv",
            use_container_width=True
        )

    with export_col2:
        st.download_button(
            "Download PDF",
            data=create_pdf_bytes(
                destination=location_name,
                start_date=saved_start,
                end_date=saved_end,
                items=st.session_state.packing_items
            ),
            file_name="stowaway_packing_list.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.session_state.generation_message:
        st.caption(
            st.session_state.generation_message
        )


##################################################
# FOOTER
##################################################

st.divider()

st.caption(
    "Stowaway uses Open-Meteo weather information and "
    "optional OpenAI-generated suggestions. Always check "
    "official travel requirements before your trip."
)
