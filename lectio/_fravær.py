from .imports import *

renameDictionary = {
    "Lærere": "Lærer",
    "Lokaler": "Lokale"
}
def fravær(self):
    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/subnav/fravaerelev.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    fravær = {
        "generalt": [],
        "moduler": {
            "manglende_fraværsårsager": [],
            "oversigt": []
        },
        "grafisk_oversigt": "https://www.lectio.dk" + soup.find("img", {"class": "fravaer_billede"}).get("src")
    }

    for hold in soup.find("table", {"id": "s_m_Content_Content_SFTabStudentAbsenceDataTable"}).find_all("tr"):
        if hold.get("id") == None:
            row = hold.find_all("td")
            fravær["generalt"].append({
                "hold": row[0].text,
                "fravær_procent": row[1].text,
            })

    resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/subnav/fravaerelev_fravaersaarsager.aspx?elevid={self.elevId}")
    soup = BeautifulSoup(resp.text, "html.parser")

    manglende = soup.find("table", {"id": "s_m_Content_Content_FatabMissingAarsagerGV"})
    if "Der er ingen manglende fraværsårsager..." not in str(manglende):
        for tr in manglende.find_all("tr")[1:]:
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

            tds = tr.find_all("td")

            fravær["moduler"]["manglende_fraværsårsager"].append({
                "type": tds[0].text.lstrip(),
                "uge": tds[1].text.lstrip(),
                "aktivitet": modulDict,
                "fravær": tds[3].text.lstrip(),
                "fraværstype": tds[4].text.lstrip(),
                "registreret": tds[5].text.lstrip(),
                "lærer": tds[6].text.lstrip(),
                "bemærkning": None
            })

    oversigt = soup.find("table", {"id": "s_m_Content_Content_FatabAbsenceFravaerGV"})
    if "Der er ikke indtastet nogen fraværsårsager" not in str(oversigt):
        for tr in oversigt.find_all("tr")[1:]:
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

            tds = tr.find_all("td")

            fravær["moduler"]["oversigt"].append({
                "type": tds[0].text.lstrip(),
                "uge": tds[1].text.lstrip(),
                "aktivitet": modulDict,
                "fravær": tds[3].text.lstrip(),
                "fraværstype": tds[4].text.lstrip(),
                "registreret": tds[5].text.lstrip(),
                "lærer": tds[6].text.lstrip(),
                "bemærkning": tds[7].text.lstrip(),
                "årsag": tds[8].text.lstrip(),
                "årsagsnote": tds[9].text.lstrip(),
            })

    return fravær