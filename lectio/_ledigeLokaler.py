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

def optagedeLokaler(self):
    lokaler = list(self.informationer()["lokaler"].values())

    requests = len(lokaler)/30
    if requests - int(requests) == 0:
        requests = int(requests)
    else:
        requests = int(requests+1) # +1 for at runde op

    urls = []
    for _ in range(requests):
        urls.append(f"https://www.lectio.dk/lectio/681/SkemaAvanceret.aspx?type=skema&lokalesel={','.join(lokaler[0:30]).replace('RO', '')}")
        lokaler = lokaler[30:]

    lokaler = {}
    for url in urls:
        resp = self.session.get(url)
        if resp.url != url:
            raise Exception("lectio-cookie udløbet")
        soup = BeautifulSoup(resp.text, "html.parser")

        i = 0
        for dag in soup.find_all("div", class_="s2skemabrikcontainer"):
            if i != 0:
                dag = BeautifulSoup(str(dag), "html.parser")
                for modul in dag.find_all("a", class_="s2skemabrik"):
                    modulDict = _utils.skemaBrikExtract(modul)
                    if modulDict["status"] != "aflyst":
                        try:
                            lokaler[modulDict["lokale"]].append(modulDict["tidspunkt"])
                        except KeyError:
                            lokaler[modulDict["lokale"]] = [modulDict["tidspunkt"]]
            i += 1

    return lokaler