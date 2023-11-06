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

        modulDict = _utils.skemaBrikExtract("", modul)
        try:
            lektie = {
                "dato": modulDict["tidspunkt"],
                "aktivitet": modulDict,
                "note": tr.find_all("td")[1].text,
            }
            tds = tr.find_all("td")
            lektie["lektier"] = {
                "beskrivelse": tds[2].text,
                "link": tds[2].find("a").get("href")
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