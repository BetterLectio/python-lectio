from .imports import *
from . import _utils

def lektier(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/material_lektieoversigt.aspx?elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    soup = BeautifulSoup(resp.text, "html.parser")

    lektier = []

    for tr in soup.find_all("tr"):
        modul = tr.find("a", class_="s2skemabrik")
        if modul is None:
            continue
        modulDict = _utils.skemaBrikExtract(modul)
        try:
            lektie = {
                "dato": tr.find("th").get("b"),
                "aktivitet": modulDict,
                "note": tr.find_all("td")[1].text,
            }
            if tr.find("td", {"class": "ls-homework"}).find("a"):
                lektie["lektier"] = {
                    "beskrivelse": tr.find("td", {"class": "ls-homework"}).find("a").text,
                    "link": tr.find("td", {"class": "ls-homework"}).find("a").get("href")
                }
            else:
                lektie["lektier"] = {
                    "beskrivelse": tr.find("td", {"class": "ls-homework"}).text,
                    "link": f"https://www.lectio.dk/lectio/{self.skoleId}/aktivitet/aktivitetforside2.aspx?absid={modulDict['absid']}&elevid={self.elevId}" # næsten det samme alligevel
                }
        except:
            lektie = {
                "dato": tr.find("th").get("b"),
                "aktivitet": "se modul siden",
                "note": "se modul siden",
                "lektier": {
                    "beskrivelse": "se modul siden",
                    "link": "se modul siden"
                }
            }

        lektier.append(lektie)

    return lektier