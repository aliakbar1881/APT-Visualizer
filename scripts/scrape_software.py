import requests
from bs4 import BeautifulSoup
import csv
import time
from loguru import logger
import json
import re
import random


class RequestError(BaseException):
    pass

class Software:
    def __init__(self, base_url, software_url):
        self.base_url = base_url
        self.software_url = software_url

    def __call__(self):
        self.fetch_softwares()
        self.fetch_software_tech()
    
    def fetch_softwares(self): 
        resp = requests.get(self.software_url)
        if not resp.ok:
            raise RequestError(f"[x]RequestError:‌ {resp.status_code}")
        soup = BeautifulSoup(resp.content, "html.parser")
        with open("data/software/softwares.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            for group in soup.tbody.find_all("tr"):
                gid = group.find_all('td')[0].a.string
                name = group.find_all('td')[1].a.string
                writer.writerow([gid, name])
                
    def fetch_software_tech(self):
        group_regex = re.compile(r'<a\shref=\"/\w+/\w+\">\w+</a>')
        result = []
        headers = {
              'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }
        with open('data/software/softwares.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                url = f"https://attack.mitre.org/software/{row[0].strip()}/"
                resp = requests.get(url)
                soup = BeautifulSoup(group_regex.findall(resp.text)[0], "html.parser")
                group = soup.a.string
                url_json = f"https://attack.mitre.org/software/{row[0].strip()}/{row[0].strip()}-enterprise-layer.json"
                jitter = random.random() * random.randint(3, 6)
                time.sleep(jitter)
                try:
                    resp = requests.get(url_json, headers=headers)
                except:
                    logger.error(f"{url} not respond")
                    continue
                if resp.status_code > 400 :
                    logger.error(f"{group} : (status code :‌ {resp.status_code}) - {url_json}  ")
                    continue
                logger.info(row[0], row[1], resp)
                techniques = json.loads(resp.content)["techniques"]
                for technique in techniques:
                    technique_id = technique.get("techniqueID", None)
                    comment = technique.get("comment", None)
                    result.append([row[0], row[1], technique_id, comment, group])
        with open("data/software-techniques.csv", "w", newline='') as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)


if __name__ == "__main__":
    software = Software("https://attack.mitre.org/", "https://attack.mitre.org/software/")
    software()
