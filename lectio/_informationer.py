from .imports import *

def informationer():
    # https://www.lectio.dk/lectio/681/FindSkemaAdv.aspx
    pass

def lærere(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/FindSkema.aspx?type=laerer")
    soup = BeautifulSoup(resp.text, "html.parser")

    lærere = []
    for lærer in soup.find_all("a"):
        if "data-lectiocontextcard" in str(lærer):
            lærere.append({"navn": lærer.text, "lærerid": lærer["href"].split("laererid=")[1]})

    return lærere

def elever(self, forbogstav, retry=False):
    elever = []

    # if forbogstav != None:
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/FindSkema.aspx?type=elev&forbogstav={forbogstav}")
    soup = BeautifulSoup(resp.text, "html.parser")
    successful = False
    for elev in soup.find_all("a"):
        if "data-lectiocontextcard" in str(elev):
            elever.append({"navn": elev.getText(), "elevid": elev["href"].split("elevid=")[1]})
            successful = True

    if successful:
        return elever
    elif not retry:
        self.login()
        return self.elever(retry=True)
    else:
        return False

def fåElev(self, elevId):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    elev = {
        "navn": soup.find("div", {"class": "maintitle"}).text.replace("Eleven ", "").replace(" - Skema", ""),
        "billede": soup.find("img", {"id": "s_m_HeaderContent_picctrlthumbimage"}).get("src")
    }

    return elev