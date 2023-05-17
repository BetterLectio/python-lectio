from .imports import *
import pprint

def get_grades(soup: BeautifulSoup, mode="type"):
    """Get a list of grades from a BeautifulSoup object

    Args:
        soup (BeautifulSoup): The BeautifulSoup object
        mode (string): The mode of the output

    Returns:
        dict: Grades
    """

    table = soup.find("table", {"id": "s_m_Content_Content_karakterView_KarakterGV"})

    rows = table.find_all("tr")
    headers = [ele.text.strip() for ele in rows[0].find_all("th")]


    if mode == "type":
        grades = {}

        for ele in rows[0].find_all("th"):
            headers.append(ele.text.strip())
            grades[ele.text.strip()] = []

        for row in rows[1:]:
            grade = dict([detail.lower().split(": ") for detail in row.find("div", {"class": "textCenter"}).get("title").split("\n")])

            rows = row.find_all("td")
            grade["hold"] = {"navn": rows[0].text, "id": rows[0].find("span").get("data-lectiocontextcard")}
            grade["fag"] = rows[1].text

            for i in range(len(rows) - 2):
                grade["karakter"] = rows[i + 2].text
                grades[headers[i + 2]].append(grade)

        return grades

    else: # if type == "table"
        grades = []
        for row in rows[1:]:
            grade = dict([detail.lower().split(": ") for detail in row.find("div", {"class": "textCenter"}).get("title").split("\n")])

            rows = row.find_all("td")
            grade["hold"] = {"navn": rows[0].text, "id": rows[0].find("span").get("data-lectiocontextcard")}
            grade["fag"] = rows[1].text
            grade["grades"] = [ele.text.strip() for ele in row.find_all("td")[2:]]

            grades.append(grade)

        return {
            "headers": headers,
            "grades": grades
        }


def get_grade_notes(soup: BeautifulSoup):
    """Get a list of notes from a BeautifulSoup object

    Args:
        soup (BeautifulSoup): The BeautifulSoup object

    Returns:
        dict: List of notes and headers
    """
    table = soup.find("table", {"id": "s_m_Content_Content_karakterView_KarakterNoterGrid"})
    rows = table.find_all("tr")
    headers = []
    grades = []
    for row in rows:
        if cols := row.find_all("th"):
            headers = [ele.text.strip() for ele in cols]
        elif cols := row.find_all("td"):
            grades.append([ele.text.strip() for ele in cols])

    return {
        "headers": headers,
        "notes": grades
    }

def karakterer(self, mode):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/grades/grade_report.aspx?elevid={self.elevId}&culture=da-DK"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    header = [
        th.text.replace("\xad", "").lower().replace(" ", "_")
        for th in soup.find("div", {"id": "printareaprotocolgrades"})
        .find("tr")
        .find_all("th")
    ]
    karakterer_list = []
    for tr in soup.find("div", {"id": "printareaprotocolgrades"}).find_all("tr")[1:]:
        karakter = {header[i]: td.text for i, td in enumerate(tr.find_all("td"))}
        karakterer_list.append(karakter)

    grades = get_grades(soup, mode)
    notes = get_grade_notes(soup)

    return {
        "karakterer": grades,
        "notes": notes,
        "protokollinjer": karakterer_list,
    }
