import json
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

class sdk:
    def __init__(self, brugernavn, adgangskode, skoleId):
        self.brugernavn = brugernavn
        self.adgangskode = adgangskode
        self.skoleId = skoleId

        self.session = requests.session()

        self.login()

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
            exit("Kunne ikke finde elev id. Rapporter venligst dette på Github")

    def skema(self, retry=False):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-DK,en;q=0.9,da-DK;q=0.8,da;q=0.7,en-US;q=0.6',
            'referer': f'https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={self.elevId}',
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
        resp = self.session.get(f"https://www.lectio.dk/lectio/{self.skoleId}/SkemaNy.aspx?type=elev&elevid={self.elevId}&showtype=1",
                            headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        successful = False
        skema = soup.find_all("a", class_="s2skemabrik")
        for modul in skema:
            modulDetailer = modul["data-additionalinfo"].split("\n\n")[0].split("\n")

            tidspunkt = modulDetailer[-4]
            hold = modulDetailer[-3].replace("Hold: ", "")
            lærer = modulDetailer[-2].replace("Lærere: ", "").replace("Lærer: ", "")
            lokale = modulDetailer[-1].replace("Lokale: ", "")

            unixTidspunkt = int(datetime.strptime(tidspunkt.split(" til")[0], "%d/%m-%Y %H:%M").timestamp())
            danskUnixTid = int(datetime.now(pytz.timezone('Europe/Copenhagen')).timestamp())

            tidTilTime = unixTidspunkt - danskUnixTid
            if tidTilTime > 0:
                successful = True
                break
        if successful:
            return {"tidspunkt": tidspunkt, "hold": hold, "lærer": lærer, "lokale": lokale}
        elif not retry:
            self.login()
            return self.skema(retry=True)
        else:
            return False