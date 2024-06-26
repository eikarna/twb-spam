import requests
import json
import uuid
import threading
import time
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
        campaign_url = f"https://api.twibbonize.com/v2/campaign/{url}"
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
        campaign_uuid = campaign_data["data"]["modules"][0]["uuid"]
        module_uuid = campaign_data["data"]["modules"][0]["uuid"]
        module_code = campaign_data["data"]["modules"][0]["moduleCode"]
        sub_module_uuid = campaign_data["data"]["modules"][0]["data"]["frames"][0].split(".")[0]
        campaign_creator_uuid = campaign_data["data"]["campaign"]["campaignCreator"]["avatar"].split(".")[0]

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
    retry_limit = 10
    retry_count = 0
    success = True

    while success and retry_count <= retry_limit:
        try:
            payload = {
                "deviceId": str(uuid.uuid4())
            }

            response = requests.post("https://api.twibbonize.com/v2/analytics/hash", json=payload)
            cookie = response.cookies.get_dict()
            body = response.json()

            if not "message" in body:
                payload = {
                    "fingerprint": body["data"]["fingerprint"],
                    "url": campaign_data["data"]["campaign"]["url"],
                    "moduleUuid": campaign_data["data"]["modules"][0]["uuid"],
                    "moduleCode": campaign_data["data"]["modules"][0]["moduleCode"],
                    "subModuleUuid": campaign_data["data"]["modules"][0]["data"]["frames"][0].split(".")[0],
                }

                response = requests.post("https://api.twibbonize.com/v2/analytics/hit", cookies=cookie, json=payload)

                res1 = requests.get(f"https://api.twibbonize.com/v2/analytics/hit/campaign/{campaign_data['data']['modules'][0]['uuid']}")
                bod1 = res1.json()

                total_views = int(bod1['data']['hit'])
                formatted_views = format_number(total_views)
                print(f"[{threading.get_native_id()}] {SUCCESS_COLOR}Sukses! Total Views:", formatted_views)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"{ERROR_COLOR}An error occurred:", str(e))
            retry_count += 1
            if retry_count >= retry_limit:
                success = False
            print(f"{WARN_COLOR}Retrying... Attempt {retry_count}/{retry_limit}")
            time.sleep(1)

    if not success:
        print(f"{ERROR_COLOR}Function failed after {retry_limit} attempts.")

def main():
    urlt = input("Twibbon ID: ")
    campaign_data = fetch_campaign_data(urlt)
    campaign_data = process_campaign_data(campaign_data)

    if campaign_data is None:
        return

    thr = int(input("Threads: "))
    for i in range(thr):
        thread = threading.Thread(target=spam, args=(campaign_data,))
        thread.start()
        time.sleep(0.8)

if __name__ == "__main__":
    main()
