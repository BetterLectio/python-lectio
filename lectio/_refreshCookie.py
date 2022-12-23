from .imports import *

def refreshCookie(self):
    success = False
    error = None
    try:
        headers = {
            "cookie": f"lectiogsc={self.session.cookies['lectiogsc']}; autologinkey={self.session.cookies['autologinkey']}",
        }
        resp = requests.get(f"https://www.lectio.dk/lectio/{self.skoleId}/forside.aspx", headers=headers, allow_redirects=False)
        newSessionId = resp.cookies["ASP.NET_SessionId"]
        self.session.cookies.set('ASP.NET_SessionId', newSessionId, domain='lectio.dk', path='/')

        success = True
    except Exception as e:
        error = e

    return {"success": success, "error": error}