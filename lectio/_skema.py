from .imports import *
from . import _utils

def skema(self, retry=False, uge=None, år=None, elevId=None):
    if elevId == None:
        elevId = self.elevId

    if uge == None and år == None:
        resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}")
    elif uge != None and år != None:
        uge = str(uge)
        år = str(år)
        if len(uge) == 1:
            uge = "0" + uge
        resp = self.session.get(
            f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}&week={uge}{år}")
    else:
        raise Exception("Enten skal hverken uge og år være i brug ellers skal både uge og år være i brug")

    soup = BeautifulSoup(resp.text, "html.parser")

    skema = {
        "modulTider": {},
        "ugeDage": [],
        "moduler": [],
        "dagsNoter": [],
        "hold": [],
        "grupper": []
    }

    holdOgGrupper = soup.find("div", {"id": "s_m_Content_Content_holdElementLinkList"})
    for tr in holdOgGrupper.find_all("tr"):
        content = tr.find_all("li")
        if "Hold" in str(tr.find("th")):
            for hold in content:
                skema["hold"].append({"navn": hold.text, "id": hold.find("a").get("href").split("holdelementid=")[1]})
        else:
            for gruppe in content:
                skema["grupper"].append({"navn": gruppe.text, "id": gruppe.find("a").get("href").split("holdelementid=")[1]})

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

    successful = False
    i = 0

    renameDictionary = {
        "Lærere": "Lærer",
        "Lokaler": "Lokale"
    }

    statusDictionary = {
        "s2brik": "normal",
        "s2cancelled": "aflyst",
        "s2changed": "ændret",

        "s2bgboxeksamen": "eksamen"
    }

    for dag in soup.find_all("div", class_="s2skemabrikcontainer"):
        if i != 0:
            dag = BeautifulSoup(str(dag), "html.parser")
            for modul in dag.find_all("a", class_="s2skemabrik"):
                modulDict = _utils.skemaBrikExtract(modul)
                skema["moduler"].append(modulDict)
        i += 1

    if len(skema) > 0:
        successful = True

    if successful:
        return skema
    elif not retry:
        self.login()
        return self.skema(retry=True)
    else:
        return False