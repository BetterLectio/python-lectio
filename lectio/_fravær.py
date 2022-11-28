from .imports import *

def fravær(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/subnav/fravaerelev.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    fravær = {
        "generalt": [],
        "moduler": "ikke mulig endnu da jeg har 0% fravær"
    }
    for hold in soup.find("table", {"id": "s_m_Content_Content_SFTabStudentAbsenceDataTable"}).find_all("tr"):
        if hold.get("id") == None:
            row = hold.find_all("td")
            fravær["generalt"].append({
                "hold": row[0].text,
                "fravær_procent": row[1].text,
            })

    return fravær