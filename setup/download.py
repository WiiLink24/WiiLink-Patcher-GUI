import os, urllib.request, tempfile, zipfile, libWiiPy, shutil, json, certifi, ssl
from .enums import *

context = ssl.create_default_context(cafile=certifi.where())

patcher_url = "https://patcher.wiilink24.com"
temp_dir = os.path.join(tempfile.gettempdir(), "WiiLinkPatcher")
wad_directory = os.path.join("WiiLink", "WAD")

title_directory = os.path.join(temp_dir, "Unpack")

"""
Using code from "commands/title/nus.py" from WiiPy by NinjaCheetah
https://github.com/NinjaCheetah/WiiPy
"""


def connection_test():
    """Function to ensure the patcher is able to connect to the patcher server and NUS"""
    patcher_test = f"{patcher_url}/connectiontest.txt"
    patcher_expected = b"If the patcher can read this, the connection test succeeds.\n"

    patcher_request = urllib.request.Request(patcher_test)
    patcher_request.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36")

    try:
        patcher_response = urllib.request.urlopen(patcher_request, context=context).read()
    except Exception as e:
        print(f"Connection test failed! {e}")
        return False

    if patcher_response != patcher_expected:
        print(f"""Unexpected response!
Expected: {patcher_expected}
Received: {patcher_response}""")
        return False

    nus_test = ("http://nus.cdn.shop.wii.com/ccs/download/000100014841564a/tmd")

    nus_request = urllib.request.Request(nus_test)
    nus_request.add_header("User-Agent", "wii libnup/1.0")

    try:
        nus_response = urllib.request.urlopen(nus_request, context=context).read()
    except Exception as e:
        print(f"Connection test failed! {e}")
        return False

    return True


def download_translation(language: str):
    """Downloads a specified translation file from the server, ready to be loaded into the app."""
    translation_url = f"{patcher_url}/qt-lang/translation_{language}.qm"

    translation_dir = os.path.join(os.path.dirname(__file__), "translations")
    os.makedirs(translation_dir, exist_ok=True)

    try:
        download_file(translation_url, translation_dir)
    except Exception as e:
        print(e)
        return False
    
    return True


def download_translation_dict():
    """Downloads and returns a dictionary of available languages from the server."""
    url = f"{patcher_url}/qt-lang/languages.json"

    try:
        raw_json = download_file(url)
    except Exception as e:
        print(e)
        return False

    translation_dict = json.loads(raw_json)

    return translation_dict


def download_file(url: str, destination: str = None):
    """Simple function to download files from a specified URL to a specified location, or to return the contents of the URL if a location is not specified."""
    request = urllib.request.Request(url)
    request.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36")
    try:
        file = urllib.request.urlopen(request, context=context).read()
        if destination is not None:
            open(destination, "wb").write(file)
        else:
            return file
    except Exception as e:
        raise ValueError(f"""An exception occurred! {e}
File URL: {url}""")


def download_osc_app(app_name: str):
    """Downloads an app from the OSC to "WiiLink/apps"."""
    app_path = os.path.join("WiiLink", "apps", app_name)

    os.makedirs(app_path, exist_ok=True)

    print(f"Downloading {app_name} from OSC:")

    print(" - Downloading boot.dol...")
    download_file(f"https://hbb1.oscwii.org/unzipped_apps/{app_name}/apps/{app_name}/boot.dol",
                  os.path.join(app_path, "boot.dol"))
    print("   - Done!")
    print(" - Downloading meta.xml...")
    download_file(f"https://hbb1.oscwii.org/unzipped_apps/{app_name}/apps/{app_name}/meta.xml",
                  os.path.join(app_path, "meta.xml"))
    print("   - Done!")
    print(" - Downloading icon.png...")
    download_file(f"https://hbb1.oscwii.org/api/v3/contents/{app_name}/icon.png",
                  os.path.join(app_path, "icon.png"))
    print("   - Done!")


def download_agc(platform: Platforms):
    """Downloads AnyGlobe Changer, either from OSC or GitHub, depending on the user's platform"""
    if platform != Platforms.Dolphin:
        download_osc_app("AnyGlobe_Changer")
        return
    else:
        # Dolphin users need v1.0 of AnyGlobe Changer, as the latest OSC release doesn't work with Dolphin, for some reason.
        app_path = os.path.join(temp_dir, "AGC")
        agc_dest = os.path.join(app_path, "AGC.zip")

        os.makedirs(app_path)

        print("Downloading AnyGlobe Changer from GitHub:")
        print(" - Downloading release...")
        download_file("https://github.com/fishguy6564/AnyGlobe-Changer/releases/download/1.0/AnyGlobe.Changer.zip",
                      agc_dest)
        print("   - Done!")
        print(" - Extracting release...")
        with zipfile.ZipFile(agc_dest, "r") as agc_zip:
            agc_zip.extractall(os.path.join("WiiLink"))
        print("   - Done!")
        os.remove(agc_dest)
        os.rmdir(app_path)
        return


def download_spd():
    """Downloads the SPD WAD from the WiiLink Patcher server."""
    spd_url = f"{patcher_url}/spd/WiiLink_SPD.wad"

    os.makedirs(wad_directory, exist_ok=True)

    print("Downloading WiiLink Address Settings:")
    download_file(spd_url, os.path.join(wad_directory, "WiiLink Address Settings.wad"))
    print(" - Done!")


def download_patch(folder: str, patch_name: str):
    """Downloads a patch from the WiiLink Patcher server."""
    patch_url = f"{patcher_url}/bsdiff/{folder}/{patch_name}"

    return download_file(patch_url)


def download_channel(channel_title: str, title_id: str, version: int = None, region: Regions = None,
                     channel_name: str = None,
                     additional_files: dict[str, str] = None):
    os.makedirs(wad_directory, exist_ok=True)
    os.makedirs(title_directory, exist_ok=True)

    if region is not None:
        wad_file = os.path.join(wad_directory, f"{channel_title} [{region.name}].wad")
    else:
        wad_file = os.path.join(wad_directory, f"{channel_title}.wad")

    # Download the title from the NUS. This is done "manually" (as opposed to using download_title()) so that we can
    # provide verbose output.
    title = libWiiPy.title.Title()

    if additional_files is not None:
        for file, destination in additional_files.items():
            file_url = f"{patcher_url}/{channel_name.lower()}/{title_id}{file}"
            download_file(file_url, destination)

    # Announce the title being downloaded, and the version if applicable.
    if version is not None:
        print(f"Downloading {channel_title} v{version}, please wait...")
    else:
        print(f"Downloading the latest version of {channel_title}, please wait...")

    if not os.path.exists(os.path.join(title_directory, f"tmd.{version}")):
        print(" - Downloading and parsing TMD...")
        tmd = libWiiPy.title.download_tmd(title_id, version)
    else:
        tmd = open(os.path.join(title_directory, f"tmd.{version}"), "rb").read()

    title.load_tmd(tmd)

    if not os.path.exists(os.path.join(title_directory, "tik")):
        # Download the ticket, if we can.
        print(" - Downloading and parsing Ticket...")
        try:
            ticket = libWiiPy.title.download_ticket(title_id)
        except ValueError:
            # If libWiiPy returns an error, then no ticket is available.
            raise ValueError("No Ticket is available!")
    else:
        ticket = open(os.path.join(title_directory, "tik"), "rb").read()

    title.load_ticket(ticket)

    if not os.path.exists(os.path.join(title_directory, f"{title_id}.cert")):
        cert = libWiiPy.title.download_cert_chain()
    else:
        cert = open(os.path.join(title_directory, f"{title_id}.cert"), "rb").read()

    title.load_cert_chain(cert)

    # Download the channel's contents
    title = download_title_contents(title, title_id)

    # Pack a WAD and output that.
    if wad_file is not None:
        print(" - Packing WAD...")
        # Have libWiiPy dump the WAD, and write that data out.
        open(wad_file, "wb").write(title.dump_wad())

    shutil.rmtree(temp_dir)

    print("   - Done!")


def download_title_contents(title: libWiiPy.title.Title, title_id: str):
    """Download the contents for a title from NUS"""

    # Load the content records from the TMD, and begin iterating over the records.
    title.load_content_records()
    content_list = []
    for content in range(len(title.tmd.content_records)):
        # Generate the content file name by converting the Content ID to hex and then removing the 0x.
        content_file_name = hex(title.tmd.content_records[content].content_id)[2:]
        while len(content_file_name) < 8:
            content_file_name = "0" + content_file_name
        print(f" - Downloading content {content + 1} of {len(title.tmd.content_records)} "
              f"(Content ID: {title.tmd.content_records[content].content_id}, "
              f"Size: {title.tmd.content_records[content].content_size} bytes)...")
        content_list.append(libWiiPy.title.download_content(title_id, title.tmd.content_records[content].content_id))
        print("   - Done!")

    title.content.content_list = content_list

    return title


def download_todaytomorrow(region: Regions):
    match region:
        case Regions.PAL:
            additional_files = {
                ".tik": os.path.join(title_directory, "tik")
            }
            download_channel("Today and Tomorrow Channel", "0001000148415650", 512, Regions.PAL, "tatc",
                             additional_files)
        case Regions.Japan:
            download_channel("Today and Tomorrow Channel", "000100014841564a", 512, Regions.Japan)
