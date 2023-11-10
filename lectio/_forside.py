from .imports import *
from . import _utils

colorDict = {
    "prio1.auto": "rød",
    "prio2.auto": "gul",
    "prio3.auto": "grå",
    "prio4.auto": "grøn"
}

def forside(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx?elevid={self.elevId}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    forsideDict = {
        "aktuelt": [],
        "kommunikation": {"beskeder": [], "dokumenter": []},
        "undervisning": {},
        "skema": [],
        "eksamener": []
    }

    try:
        for tr in soup.find("div", {"id": "s_m_Content_Content_aktueltIsland_pa"}).find_all("tr", {"class": "DashWithScroll textTop"}):
            content = tr.find("td", {"class": "infoCol"}).find("span")
            contentStr = str(content)
            for span in content.find_all("span", {"class": "bb_b"}):
                new = copy.copy(span)
                new.name = "strong"
                contentStr = contentStr.replace(str(span), str(new))

            forsideDict["aktuelt"].append({
                "punkt_farve": "grå", # Hvis lectio tilføjer det igen: colorDict[tr.find("td", {"class": "iconCol"}).find("img").get("src").split("/")[-1]],
                "text": markdownify.markdownify(contentStr, heading_style="ATX").lstrip().rstrip().replace("\n\n", "\n"), #HTML til markdown det
            })
    except Exception:
        pass

    try:
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
    except Exception:
        pass

    try:
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
    except Exception:
        pass

    lastDate = ""
    dato = soup.find("span", {"id": "s_m_masterfooternowSpan"}).text.split("  ")[0].replace("-", "/").split("/")
    for element in soup.find("div", {"id": "s_m_Content_Content_skemaIsland_pa"}).find_all():
        try:
            if "s2dayHeaderSimple" in element.get("class"):
                if "I dag" in element.text:
                    lastDate = datetime.now().strftime("%d/%m-%Y")
                elif "I morgen" in element.text:
                    lastDate = (datetime.now() + timedelta(days=1)).strftime("%d/%m-%Y")
                else:
                    _dato = element.text.split(" ")[1].strip()
                    if _dato.split("/")[1] == "1" and dato[1] != "1":
                        lastDate = f'{element.text.split(" ")[1].strip()} - {int(dato[2])+1}'
                    else:
                        lastDate = f'{element.text.split(" ")[1].strip()} - {dato[2]}'
        except TypeError:
            if element.get("role") == "heading":
                forsideDict["skema"].append(_utils.skemaBrikExtract(lastDate, element.find("a", {"class": "s2skemabrik"})))

    try:  
        eksamener_table = soup.find("table", {"id": "s_m_Content_Content_EksamenerInfo"})
        for row in eksamener_table.find_all("tr"):
            tds = row.find_all("td")
            forsideDict["eksamener"].append({
                "navn": tds[1].text,
                "link": "https://www.lectio.dk" + tds[1].find("a").get("href"),
                "punkt_farve": colorDict[tds[0].find("img").get("src").split("/")[-1]],
            })
    except Exception:
        pass

    return forsideDict