from .imports import *

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
        "dagsNoter": []
    }

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
                try:
                    absid = re.search('absid=[0-9]+', modul["href"]).group().replace("absid=", "")
                except Exception:
                    absid = modul.get("href")

                modulDict = {
                    "navn": None,
                    "tidspunkt": None,
                    "hold": None,
                    "lærer": None,
                    "lokale": None,
                    "status": "normal",
                    "absid": absid,
                    "andet": None
                }

                modulDetaljer = modul
                statusClass = modulDetaljer.get("class")[2]
                if statusClass in statusDictionary:
                    modulDict["status"] = statusDictionary[modulDetaljer.get("class")[2]]
                else:
                    modulDict["status"] = modulDetaljer.get("class")[2]

                modulDetaljer = modulDetaljer["data-additionalinfo"].split("\n\n")[0].split("\n")

                for modulDetalje in modulDetaljer:
                    if (value := ": ".join(modulDetalje.split(": ")[1:])) != "":
                        if (navn := modulDetalje.split(": ")[0]) in renameDictionary:
                            navn = renameDictionary[navn]

                        modulDict[navn.lower()] = value
                    else:
                        try:
                            int(datetime.strptime(modulDetalje.split(": ")[0].split(" til")[0],
                                                  "%d/%m-%Y %H:%M").timestamp())
                            modulDict["tidspunkt"] = modulDetalje
                        except Exception:
                            modulDict["navn"] = modulDetalje.split(": ")[0]

                try:
                    modulDict["andet"] = modul["data-additionalinfo"].split("\n\n")[1]
                except Exception:
                    pass

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