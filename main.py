import requests
import json
import os
import time

file1 = open('uuid.txt', 'r')
count = 0
url = "https://api.tpilums.org.pk/core/api/image/get_links/"
while True:

    line = file1.readline()
    if not line:
        print(f"Total Events Saved {count}")
        break
    id = line.strip()
    payload = f"[\"{id}\"]"
    headers = {
        'Authorization': 'Token dde9d96b97d56db1a0f6c66e2b90ec8932a50ed2'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    image_links = json.loads(response.text)
    image_url = "https://api.tpilums.org.pk/media/"

    for event in image_links['image_links']:
        dir_path = f"/home/zainulhassan540/Forest-Fire-Detection{event}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            print(f"Directory '{dir_path}' already exists.")

        for image_link in image_links['image_links'][event]:
            image_url = f"https://api.tpilums.org.pk/media/{image_link}"
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = response.content
                file_path = f"{dir_path}/{image_link.split('/')[-1]}"

                with open(file_path, "wb") as file:
                    file.write(image_data)

                print(f"Image downloaded and saved as {file_path}")
            else:
                print(f"Failed to download the image. Status code: {response.status_code}")
        time.sleep(.5)
    count += 1
    print(count)

file1.close()

