from .imports import *
from . import _utils

colorDict = {
    "prio1.auto": "rød",
    "prio2.auto": "gul",
    "prio3.auto": "grå",
    "prio4.auto": "grøn"
}

def forside(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    forsideDict = {
        "aktuelt": [],
        "kommunikation": {"beskeder": [], "dokumenter": []},
        "undervisning": {},
        "skema": []
    }

    for tr in soup.find("div", {"id": "s_m_Content_Content_aktueltIsland_pa"}).find_all("tr", {"class": "DashWithScroll textTop"}):
        content = tr.find("td", {"class": "infoCol"}).find("span")
        contentStr = str(content)
        for span in content.find_all("span", {"class": "bb_b"}):
            new = copy.copy(span)
            new.name = "strong"
            contentStr = contentStr.replace(str(span), str(new))

        forsideDict["aktuelt"].append({
            "punkt_farve": colorDict[tr.find("td", {"class": "iconCol"}).find("img").get("src").split("/")[-1]],
            "text": markdownify.markdownify(contentStr, heading_style="ATX").lstrip().rstrip().replace("\n\n", "\n"), #HTML til markdown det
        })


    kommunikation = soup.find("div", {"id": "s_m_Content_Content_kommIsland_pa"})
    for id, type in [["s_m_Content_Content_BeskederInfo", "beskeder"], ["s_m_Content_Content_DokumenterInfo", "dokumenter"]]:
        for tr in kommunikation.find("table", {"id": id}).find_all("tr"):
            tds = tr.find_all("td")
            try:
                forsideDict["kommunikation"][type].append({
                    "navn": tds[1].text,
                    "afsender": tds[2].find("span").get("title"),
                    "dato": tds[3].get("title"),
                    "id": re.search("id=\d+", str(tds[1].find("a").get("href"))).group().replace("id=", "")
                })
            except IndexError:
                pass

    undervisning = soup.find("div", {"id": "s_m_Content_Content_undervisningIsland_pa"})
    headings = undervisning.find_all("div", {"role": "heading"})
    tables = undervisning.find_all("table")

    for i in range(len(headings)):
        navn = headings[i].find("span", {"class": "dashboardLinkHeaderText"}).text.lower().replace(" ", "_")
        forsideDict["undervisning"][navn] = []
        for tr in tables[i].find_all("tr"):
            tds = tr.find_all("td")
            try:
                forsideDict["undervisning"][navn].append({
                    "navn": tds[1].text,
                    "dato": tds[2].get("title"),
                    "id": re.search("id=\d+", str(tds[1].find("a").get("href"))).group().replace("id=", ""),
                    "punkt_farve": colorDict[tds[0].find("img").get("src").split("/")[-1]],
                })
            except IndexError:
                pass

    for modul in soup.find("div", {"id": "s_m_Content_Content_skemaIsland_pa"}).find_all("a", {"class": "s2skemabrik"}):
        forsideDict["skema"].append(_utils.skemaBrikExtract(modul))

    return forsideDict