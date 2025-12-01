import requests
from icalendar import Calendar


def fetch_airbnb_from_ical(ical_url):
    """

    Given an Airbnb-hosted ICS URL, fetch and return a list of tuples:

      (start_datetime, end_datetime, uid)

    for each VEVENT whose SUMMARY is exactly "Reserved".

    Any date-only DTSTART/DTEND will be converted to a timezone-aware midnight.

    """

    print("fetch_airbnb_from_ical: Attempting to GET %s", ical_url)

    try:

        resp = requests.get(
            ical_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CleaningApp/1.0)"},
        )

        resp.raise_for_status()

        print("fetch_airbnb_from_ical: HTTP status = %d", resp.status_code)

    except Exception as e:

        print(
            "fetch_airbnb_from_ical: Could not download ICS from %s → %s", ical_url, e
        )

        return []

    snippet = resp.content[:200]

    try:

        print(
            "fetch_airbnb_from_ical: snippet = %s",
            snippet.decode("utf-8", errors="ignore"),
        )

    except Exception:

        print("fetch_airbnb_from_ical: snippet (raw bytes) = %s", snippet)

    try:

        cal = Calendar.from_ical(resp.content)

    except Exception as e:

        print("fetch_airbnb_from_ical: Failed to parse ICS from %s → %s", ical_url, e)

        return []

    events = []

    for component in cal.walk():

        if component.name != "VEVENT":

            continue

        raw_summary = component.get("summary")

        if not raw_summary:

            continue

        summary = str(raw_summary).strip()

        # Only accept Airbnb‐style SUMMARY: "Reserved"

        if summary != "Reserved":

            continue

        dtstart_prop = component.get("dtstart")

        dtend_prop = component.get("dtend")

        uid_prop = component.get("uid")

        if not dtstart_prop or not dtend_prop or not uid_prop:

            print("fetch_airbnb_from_ical: Skipping VEVENT missing dtstart/dtend/uid")

            continue

        start = dtstart_prop.dt

        end = dtend_prop.dt

        uid = str(uid_prop)

        # Normalize date-only → tz-aware midnight

        if isinstance(start, date) and not isinstance(start, datetime):

            start = make_aware(datetime.combine(start, datetime.min.time()))

        elif isinstance(start, datetime) and start.tzinfo is None:

            start = make_aware(start)

        if isinstance(end, date) and not isinstance(end, datetime):

            end = make_aware(datetime.combine(end, datetime.min.time()))

        elif isinstance(end, datetime) and end.tzinfo is None:

            end = make_aware(end)

        events.append((start, end, uid))

    print(
        "fetch_airbnb_from_ical: Total Airbnb events fetched from %s → %d",
        ical_url,
        len(events),
    )

    return events
