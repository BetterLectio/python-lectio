from .imports import *
from . import _utils

def ledigeLokaler(self):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaAvanceret.aspx?type=aktuelleallelokaler&nosubnav=1&prevurl=FindSkemaAdv.aspx"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
    soup = BeautifulSoup(resp.text, "html.parser")

    ledigeLokalerDict = []
    for div in soup.find("div", {"id": "m_Content_LectioDetailIsland1_pa"}).find_all("div"):
        try:
            if div.get("id").startswith("printSingleControl"):
                ledigeLokalerDict.append({
                    "lokale": div.find("span").text,
                    "status": "ledigt" if "Der er ingen data..." in str(div) else "optaget"
                })
        except:
            pass

    return ledigeLokalerDict

def lokaleDagsorden(self, kunAktuelAfdeling=True):
    informationer = self.informationer()
    lokaler = list(informationer["lokaler"].values())
    lokaleNavne = list(informationer["lokaler"].keys())

    afdelingsLokaler = []
    afdelingsLokalerNavne = []
    if kunAktuelAfdeling:
        url = f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaAvanceret.aspx?type=aktuelleallelokaler&nosubnav=1&prevurl=FindSkemaAdv.aspx"
        resp = self.session.get(url)
        if resp.url != url:
            raise Exception("lectio-cookie udløbet")
        soup = BeautifulSoup(resp.text, "html.parser")
        for div in soup.find("div", {"id": "m_Content_LectioDetailIsland1_pa"}).find_all("div"):
            try:
                if div.get("id").startswith("printSingleControl"):
                    afdelingsLokaler.append(lokaler[lokaleNavne.index(div.find("span").text[7:])])
                    afdelingsLokalerNavne.append(div.find("span").text[7:])
            except:
                pass

        lokaler = afdelingsLokaler
        lokaleNavne = afdelingsLokalerNavne

    lokaleList = [{"navn": lokaleNavne[i], "id": lokaler[i], "moduler": []} for i in range(len(lokaler))]

    requests = len(lokaler) / 30
    if requests - int(requests) == 0:
        requests = int(requests)
    else:
        requests = int(requests + 1)  # +1 for at runde op

    urls = []
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(1)).strftime('%Y-%m-%d')
    for _ in range(requests):
        urls.append(f"https://www.lectio.dk/lectio/681/SkemaAvanceret.aspx?type=ShowListAll&starttime={today}T00:00:00&endtime={tomorrow}T00:00:00&dagsbemaerk=0&lokalesel={','.join(lokaler[0:30]).replace('RO', '')}")
        lokaler = lokaler[30:]


    for url in urls:
        resp = self.session.get(url)
        if resp.url != url:
            raise Exception("lectio-cookie udløbet")
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", {"id": "m_Content_ListRpt_ctl00_SkemaAvanceretListe_SkemaAdvListGV"})
        for row in table.find_all("tr")[1:]:
            info = row.find_all("td")
            if len(info[4].text) > 0:
                skemabrik = info[1].find("a", {"class": "s2skemabrik"})
                modulDict = _utils.skemaBrikExtract(skemabrik)
                _lokaler = info[4].text.split("\r\n")
                for lokale in _lokaler:
                    if modulDict["status"] != "aflyst":
                        lokaleList[lokaleNavne.index(lokale)]["moduler"].append(modulDict["tidspunkt"])

    return lokaleList