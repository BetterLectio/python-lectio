from .imports import *

def get_grades(soup: BeautifulSoup):
    """Get a list of grades from a BeautifulSoup object

    Args:
        soup (BeautifulSoup): The BeautifulSoup object

    Returns:
        dict: List of grades and headers
    """
    table = soup.find("table", {"id": "s_m_Content_Content_karakterView_KarakterGV"})
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

def karakterer(self):
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

    grades = get_grades(soup)
    notes = get_grade_notes(soup)

    return {
        "karakterer": grades,
        "notes": notes,
        "protokollinjer": karakterer_list,
    }
