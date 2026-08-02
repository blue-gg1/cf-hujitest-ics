import textwrap, requests, json
from random import randint
import pprint
import pandas as pd 
import ics




def GetNamesFromShnaton(CourseNumber: int, Year: int):
    # get the json from the shanton:
    # TODO: fake headers to look like a browser (only needed if blocked.)
    ShnatonJson = requests.get("https://shnaton.huji.ac.il/api/courses/code/"+CourseNumber+"?year="+str(Year)) 

    if ShnatonJson.status_code == 200: # dont trip over the network TODO: make this an assert.
        ShantonObject = json.loads(ShnatonJson.content)
        if ShantonObject[0]['code'] == CourseNumber: # make sure we got the right course. TODO: make this an assert.
            print(CourseNumber + "good")
        else:
            print(CourseNumber + "bad")
            print("issue with the shanton id abort.")
            exit()
        return(ShantonObject[0]['name']['he'])
    else:
        print("page is not 200, abort")
        exit()

def StringCleaner(NameOfClass):
    # clean up the string
    # TODO: count the amount of spaces as not to insert too many line retuns 

    # StringToBeRevesed = ((NameOfClass[0]['name']['he']).replace(' ', '\n')).replace('(',"}").replace(')',"{")
    # StringToBeRevesed = (((NameOfClass).replace(' ', '\n')).replace('(',"").replace(')',"")).replace("-","")

    StringToBeRevesed = ((NameOfClass).replace(' ', '\n')).replace("-","")
        
    return(StringToBeRevesed)

def GetCourseFromFile(FileName):
    # read the file from disk.
    with open(FileName,'r') as SourceList:
        SourceData = SourceList.read().splitlines()
    return(SourceData)

def GetDoubleSemesterFromShnaton(CourseNumber: int, Year: int):
    # get the json from the shanton:
    # TODO: fake headers to look like a browser (only needed if blocked.)
    ShnatonJson = requests.get("https://shnaton.huji.ac.il/api/courses/code/"+CourseNumber+"?year="+str(Year)) 

    if ShnatonJson.status_code == 200: # dont trip over the network TODO: make this an assert.
        ShnatonJsonObject = json.loads(ShnatonJson.content)
        ShnatonId = ShnatonJsonObject[0]['id']   
        print(ShnatonId)
    else:
        print("page is not 200, abort")
        exit()

    try:
        if (ShnatonJsonObject[0]['coursePeriodName']['en']) == "Semester A or B":
            BothSemester = "SemAB"
        elif (ShnatonJsonObject[0]['coursePeriodName']['en']) == "Semester A":
            BothSemester = "SemA"
        elif (ShnatonJsonObject[0]['coursePeriodName']['en']) == "Semester B":
            BothSemester = "SemB"
        else:
            BothSemester = False
            print('semster issue. is the class given?')
            # exit()
        pass
    except:
        BothSemester = False
        print('semster issue. is the class given?')
        # exit()
    return(BothSemester)
    

def GetShnatonIdFromShnaton(CourseNumber: int, Year: int):
    # get the json from the shanton:
    # TODO: fake headers to look like a browser (only needed if blocked.)
    ShnatonJson = requests.get(f"https://shnaton.huji.ac.il/api/courses/code/{CourseNumber}?year={str(Year)}")

    if ShnatonJson.status_code == 200: # dont trip over the network TODO: make this an assert.
        ShnatonJsonObject = json.loads(ShnatonJson.content)
        ShnatonId = ShnatonJsonObject[0]['id']   
    else:
        print("shanton class id does not match")
        exit()
    return(ShnatonId)


def ClankerGetTestDateFromShnaton(ShnatonId: int, Year: int):
    response = requests.get(f"https://shnaton.huji.ac.il/api/assignments?year={Year}&courseId={ShnatonId}")
    assignments = response.json()

    TestDates = []

    for assignment in assignments:
        name = assignment["assignmentDefinition"]["name"]["en"]

        if name in ("Written test", "Mid-term Exams"):
            for schedule in assignment.get("schedules", []):
                TestDates.append(schedule["startTime"])
                TestDates.append(schedule["endTime"])
    # pprint.pp(assignments)

    return(TestDates)



# for Course in CourseList:
#     print(Course)
#     CourseName = GetNamesFromShnaton(Course, 2027) # year is used for the api
#     # TextForImage = get_display(CourseName)
#     TextForImage = StringCleaner(CourseName)

#     AddTextToImageAndDealWithString(TextForImage, Course+".png", "2026-2027", Course) # the year here is any text to be added to the bottom of the logo.





def ClankerRetriveData(Course, Year):
    print(Course)

    CourseName = GetNamesFromShnaton(Course, Year)
    ShnatonId = GetShnatonIdFromShnaton(Course, Year)
    BothSemester = GetDoubleSemesterFromShnaton(Course, Year)
    TestDates = ClankerGetTestDateFromShnaton(ShnatonId, Year)

    return {
        "Year":Year,
        "Course": Course,
        "CourseName": CourseName,
        "ShnatonId": ShnatonId,
        "Semester": BothSemester,
        "TestDates": TestDates,
    }


def main(Year, FileName):
    CourseList = GetCourseFromFile(FileName)
    rows = []

    for Course in CourseList:
        data = ClankerRetriveData(Course, Year)
        TextForImage = StringCleaner(data["CourseName"])
        rows.append(data)
        print(rows)
    df = pd.DataFrame(rows)
    print(df)

    df.to_csv("courses.csv", index=False, encoding="utf-8-sig")



main(2026, "Source")