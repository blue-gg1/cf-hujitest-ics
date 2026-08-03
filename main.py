import requests
from ics import Calendar, Event
from datetime import datetime
from zoneinfo import ZoneInfo
import os
# define the vars up here.
JERUSALEM = ZoneInfo("Asia/Jerusalem")
YEAR = 2026
SOURCE_FILE = "source.old.txt" # one course code per line
# SOURCE_FILE = "source" # one course code per line
OUTPUT_FILE = "HUJI_Exams_"+str(YEAR)+".ics"


def get_course(course_code):
    ShantonYearUrl = f"https://shnaton.huji.ac.il/api/courses/code/{course_code}?year={YEAR}"
    r = requests.get(ShantonYearUrl)
    r.raise_for_status()

    data = r.json()[0]

    return {
        "id": data["id"],
        "name": data["name"]["he"],
    }

def GetShantonIdDepthJson(Shnaton_course_id):
    r = requests.get(
        f"https://shnaton.huji.ac.il/api/assignments?year={YEAR}&courseId={Shnaton_course_id}"
    )
    r.raise_for_status()
    return {
        "AssignmentsJson":r.json(),
        "Shnaton_course_id":Shnaton_course_id
        }

def add_course_events(calendar, course_code):
    course = get_course(course_code)
    MetaDataLinks = MetaDataTags(course_code)
    ShantonInDepthjson = GetShantonIdDepthJson(course["id"])
    assignment = ShantonInDepthjson["AssignmentsJson"]
    Shnaton_course_id = ShantonInDepthjson["Shnaton_course_id"]

    for assignment in assignment:

        assignment_name = assignment["assignmentDefinition"]["name"]["en"]

        # Only exams
        if assignment_name not in ("Written test", "Mid-term Exams", "First partial test", "Second partial test"):
            continue

        for schedule in assignment.get("schedules", []):

            event = Event()

            event.name = f"בחינה ב- {course['name']} ({course_code})"

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
                room["name"]["he"]
                for room in schedule.get("rooms", [])
            )

            event.description = (
                f"<b>Subject to change. Always check the <a href={MetaDataLinks["Shanton"]}>Shanton</a> or <a href={MetaDataLinks['Orbit']}>Orbit</a> for the most up-to-date info</b>\n"
                f"Location: {event.location}\n"
                f"Course: {course['name']}\n"
                f"Course Code: {course_code}\n"
                f"Exam: {assignment["assignmentDefinition"]["name"]["he"]}\n"
                f"Semester: {schedule['periodName']['he']}\n"
                f"Moed: {schedule['moed']}\n"
                f"Test Start: {start}\n"
                f"Test End: {end}\n\n\n"
                f"<i>This was last updated at: {MetaDataLinks["LastUpdate"]}</i>"
            )
            event.uid = f"{YEAR}-{course_code}-{(schedule['periodName']['en'].replace(" ","-"))}-{schedule['moed']}-{assignment["assignmentDefinition"]["name"]["en"]}-{Shnaton_course_id}@huji.local"

            calendar.events.add(event)

def MetaDataTags(course_code):
    ShnatonLink = f'https://shnaton.huji.ac.il/course/{course_code}'
    OrbitLink = f'https://orbitlive.huji.ac.il/StudentAssignmentTermList.aspx'
    LastUpdated = f'{datetime.now()}'
    
    return {
        "Shanton": ShnatonLink,
        "Orbit":OrbitLink,
        "LastUpdate":LastUpdated
    }
def moveics(IcsFileName, Path):
    os.replace(IcsFileName, Path+IcsFileName)

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
    moveics(OUTPUT_FILE, "prod/")


if __name__ == "__main__":
    main()
