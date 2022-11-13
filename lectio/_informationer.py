from .imports import *

def informationer(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/FindSkemaAdv.aspx")
    soup = BeautifulSoup(resp.text, "html.parser")

    informationerDict = {}

    for section in soup.find_all("section", {"class": "island"}):
        sectionName = section.find("span", {"class": "islandHeader"}).text.lower().replace(" ", "_")
        informationerDict[sectionName] = {}
        select = section.find("select")
        if select != None:
            for option in select.find_all("option"):
                informationerDict[sectionName][option.text] = option.get("value")

    return informationerDict

def fåBruger(self, brugerId):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/contextcard/contextcard.aspx?lectiocontextcard={brugerId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    titel = soup.find("span").text

    bruger = {
        "navn": titel.split(" - ")[-1],
        "pictureid": None,
        "type": titel.split(" - ")[0].lower()
    }

    try:
        bruger["pictureid"] = re.search("pictureid=\d+", soup.find("img").get("src")).group().replace("pictureid=", "")
    except AttributeError:
        pass

    if bruger["type"] == "lærer":
        bruger["hold"] = {}
        for hold in soup.find("table", {"class": "textTop"}).find_all("a"):
            bruger["hold"][hold.text] = re.search("holdelementid=\d+", hold.get("href")).group().replace("holdelementid=", "")
    else:
        bruger["stamklasse"] = soup.find("table", {"class": "textTop"}).find_all("td")[1].text

    return bruger

def fåElev(self, elevId):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    elev = {
        "navn": soup.find("div", {"class": "maintitle"}).text.replace("Eleven ", "").replace(" - Skema", ""),
        "billede": soup.find("img", {"id": "s_m_HeaderContent_picctrlthumbimage"}).get("src")
    }

    return elev