from .imports import *

def opgave(self, exerciseid):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/ElevAflevering.aspx?elevid={self.elevId}&exerciseid={exerciseid}")
    soup = BeautifulSoup(resp.text, "html.parser")

    opgaveDict = {
        "oplysninger": {},
        "gruppemedlemmer": [],
        "afleveres_af": {},
        "opgave_indlæg": None
    }

    for tr in soup.find("table", {"class": "ls-std-table-inputlist"}).find_all("tr"):
        opgaveDict["oplysninger"][unicodedata.normalize("NFKD", tr.find("th").text.lower().replace(" ", "_"))] = unicodedata.normalize("NFKD", tr.find("td").text)

    for tr in soup.find("table", {"class": "ls-table-layout1 lf-grid"}).find_all("tr")[1:]:
        opgaveDict["gruppemedlemmer"].append(unicodedata.normalize("NFKD", tr.text.lstrip().rstrip()))

    header = soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr", {"class": ""})[0]
    headerIdentifiers = []
    for th in header.find_all("th")[1:]:
        headerIdentifiers.append(th.text.lower().replace(" ", "_"))

    for tr in soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr")[1:]:
        i = 0
        for td in tr.find_all("td")[1:]:
            print(td.text)
            print(headerIdentifiers[i])
            opgaveDict["afleveres_af"][headerIdentifiers[i]] = unicodedata.normalize("NFKD", td.text.lstrip())
            i += 1

    return opgaveDict
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

def afleverOpgave(self, exerciseid, file=None, note=None):
    pass