from .imports import *
from . import _utils

def skema(self, uge=None, år=None, id=None):
    skema = {
        "overskrift": "",
        "modulTider": {},
        "ugeDage": [],
        "moduler": [],
        "dagsNoter": []
    }

    url = f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?"
    if id[0] == "U":
        bruger = self.fåBruger(brugerId=id)
        if bruger["type"] == "elev":
            id = "S" + bruger["id"]
        elif bruger["type"] == "lærer":
            id = "T" + bruger["id"]

    if id == None:
        url += f"type=elev&elevid={self.elevId}"
        skema["hold"] = []
        skema["grupper"] = []
        skema["type"] = "elev"
    elif id[0] == "S": # Elev
        url += f"type=elev&elevid={id[1:]}"
        skema["hold"] = []
        skema["grupper"] = []
        skema["type"] = "elev"
    elif id[0] == "T": # Lærer
        url += f"type=laerer&laererid={id[1:]}"
        skema["hold"] = []
        skema["type"] = "lærer"

    elif id[0] == "C": # Klasse
        url += f"type=stamklasse&klasseid={id[1:]}"
        skema["hold"] = []
        skema["grupper"] = []
        skema["type"] = "klasse"
    elif id[0:2] == "RE": # Ressource
        url += f"type=lokale&nosubnav=1&id={id[2:]}"
        skema["type"] = "ressource"
    elif id[0] == "R": # Lokale
        url += f"type=lokale&nosubnav=1&id={id[1:]}"
        skema["type"] = "lokale"
    elif id[0:2] == "HE": # Hold Element
        url += f"type=holdelement&holdelementid={id[2:]}"
        skema["type"] = "hold"
    elif id[0] == "G": # Gruppe
        url += f"type=holdelement&holdelementid={id[1:]}"
        skema["type"] = "gruppe"

    if uge != None and år != None:
        uge = str(uge)
        år = str(år)
        if len(uge) == 1:
            uge = "0" + uge
        url += f"&week={uge}{år}"
    elif uge != None or år != None:
        raise Exception("Enten skal hverken uge og år være i brug ellers skal både uge og år være i brug")

    resp = self.session.get(url)

    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    soup = BeautifulSoup(resp.text, "html.parser")

    skema["overskrift"] = soup.find("div", {"id": "s_m_HeaderContent_MainTitle"}).text

    if id == None or id[0] == "S" or id[0] == "C":
        holdOgGrupper = soup.find("div", {"id": "s_m_Content_Content_holdElementLinkList"})
        for tr in holdOgGrupper.find_all("tr"):
            content = tr.find_all("li")
            if "Hold" in str(tr.find("th")):
                for hold in content:
                    skema["hold"].append({"navn": hold.text, "id": hold.find("a").get("href").split("holdelementid=")[1]})
            else:
                for gruppe in content:
                    skema["grupper"].append({"navn": gruppe.text, "id": gruppe.find("a").get("href").split("holdelementid=")[1]})
    elif id[0] == "T":
        skema["hold"] = self.fåBruger(brugerId=id)["hold"]


    for modulTid in soup.find_all("div", {"class": "s2module-info"}):
        skema["modulTider"][modulTid.prettify().split("\n")[2].lstrip()] = modulTid.prettify().split("\n")[4].lstrip()



    for dag in soup.find("tr", {"class": "s2dayHeader"}).find_all("td"):
        if dag.text != "":
            skema["ugeDage"].append(dag.text)

    i = 0
    for dagsNoter in soup.find_all("td", {"class": "s2infoHeader s2skemabrikcontainer"}):
        skema["dagsNoter"].append({
            skema["ugeDage"][i]: []
        })
        for dagsNote in dagsNoter.find_all("a"):
            skema["dagsNoter"][i][skema["ugeDage"][i]].append(dagsNote.text.lstrip())
        i += 1

    i = 0

    for dag in soup.find_all("div", class_="s2skemabrikcontainer"):
        if i != 0:
            dag = BeautifulSoup(str(dag), "html.parser")
            for modul in dag.find_all("a", class_="s2skemabrik"):
                modulDict = _utils.skemaBrikExtract(modul)
                skema["moduler"].append(modulDict)
        i += 1

    return skema

def holdTilFag(self, holdId):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/contextcard/contextcard.aspx?lectiocontextcard={holdId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    return {"fag": soup.find("td", {"class": "textTop"}).find_all("td")[1].text}