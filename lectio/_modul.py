from .imports import *

def modul(self, absid):
    resp = self.session.get(
        f"https://www.lectio.dk/lectio/{self.skoleId}/aktivitet/aktivitetforside2.aspx?absid={absid}")
    soup = BeautifulSoup(resp.text, "html.parser")

    modulDetaljer = {
        "aktivitet": None,
        "note": "",
        "lektier": "",
        "præsentation": "",
        "øvrigtIndhold": ""
    }

    try:
        modulDetaljer["note"] = soup.find("textarea", {"class": "activity-note"}).text.lstrip()
    except Exception:
        pass

    modulContent = soup.find("div", {"id": "s_m_Content_Content_tocAndToolbar_inlineHomeworkDiv"})
    last = ""
    for div in modulContent.find_all("div"):
        if div.get("style") == None:
            if (divText := div.text.lstrip().rstrip()) != "":
                last = divText.lower().title().replace(" ", "")
                last = last[0].lower() + last[1:]
        else:
            for element in str(div).replace(u'\xa0', u'\n').split("\n"):
                elementSoup = BeautifulSoup(element, "html.parser")
                if elementSoup.text != "":
                    if (elementWithHref := elementSoup.find("a", href=True)) != None:
                        href = elementWithHref.get('href')
                        if href.startswith(f"/lectio/{self.skoleId}"):
                            href = "https://www.lectio.dk" + href
                        modulDetaljer[last] += unicodedata.normalize("NFKD", f"[{elementSoup.text.rstrip().lstrip()}]({href})\n")
                    else:
                        modulDetaljer[last] += unicodedata.normalize("NFKD", elementSoup.text.rstrip().lstrip().replace(u"\xa0", u" ") + "\n")

    renameDictionary = {
        "Lærere": "Lærer",
        "Lokaler": "Lokale"
    }

    modulDict = {
        "navn": None,
        "tidspunkt": None,
        "hold": None,
        "lærer": None,
        "lokale": None,
        "absid": absid
    }
    for modulDetalje in soup.find("a", class_="s2skemabrik")["data-additionalinfo"].split("\n\n")[0].split("\n"):
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

    modulDetaljer["aktivitet"] = modulDict

    return modulDetaljer

def elevFeedback():
    pass