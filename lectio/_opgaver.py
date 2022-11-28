from .imports import *

def opgave(self, exerciseid):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/ElevAflevering.aspx?elevid={self.elevId}&exerciseid={exerciseid}")
    soup = BeautifulSoup(resp.text, "html.parser")

    opgaveDict = {
        "oplysninger": {},
        "gruppemedlemmer": [],
        "afleveres_af": {},
        "opgave_indlæg": []
    }

    for tr in soup.find("table", {"class": "ls-std-table-inputlist"}).find_all("tr"):
        if (identifier := unicodedata.normalize("NFKD", tr.find("th").text).lower().replace(" ", "_")) == "ansvarlig:":
            opgaveDict["oplysninger"][identifier] = {"navn": unicodedata.normalize("NFKD", tr.find("td").text), "bruger_id": tr.find("span").get("data-lectiocontextcard")}
        elif identifier == "opgavebeskrivelse:":
            opgaveDict["oplysninger"][identifier] = f'[{unicodedata.normalize("NFKD", tr.find("td").text).lstrip().rstrip()}](https://www.lectio.dk{tr.find("a").get("href")})'
        else:
            opgaveDict["oplysninger"][identifier] = unicodedata.normalize("NFKD", tr.find("td").text)

    if soup.find_all("span", {"class": "islandHeader"})[1].text == "Gruppeaflevering":
        for tr in soup.find("table", {"class": "ls-table-layout1 lf-grid"}).find_all("tr")[1:]:
            opgaveDict["gruppemedlemmer"].append({"navn": unicodedata.normalize("NFKD", tr.text.lstrip().rstrip()), "bruger_id": tr.find("span").get("data-lectiocontextcard")})

    header = soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr", {"class": ""})[0]
    headerIdentifiers = []
    for th in header.find_all("th")[1:]:
        headerIdentifiers.append(th.text.lower().replace(" ", "_"))

    for tr in soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"}).find_all("tr")[1:]:
        i = 0
        for td in tr.find_all("td")[1:]:
            if (identifier := headerIdentifiers[i]) == "afsluttet":
                opgaveDict["afleveres_af"][identifier] = td.find("input").get("checked") == "checked"
            elif identifier == "elev":
                opgaveDict["afleveres_af"][identifier] = {"navn": unicodedata.normalize("NFKD", td.text).lstrip().rstrip(), "bruger_id": td.find_all("span")[1].get("data-lectiocontextcard")}
            else:
                opgaveDict["afleveres_af"][identifier] = unicodedata.normalize("NFKD", td.text).lstrip().rstrip()
            i += 1

    indlægHtml = soup.find("table", {"id": "m_Content_RecipientGV"})
    indlægHeader = [header.text.lower().replace(" ", "_") for header in indlægHtml.find_all("th")]

    for tr in indlægHtml.find_all("tr")[1:]:
        indlæg = {}
        i = 0
        for td in tr.find_all("td"):
            if (identifier := indlægHeader[i]) == "dokument" and (href := td.find("a").get('href')) != None:
                indlæg[identifier] = f"[{td.text.lstrip().rstrip()}](https://www.lectio.dk{href})"
            elif identifier == "bruger":
                indlæg[identifier] = {"navn": td.text.lstrip().rstrip(), "bruger_id": td.find("span").get("data-lectiocontextcard")}
            else:
                indlæg[identifier] = td.text.lstrip().rstrip()
            i += 1

        opgaveDict["opgave_indlæg"].append(indlæg)

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