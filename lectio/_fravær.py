from .imports import *

def fravær(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/subnav/fravaerelev.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    fravær = []
    for hold in soup.find("table", {"id": "s_m_Content_Content_SFTabStudentAbsenceDataTable"}).find_all("tr"):
        if hold.get("id") == None:
            row = hold.find_all("td")
            fravær.append({
                "hold": row[0],
                "fravær_procent": row[1],
            })
            print(fravær)