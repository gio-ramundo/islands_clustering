import requests
import os
import sys
from bs4 import BeautifulSoup
import pickle
import ee

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
# Dictionary with files ID and names
files = config.FILES

# Google Earth API authenticaiton
# Need to create a project through link https://console.cloud.google.com/earth-engine/welcome?hl=it
# Inset project name in config files in the variable project
project = config.proj
ee.Authenticate()
ee.Initialize(project = project)

# Already downloaded files
file_pkl = os.path.join(project_folder, "files", "downloaded_files.pkl")
if os.path.exists(file_pkl):
    try:
        with open(file_pkl, 'rb') as file:
            downloaded_files = pickle.load(file)
        print("downloaded_files.pkl loaded succesfully.")
    except Exception as e:
        print(f"Error during downloaded_files.pkl loading: {e}")
        downloaded_files = []
else:
    downloaded_files = []

# Destination folders
folder_out = os.path.join(project_folder, "files")
os.makedirs(folder_out, exist_ok = True)
folder_out1 = os.path.join(folder_out, "PVOUT_month")
os.makedirs(folder_out1, exist_ok = True)
folder_out2 = os.path.join(folder_out, "offshore")
os.makedirs(folder_out2, exist_ok = True)

def download_file(file_id, file_name):
    url = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    # Output folder (different for different files)
    if type(file_name) == type([]): # offshore .shp files
        folder_new = os.path.join(folder_out2, file_name[0])
        os.makedirs(folder_new, exist_ok = True)
        file_path = os.path.join(folder_new, file_name[1])
    elif file_name.startswith("PVOUT_"): # moonthly PVOUT files
        file_path = os.path.join(folder_out1, file_name)
    else: # other files
        file_path = os.path.join(folder_out, file_name)
    try:
        print(f'Start {file_name} download')
        response = session.get(url, params = {"id": file_id}, stream = True, allow_redirects = True)
        response.raise_for_status()
        # Huge file warning
        if "Virus scan warning" in response.text:
            # Web scraping
            soup = BeautifulSoup(response.text, 'html.parser')
            download_form = soup.find('form', {'id': 'download-form'})
            if download_form:
                download_url = download_form.get('action')
                form_data = {}
                for input_tag in download_form.find_all('input'):
                    name = input_tag.get('name')
                    value = input_tag.get('value')
                    if name:
                        form_data[name] = value
            download_response = requests.get(download_url, params = form_data, stream = True)
            download_response.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in download_response.iter_content(chunk_size = 8192):
                    f.write(chunk)
            print(f"File downloaded correctly")
        else:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size = 8192):
                    f.write(chunk)
            print(f"File downloaded correctly")
        # Dictionary and pkl update
        downloaded_files.append(file_id)
        with open(file_pkl, "wb") as f:
            pickle.dump(downloaded_files, f)
    except requests.exceptions.RequestException as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Function application
for file_id, file_name in files.items():
    if file_id not in downloaded_files:
        download_file(file_id, file_name)

# Final check
if len(files) == len(downloaded_files):
    print('All files downloaded correctly.')
else:
    print('Not all files downloaded correctly. Run again the script.')