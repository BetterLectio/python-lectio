from .imports import *

def lektier(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/material_lektieoversigt.aspx?elevid={self.elevId}")

    soup = BeautifulSoup(resp.text, "html.parser")

    lektier = []

    renameDictionary = {
        "Lærere": "Lærer",
        "Lokaler": "Lokale"
    }

    for tr in soup.find_all("tr"):
        modul = tr.find("a", class_="s2skemabrik")
        modulDetaljer = modul["data-additionalinfo"].split("\n\n")[0].split("\n")

        modulDict = {
            "navn": None,
            "tidspunkt": None,
            "hold": None,
            "lærer": None,
            "lokale": None,
            "absid": re.search('absid=[0-9]+', modul["href"]).group().replace("absid=", "")
        }
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

        lektie = {
            "dato": tr.find("th").get("b"),
            "aktivitet": modulDict,
            "note": tr.find_all("td")[1].text,
            "lektier": {
                "beskrivelse": tr.find("td", {"class": "ls-homework"}).find("a").text,
                "link": tr.find("td", {"class": "ls-homework"}).find("a").get("href")
            }
        }

        lektier.append(lektie)

    return lektier