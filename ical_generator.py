import io
import uuid
from datetime import date, datetime, time

import pytz
import streamlit as st
from icalendar import Calendar, Event

# --- Page Configuration ---
st.set_page_config(
    page_title="Airbnb iCal Simulator", page_icon="📅", layout="centered"
)

# --- Custom Styling ---
st.markdown(
    """
    <style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF5A5F; /* Airbnb Red */
        color: white;
    }
    .stButton button:hover {
        background-color: #FF385C;
        color: white;
    }
    .event-card {
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- Session State Management ---
if "bookings" not in st.session_state:
    st.session_state.bookings = []


def add_booking(start_dt, end_dt, status):
    # Generate a UID that looks like Airbnb's format
    # Example: 1418fb94e984-51401b505dec1292fa6b395a@airbnb.com
    airbnb_uid = f"{uuid.uuid4()}-{uuid.uuid4().hex[:10]}@airbnb.com"

    booking = {
        "id": airbnb_uid,
        "start": start_dt,  # Storing as datetime
        "end": end_dt,  # Storing as datetime
        "summary": status,
    }
    st.session_state.bookings.append(booking)
    st.toast("Reservation Added!", icon="✅")


def remove_booking(idx):
    st.session_state.bookings.pop(idx)
    st.rerun()


def generate_ical_content():
    cal = Calendar()

    # --- 1. Match Airbnb Headers ---
    cal.add("prodid", "-//Airbnb Inc//Hosting Calendar 1.0//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")

    for booking in st.session_state.bookings:
        event = Event()

        # --- 2. Event Details ---
        event.add("summary", booking["summary"])

        # Because these are datetime objects (not date),
        # icalendar will output: DTSTART:20251126T140000
        event.add("dtstart", booking["start"])
        event.add("dtend", booking["end"])

        event.add("uid", booking["id"])
        # Add timestamp in UTC
        event.add("dtstamp", datetime.now(pytz.utc))

        cal.add_component(event)

    return cal.to_ical()


# --- UI Header ---
st.title("📅 Airbnb iCal Simulator")
st.markdown(
    "Create a valid `.ics` file including **Times** and valid **Airbnb Headers**."
)

# --- Input Section ---
st.divider()
st.subheader("Add a Reservation")

# Status Dropdown
status_option = st.selectbox(
    "Reservation Status",
    ["Reserved", "Airbnb (Not available)"],
    help="'Reserved' is a guest booking. 'Airbnb (Not available)' is a blocked date.",
)

col1, col2 = st.columns(2)

with col1:
    start_d = st.date_input("Check-in Date", value=datetime.today())
    start_t = st.time_input(
        "Check-in Time", value=datetime.strptime("14:00", "%H:%M").time()
    )

with col2:
    end_d = st.date_input("Check-out Date", value=start_d)
    end_t = st.time_input(
        "Check-out Time", value=datetime.strptime("11:00", "%H:%M").time()
    )

# Combine Date and Time
start_dt = datetime.combine(start_d, start_t)
end_dt = datetime.combine(end_d, end_t)

# Validation & Add Button
if st.button("Add Reservation"):
    if end_dt <= start_dt:
        st.error("Error: Check-out time must be after Check-in time.")
    else:
        add_booking(start_dt, end_dt, status_option)

# --- Preview Section ---
st.divider()
st.subheader(f"Current Bookings ({len(st.session_state.bookings)})")

if not st.session_state.bookings:
    st.caption("No bookings added yet.")
else:
    for idx, booking in enumerate(st.session_state.bookings):
        # Card View
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"**{booking['summary']}**")
                st.caption(f"UID: ...{booking['id'][-15:]}")
            with c2:
                # Format as YYYY-MM-DD HH:MM
                st.write(f"🟢 {booking['start'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"🔴 {booking['end'].strftime('%Y-%m-%d %H:%M')}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    remove_booking(idx)
            st.markdown("---")

# --- Download Section ---
if st.session_state.bookings:
    st.subheader("Download File")

    ical_bytes = generate_ical_content()

    st.download_button(
        label="📥 Download .ics File",
        data=ical_bytes,
        file_name="airbnb_simulation.ics",
        mime="text/calendar",
    )
