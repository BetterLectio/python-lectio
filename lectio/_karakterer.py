from .imports import *

def karakterer(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/grades/grade_report.aspx?elevid={self.elevId}&culture=da-DK"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    header = []
    for th in soup.find("div", {"id": "printareaprotocolgrades"}).find("tr").find_all("th"):
        header.append(th.text.replace("\xad", "").lower().replace(" ", "_"))

    karaktererList = []
    for tr in soup.find("div", {"id": "printareaprotocolgrades"}).find_all("tr")[1:]:
        i = 0
        karakter = {}
        for td in tr.find_all("td"):
            karakter[header[i]] = td.text
            i += 1
        karaktererList.append(karakter)

    return karaktererList