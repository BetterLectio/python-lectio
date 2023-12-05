from .imports import *
from . import _utils

def modulHtml(self, absid):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/aktivitet/aktivitetforside2.aspx?absid={absid}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")

    modulDetaljer = {
        "aktivitet": None,
        "note": "",
        "lektier": "",
        "præsentation": "",
        "øvrigt_indhold": ""
    }

    soup = BeautifulSoup(resp.text, "html.parser")

    modulDetaljer["aktivitet"] = _utils.skemaBrikExtract("", soup.find("a", class_="s2skemabrik"))

    try:
        modulDetaljer["note"] = soup.find("textarea", {"class": "activity-note"}).prettify()
    except AttributeError:
        pass

    last = ""
    for indhold in soup.find("div", {"id": "s_m_Content_Content_tocAndToolbar_inlineHomeworkDiv"}).find_all("div", recursive=False):
        if indhold.get("id"):
            modulDetaljer[last] += indhold.prettify()
        else:
            last = indhold.text.strip().lower().replace(" ", "_")
            modulDetaljer[last] = ""

    return modulDetaljer

def modul(self, absid):
    url = f"https://www.lectio.dk/lectio/{self.skoleId}/aktivitet/aktivitetforside2.aspx?absid={absid}"
    resp = self.session.get(url)
    if resp.url != url:
        raise Exception("lectio-cookie udløbet")
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
        if div.get("id") == None:
            if (divText := div.text.lstrip().rstrip()) != "" and divText != "Vis fuld skærm":
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

    årstal = soup.find("span", {"id": "s_m_masterfooternowSpan"}).text.split("  ")[0].split("-")[1] # Upræcis men virker det meste af tiden
    dato = soup.find("div", {"class": "s2skemabrikcontent"}).text.split(" ")[1] + "-" + årstal
    modulDetaljer["aktivitet"] = _utils.skemaBrikExtract(dato, soup.find("a", class_="s2skemabrik"))

    return modulDetaljer

def elevFeedback():
    pass