import requests
from ics import Calendar, Event
from datetime import datetime
from zoneinfo import ZoneInfo

JERUSALEM = ZoneInfo("Asia/Jerusalem")

YEAR = 2026
SOURCE_FILE = "source"      # one course code per line
OUTPUT_FILE = "HUJI_Exams_2026.ics"


def get_course(course_code):
    r = requests.get(
        f"https://shnaton.huji.ac.il/api/courses/code/{course_code}?year={YEAR}"
    )
    r.raise_for_status()

    data = r.json()[0]

    return {
        "id": data["id"],
        "name": data["name"]["he"],
    }


def get_assignments(course_id):
    r = requests.get(
        f"https://shnaton.huji.ac.il/api/assignments?year={YEAR}&courseId={course_id}"
    )
    r.raise_for_status()
    return r.json()


def add_course_events(calendar, course_code):
    course = get_course(course_code)
    assignments = get_assignments(course["id"])

    for assignment in assignments:

        assignment_name = assignment["assignmentDefinition"]["name"]["en"]

        # Only exams
        if assignment_name not in ("Written test", "Mid-term Exams"):
            continue

        for schedule in assignment.get("schedules", []):

            event = Event()

            event.name = f"{course['name']} ({course_code})"

            start = datetime.fromisoformat(schedule["startTime"])
            end = datetime.fromisoformat(schedule["endTime"])

            # If the API gives naive datetimes, interpret them as Jerusalem time
            if start.tzinfo is None:
                start = start.replace(tzinfo=JERUSALEM)

            if end.tzinfo is None:
                end = end.replace(tzinfo=JERUSALEM)

            event.begin = start
            event.end = end

            event.location = ", ".join(
                room["name"]["en"]
                for room in schedule.get("rooms", [])
            )

            event.description = (
                f"Course: {course['name']}\n"
                f"Course Code: {course_code}\n"
                f"Exam: {assignment_name}\n"
                f"Semester: {schedule['periodName']['en']}\n"
                f"Moed: {schedule['moed']}"
            )

            calendar.events.add(event)


def main():
    calendar = Calendar()

    with open(SOURCE_FILE) as f:
        courses = [line.strip() for line in f if line.strip()]

    for course in courses:
        try:
            print(f"Processing {course}")
            add_course_events(calendar, course)
        except Exception as e:
            print(f"Failed {course}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    print(f"\nSaved {OUTPUT_FILE}")
    print(f"Total events: {len(calendar.events)}")


if __name__ == "__main__":
    main()
