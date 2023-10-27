from .imports import *
from . import _utils

def lektier(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/material_lektieoversigt.aspx?elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    soup = BeautifulSoup(resp.text, "html.parser")

    lektier = []

    _dato = soup.find("span", {"id": "s_m_masterfooternowSpan"}).text.split("  ")[0].replace("-", "/").split("/")
    for tr in soup.find_all("tr"):
        modul = tr.find("a", class_="s2skemabrik")
        if modul is None:
            continue

        dato = tr.find("th").find("b").text.split(" ")[1]
        if dato.split("/")[1] == "1" and _dato[1] != "1":
            dato += f'-{int(_dato[2])+1}'
        else:
            dato += f'-{int(_dato[2])}'

        modulDict = _utils.skemaBrikExtract(dato, modul)
        try:
            lektie = {
                "dato": dato,
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