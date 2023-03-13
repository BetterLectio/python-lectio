from .imports import *

def spørgeskemaer(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/spoergeskema/spoergeskema_rapport.aspx?type=mine&elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table", {"id": "s_m_Content_Content_SpørgeskemaerÅbneForSvarGV"}).find_all("tr")

    headers = []
    for th in table[0].find_all("th"):
        headers.append(th.text.lower())

    spørgeskemaerDict = {"åbne_for_besvarelse": [], "åbne_for_rapportering": []}
    for tr in table[1:]:
        spørgeskemaDict = {}
        i = 0
        for td in tr.find_all("td"):
            spørgeskemaDict[headers[i]] = td.text.lstrip()
            i += 1
        spørgeskemaDict["id"] = re.search("id=\d+", str(tr.find("a").get("href"))).group().replace("id=", "")
        spørgeskemaerDict["åbne_for_besvarelse"].append(spørgeskemaDict)

    table = soup.find("table", {"id": "s_m_Content_Content_SpørgeskemaerÅbneForRapporteringGV"}).find_all("tr")

    headers = []
    for th in table[0].find_all("th"):
        headers.append(th.text.lower())

    for tr in table[1:]:
        spørgeskemaDict = {}
        i = 0
        for td in tr.find_all("td"):
            spørgeskemaDict[headers[i]] = td.text.lstrip()
            i += 1
        spørgeskemaDict["id"] = re.search("id=\d+", str(tr.find("a").get("href"))).group().replace("id=", "")
        spørgeskemaerDict["åbne_for_rapportering"].append(spørgeskemaDict)

    return spørgeskemaerDict