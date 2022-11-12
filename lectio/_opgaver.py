from .imports import *

def opgaver(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/OpgaverElev.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    opgaver = []
    header = []

    _header = soup.find("tr")
    for th in _header.find_all("th"):
        header.append(th.text.lower().replace("\xad", "-"))

    for opgave in soup.find_all("tr")[1:]:
        opgaveDict = {}

        i = 0
        for td in opgave.find_all("td"):
            if header[i] == "opgavetitel":
                opgaveDict["exerciseid"] = re.findall("exerciseid=\d+", td.find("a", href=True).get("href"))[0].replace(
                    "exerciseid=", "")

            opgaveDict[header[i]] = td.text.lstrip()
            i += 1

        opgaver.append(opgaveDict)

    return opgaver

def opgave(self, exerciseid):
    pass

def afleverOpgave(self, exerciseid, file=None, note=None):
    pass