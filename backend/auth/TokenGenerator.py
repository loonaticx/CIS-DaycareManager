import base64
import datetime
import time


# Very basic auth token

class TokenGenerator:

    def _encrypt(self, ipaddr):
        expiryTime = int(time.mktime(datetime.datetime(2024, 12, 1, 23, 59).timetuple()))
        return base64.b64encode(f"{ipaddr}_{expiryTime}".encode('utf-8'))

    def decrypt(self, token):
        return base64.b64decode(token).decode('utf-8')

    def generateToken(self, ipaddr):
        return self._encrypt(ipaddr)

    def isTokenValid(self, token):
        if not token:
            return False
        dToken = self.decrypt(token)
        ipaddr, timestamp = dToken.split("_")
        currentTime = int(time.mktime(datetime.datetime.now().timetuple()))
        return currentTime < int(timestamp)


if __name__ == "__main__":
    t = TokenGenerator()
    tok = t.generateToken("abc")
    print(t.isTokenValid(tok))
