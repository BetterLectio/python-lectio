import json
import requests
import re
import base64
from bs4 import BeautifulSoup
from datetime import datetime

class sdk:
    def __init__(self, brugernavn, adgangskode, skoleId, base64Cookie=None):
        self.session = requests.session()

        if base64Cookie == None:
            self.brugernavn = brugernavn
            self.adgangskode = adgangskode
            self.skoleId = skoleId

            self.login()
        else:
            cookie = json.loads(base64.b64decode(base64Cookie))
            self.skoleId = cookie["LastLoginExamno"]
            self.elevId = cookie["LastLoginElevId"]

            for identifier, value in cookie.items():
                self.session.cookies.set(identifier, value, domain="lectio.dk")



    def login(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-DK,en;q=0.9',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
        }
        resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/login.aspx", headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        payload = {}
        for payloadItem in soup.find_all({"input": {"type": "hidden"}}):
            payload[payloadItem.get('name')] = payloadItem.get('value')

        del payload["query"]
        del payload["m$defaultformbtn"]

        payload["__EVENTTARGET"] = "m$Content$submitbtn2"
        payload["m$Content$username"] = self.brugernavn
        payload["m$Content$password"] = self.adgangskode
        payload["m$Content$AutologinCbx"] = "on"
        payload["LectioPostbackId"] = ""

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-DK,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-length': str(len(json.dumps(payload, separators=(',', ':')))),
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.lectio.dk',
            'referer': f'https://www.lectio.dk/lectio/{self.skoleId}/login.aspx',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
        }
        resp = self.session.post(f"https://www.lectio.dk/lectio/{self.skoleId}/login.aspx", data=payload, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        successful = False
        for meta in soup.find_all({"meta": {"name": "msapplication-starturl"}}):
            if f"/lectio/{self.skoleId}/forside.aspx?" in str(meta.get("content")):
                self.elevId = meta.get("content").split("?elevid=")[1]
                successful = True
                break
        if not successful:
            raise Exception("Kunne ikke finde elev id. Rapporter venligst dette på Github")

    def base64Cookie(self):
        cookie = self.session.cookies.get_dict()
        cookie["LastLoginElevId"] = self.elevId

        return base64.b64encode(json.dumps(cookie).encode())

    def fåSkoleId(self):
        resp = self.session.get("https://www.lectio.dk/lectio/681/forside.aspx")
        soup = BeautifulSoup(resp.text, "html.parser")

        for meta in soup.find_all({"meta": {"name": "msapplication-starturl"}}):
            if f"/lectio/{self.skoleId}/forside.aspx?" in str(meta.get("content")):
                return meta.get("content").split("?elevid=")[1]

        raise Exception("Kunne ikke finde elev id. Rapporter venligst dette på Github")


    def lektier(self, elevId=None):
        if elevId == None:
            elevId = self.elevId

        resp = self.session.get(f"https://www.lectio.dk/lectio/681/material_lektieoversigt.aspx?elevid={elevId}")

        soup = BeautifulSoup(resp.text, "html.parser")

        lektier = []

        renameDictionary = {
            "Lærere": "Lærer",
            "Lokaler": "Lokale"
        }

        for tr in soup.find_all("tr"):
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

            lektie = {
                "dato": tr.find("th").get("b"),
                "aktivitet": modulDict,
                "note": tr.find_all("td")[1].text,
                "lektier": {
                    "beskrivelse": tr.find("td", {"class": "ls-homework"}).find("a").text,
                    "link": tr.find("td", {"class": "ls-homework"}).find("a").get("href")
                }
            }

            lektier.append(lektie)

        return lektier

    def skema(self, retry=False, uge=None, år=None, elevId=None):
        if elevId == None:
            elevId = self.elevId

        if uge == None and år == None:
            resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}")
        elif uge != None and år != None:
            uge = str(uge)
            år = str(år)
            if len(uge) == 1:
                uge = "0" + uge
            resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}&week={uge}{år}")
        else:
            raise Exception("Enten skal hverken uge og år være i brug ellers skal både uge og år være i brug")

        soup = BeautifulSoup(resp.text, "html.parser")

        skema = {
            "modulTider": {},
            "ugeDage": [],
            "moduler": [],
            "dagsNoter": []
        }

        for modulTid in soup.find_all("div", {"class": "s2module-info"}):
            skema["modulTider"][modulTid.prettify().split("\n")[2].lstrip()] = modulTid.prettify().split("\n")[4].lstrip()

        for dag in soup.find("tr", {"class": "s2dayHeader"}).find_all("td"):
            if dag.text != "":
                skema["ugeDage"].append(dag.text)

        i = 0
        for dagsNoter in soup.find_all("td", {"class": "s2infoHeader s2skemabrikcontainer"}):
            skema["dagsNoter"].append({
                skema["ugeDage"][i]: []
            })
            for dagsNote in dagsNoter.find_all("a"):
                skema["dagsNoter"][i][skema["ugeDage"][i]].append(dagsNote.text.lstrip())
            i += 1

        successful = False
        i = 0

        renameDictionary = {
            "Lærere": "Lærer",
            "Lokaler": "Lokale"
        }

        for dag in soup.find_all("div", class_="s2skemabrikcontainer"):
            if i != 0:
                dag = BeautifulSoup(str(dag), "html.parser")
                for modul in dag.find_all("a", class_="s2skemabrik"):
                    modulDetaljer = modul["data-additionalinfo"].split("\n\n")[0].split("\n")

                    modulDict = {
                        "navn": None,
                        "tidspunkt": None,
                        "hold": None,
                        "lærer": None,
                        "lokale": None,
                        "absid": re.search('absid=[0-9]+', modul["href"]).group().replace("absid=", ""),
                        "andet": None
                    }
                    for modulDetalje in modulDetaljer:
                        if (value := ": ".join(modulDetalje.split(": ")[1:])) != "":
                            if (navn := modulDetalje.split(": ")[0]) in renameDictionary:
                                navn = renameDictionary[navn]

                            modulDict[navn.lower()] = value
                        else:
                            try:
                                int(datetime.strptime(modulDetalje.split(": ")[0].split(" til")[0], "%d/%m-%Y %H:%M").timestamp())
                                modulDict["tidspunkt"] = modulDetalje
                            except Exception:
                                modulDict["navn"] = modulDetalje.split(": ")[0]

                    try:
                        modulDict["andet"] = modul["data-additionalinfo"].split("\n\n")[1]
                    except Exception:
                        pass

                    skema["moduler"].append(modulDict)
            i += 1

        if len(skema) > 0:
            successful = True

        if successful:
            return skema
        elif not retry:
            self.login()
            return self.skema(retry=True)
        else:
            return False

    def fåElev(self, elevId):
        resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={elevId}")
        soup = BeautifulSoup(resp.text, "html.parser")

        elev = {
            "navn": soup.find("div", {"class": "maintitle"}).text.replace("Eleven ", "").replace(" - Skema", ""),
            "billede": soup.find("img", {"id": "s_m_HeaderContent_picctrlthumbimage"}).get("src")
        }

        return elev
    def elever(self, forbogstav, retry=False):
        elever = []

        # if forbogstav != None:
        resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/FindSkema.aspx?type=elev&forbogstav={forbogstav}")
        soup = BeautifulSoup(resp.text, "html.parser")
        successful = False
        for elev in soup.find_all("a"):
            if "data-lectiocontextcard" in str(elev):
                elever.append({"navn": elev.getText(), "elevid": elev["href"].split("elevid=")[1]})
                successful = True

        if successful:
            return elever
        elif not retry:
            self.login()
            return self.elever(retry=True)
        else:
            return False

        # Ikke gør det neden under da man får ip ban fra lektio

        # else:
        #   resp = self.session.get(f"https://www.lectio.dk/lectio/681/FindSkema.aspx?type=elev")
        #   soup = BeautifulSoup(resp.text, "html.parser")
        #   forbogstaver = []
        #   for forbogstav in soup.find_all("a"):
        #       if ' href="/lectio/681/FindSkema.aspx?type=elev&amp;forbogstav=' in str(forbogstav):
        #           forbogstaver.append(forbogstav.getText())

        #   for elev in soup.find_all("a"):
        #       if "data-lectiocontextcard" in str(elev):
        #           print(elev.getText())
        #           elever.append({"elevid": elev["href"].split("elevid=")[1], "navn": elev.getText()})

        #   for forbogstav in forbogstaver:
        #       resp = self.session.get(f"https://www.lectio.dk/lectio/681/FindSkema.aspx?type=elev&forbogstav={forbogstav}")
        #       soup = BeautifulSoup(resp.text, "html.parser")
        #       for elev in soup.find_all("a"):
        #           if "data-lectiocontextcard" in str(elev):
        #               print(elev.getText())
        #               elever.append({"elevid": elev["href"].split("elevid=")[1], "navn": elev.getText()})