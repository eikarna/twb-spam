import requests
import json
import uuid
import threading
import time
import sys
from colorama import init, Fore, Style

init(autoreset=True)

SUCCESS_COLOR = Style.BRIGHT + Fore.GREEN
ERROR_COLOR = Style.BRIGHT + Fore.RED
WARN_COLOR = Style.BRIGHT + Fore.YELLOW

def format_number(number):
    formatted_str = "{0:,}".format(number).replace(",", ".")
    return formatted_str

def fetch_campaign_data(url):
    try:
        campaign_url = f"https://api.twibbonize.com/v1/campaign/{url}"
        response = requests.get(campaign_url)
        campaign_data = response.json()
        return campaign_data
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"{ERROR_COLOR}An error occurred while fetching campaign data:", str(e))
        return None

def process_campaign_data(campaign_data):
    if campaign_data is None:
        return None

    try:
        campaign_uuid = campaign_data["data"]["campaign"]["uuid"]
        module_uuid = campaign_data["data"]["modules"][0]["uuid"]
        module_code = campaign_data["data"]["modules"][0]["moduleCode"]
        sub_module_uuid = campaign_data["data"]["modules"][0]["data"]["frames"][0].split(".")[0]
        campaign_creator_uuid = campaign_data["data"]["campaign"]["campaignCreator"]["uuid"]

        print("")
        print(f"{SUCCESS_COLOR}Extracted Keys:")
        print(f"{WARN_COLOR}Module UUID:", module_uuid)
        print(f"{WARN_COLOR}Module Code:", module_code)
        print(f"{WARN_COLOR}URL:", campaign_data['data']['campaign']['url'])
        print(f"{WARN_COLOR}Submodule UUID:", sub_module_uuid)
        print(f"{WARN_COLOR}Campaign UUID:", campaign_uuid)
        print(f"{WARN_COLOR}Campaign Creator UUID:", campaign_creator_uuid)
        print("")

        return campaign_data
    except KeyError as e:
        print(f"{ERROR_COLOR}Failed to extract keys from campaign data:", str(e))
        return None

def spam(campaign_data):
    retry_limit = 5
    retry_count = 0

    while True and retry_count < retry_limit:
        try:
            payload = {
                "deviceId": str(uuid.uuid4())
            }

            response = requests.post("https://analytics-producer.twibbonize.com/analytics/hash", json=payload)
            cookie = response.cookies.get_dict()
            body = response.json()

            payload = {
                "fingerprint": body["data"]["fingerprint"],
                "url": campaign_data["data"]["campaign"]["url"],
                "moduleUuid": campaign_data["data"]["modules"][0]["uuid"],
                "moduleCode": campaign_data["data"]["modules"][0]["moduleCode"],
                "subModuleUuid": campaign_data["data"]["modules"][0]["data"]["frames"][0].split(".")[0],
                "campaignUuid": campaign_data["data"]["campaign"]["uuid"],
                "campaignCreatorUuid": campaign_data["data"]["campaign"]["campaignCreator"]["uuid"],
            }

            response = requests.post("https://analytics-producer.twibbonize.com/analytics/hit", cookies=cookie, json=payload)

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"{ERROR_COLOR}An error occurred:", str(e))
            retry_count += 1
            print(f"{WARN_COLOR}Retrying... Attempt {retry_count}/{retry_limit}")
            time.sleep(1)

    if not success:
        print(f"{ERROR_COLOR}Function failed after {retry_limit} attempts.")

def main():
    urlt = str(sys.argv[1])
    campaign_data = fetch_campaign_data(urlt)
    campaign_data = process_campaign_data(campaign_data)

    if campaign_data is None:
        return

    thr = int(sys.argv[2])
    for i in range(thr):
        thread = threading.Thread(target=spam, args=(campaign_data,))
        thread.start()
        time.sleep(0.8)

if __name__ == "__main__":
    main()
