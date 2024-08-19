import requests
from bs4 import BeautifulSoup
import csv
import time
from loguru import logger
import json
import random


class RequestError(BaseException):
    pass

class Groups:
    def __init__(self, base_url, group_url):
        self.base_url = base_url
        self.group_url = group_url

    def __call__(self):
        #self.fetch_groups()
        self.fetch_group_tech()
    
    def fetch_groups(self): 
        resp = requests.get(self.group_url)
        if not resp.ok:
            raise RequestError(f"[x]RequestError:‌ {resp.status_code}")
        soup = BeautifulSoup(resp.content, "html.parser")
        with open("data/groups/groups.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            for group in soup.tbody.find_all("tr"):
                gid = group.find_all('td')[0].a.string
                name = group.find_all('td')[1].a.string
                writer.writerow([gid  , name])
                
    def fetch_group_tech(self):
        result = []
        with open('groups.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                url = f"https://attack.mitre.org/groups/{row[0].strip()}/{row[0].strip()}-enterprise-layer.json"
                jitter = random.random() * random.randint(1, 2)
                time.sleep(jitter)
                resp = requests.get(url)
                logger.info(row[0], row[1], resp)
                try:
                    techniques = json.loads(resp.content)["techniques"]
                except:
                    print(resp.content)
                for technique in techniques:
                    technique_id = technique.get("techniqueID", None)
                    comment = technique.get("comment", None)
                    result.append([row[0], row[1], technique_id, comment])
        with open("groups-techniques.csv", "w", newline='') as f:
            writer = csv.writer(f)
            for row in result:
                writer.writerow(row)


if __name__ == "__main__":
    groups = Groups("https://attack.mitre.org/", "https://attack.mitre.org/groups/")
    groups()
