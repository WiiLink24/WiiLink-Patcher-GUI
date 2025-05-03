import libWiiPy, os, tempfile, shutil, bsdiff4
from .enums import *
from .download import download_patch, download_file, download_agc, download_osc_app, download_title_contents, \
    download_channel

patcher_url = "https://patcher.wiilink24.com"
temp_dir = os.path.join(tempfile.gettempdir(), "WiiLinkPatcher")
wad_directory = os.path.join("WiiLink", "WAD")

title_directory = os.path.join(temp_dir, "Unpack")


def apply_bsdiff_patches(channel_name: str, patch_files: dict[str, int], title: libWiiPy.title.Title):
    """Download and apply bsdiff patches to the app files specified"""
    patch_directory = os.path.join(temp_dir, "Patches")

    # Apply patches
    for patch, index in patch_files.items():
        print(f" - Patching content {index + 1}...")

        print("   - Downloading patch...")
        patch_binary = download_patch(channel_name.lower(), patch)
        print("      - Done!")
        stock_content = title.get_content_by_index(index)
        print("   - Applying patch...")
        patched_content = bsdiff4.patch(stock_content, patch_binary)
        title.set_content(patched_content, index)
        print("      - Done!")

    # Delete temporary directory, ready for next channel to be patched
    shutil.rmtree(temp_dir)

    return title


def patch_channel(channel_name: str, channel_title: str, title_id: str,
                  patch_files: dict[str, int], channel_type: ChannelTypes, version: int = None, region: Regions = None,
                  language: Languages = None, additional_files: dict[str, str] = None, wfc_network: WFCNetworks = None):
    print(f"Patching {channel_title}:")
    file_url = f"{patcher_url}/{channel_name.lower()}/{title_id}"

    os.makedirs(wad_directory, exist_ok=True)
    os.makedirs(title_directory, exist_ok=True)

    match channel_type:
        case ChannelTypes.WiiConnect24:
            if region is not None:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} [{region.name}] (WiiLink).wad")
            else:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} (WiiLink).wad")
        case ChannelTypes.Regional:
            if language is not None:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} [{language.name}] (WiiLink).wad")
            else:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} (WiiLink).wad")
        case ChannelTypes.WFC:
            if region is not None:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} [{region.name}] ({wfc_network}).wad")
            else:
                output_wad = os.path.join("WiiLink", "WAD", f"{channel_title} ({wfc_network}).wad")
        case _:
            output_wad = os.path.join("WiiLink", "WAD", f"{channel_title}.wad")

    if channel_type != ChannelTypes.Regional:
        additional_files.update({
            ".cert": os.path.join(title_directory, f"{title_id}.cert")
        })

    for file, destination in additional_files.items():
        url = f"{file_url}{file}"
        download_file(url, destination)

    title = libWiiPy.title.Title()

    if not os.path.exists(os.path.join(title_directory, f"tmd.{version}")):
        tmd = libWiiPy.title.download_tmd(title_id, version)
    else:
        tmd = open(os.path.join(title_directory, f"tmd.{version}"), "rb").read()

    title.load_tmd(tmd)

    if not os.path.exists(os.path.join(title_directory, "tik")):
        ticket = libWiiPy.title.download_ticket(title_id)
    else:
        ticket = open(os.path.join(title_directory, "tik"), "rb").read()

    title.load_ticket(ticket)

    if not os.path.exists(os.path.join(title_directory, f"{title_id}.cert")):
        cert = libWiiPy.title.download_cert_chain()
    else:
        cert = open(os.path.join(title_directory, f"{title_id}.cert"), "rb").read()

    title.load_cert_chain(cert)

    title = download_title_contents(title, title_id)

    title = apply_bsdiff_patches(channel_name, patch_files, title)

    print(" - Packing WAD...")

    open(output_wad, "wb").write(title.dump_wad())

    print("   - Done!")


def nc_patch(region: Regions):
    """Patch the Nintendo Channel for the specified region"""
    region_data = {
        Regions.USA: ["0001000148415445", "Nintendo Channel"],
        Regions.PAL: ["0001000148415450", "Nintendo Channel"],
        Regions.Japan: ["000100014841544a", "Minna no Nintendo Channel"]
    }

    channel_id = region_data[region][0]
    channel_title = region_data[region][1]

    patches = {
        f"NC_1_{region.name}.bsdiff": 1
    }

    additional_files = {
        ".tik": os.path.join(title_directory, "tik")
    }

    patch_channel("nc", channel_title, channel_id, patches, ChannelTypes.WiiConnect24, 1792, region, None, additional_files)


def forecast_patch(region: Regions, platform: Platforms):
    """Patch the Forecast Channel for the specified region"""
    title_ids = {
        Regions.USA: "0001000248414645",
        Regions.PAL: "0001000248414650",
        Regions.Japan: "000100024841464a"
    }

    channel_id = title_ids[region]

    patches = {
        "Forecast_1.bsdiff": 1,
        "Forecast_5.bsdiff": 5,
    }

    # Download AnyGlobe Changer to allow setting custom regions
    download_agc(platform)

    patch_channel("forecast", "Forecast Channel", channel_id, patches, ChannelTypes.WiiConnect24, 7, region)


def news_patch(region: Regions):
    """Patch the News Channel for the specified region"""
    title_ids = {
        Regions.USA: "0001000248414745",
        Regions.PAL: "0001000248414750",
        Regions.Japan: "000100024841474a"
    }

    channel_id = title_ids[region]

    patches = {
        "News_1.bsdiff": 1
    }

    patch_channel("news", "News Channel", channel_id, patches, ChannelTypes.WiiConnect24, 7, region)


def evc_patch(region: Regions):
    """Patch the Everybody Votes Channel for the specified region"""
    title_ids = {
        Regions.USA: "0001000148414a45",
        Regions.PAL: "0001000148414a50",
        Regions.Japan: "0001000148414a4a",
    }

    channel_id = title_ids[region]

    patches = {
        f"EVC_1_{region.name}.bsdiff": 1
    }

    additional_files = {
        ".tik": os.path.join(title_directory, "tik")
    }

    patch_channel("evc", "Everybody Votes Channel", channel_id, patches, ChannelTypes.WiiConnect24, 512, region, None, additional_files)

    regsel_patch(region)


def regsel_patch(region: Regions):
    """Patch Region Select for the specified region"""
    title_ids = {
        Regions.USA: "0001000848414c45",
        Regions.PAL: "0001000848414c50",
        Regions.Japan: "0001000848414c4a"
    }

    channel_id = title_ids[region]

    patches = {
        "RegSel_1.bsdiff": 1
    }

    patch_channel("regsel", "Region Select", channel_id, patches, ChannelTypes.WiiConnect24, 2, region)


def cmoc_patch(region: Regions):
    """Patch the Check Mii Out Channel for the specified region"""
    region_data = {
        Regions.USA: ["0001000148415045", "Check Mii Out Channel"],
        Regions.PAL: ["0001000148415050", "Mii Contest Channel"],
        Regions.Japan: ["000100014841504a", "Mii Contest Channel"]
    }

    channel_id = region_data[region][0]
    channel_title = region_data[region][1]

    patches = {
        f"CMOC_1_{region.name}.bsdiff": 1
    }

    additional_files = {
        ".tik": os.path.join(title_directory, "tik")
    }

    patch_channel("cmoc", channel_title, channel_id, patches, ChannelTypes.WiiConnect24, 512, region, additional_files=additional_files)


def wiiroom_patch(language: Languages):
    """Patch Wii Room for the specified language"""
    patches = {
        f"WiinoMa_2_{language.name}.bsdiff": 2
    }

    if language == Languages.Russian:
        patches.update({
            "WiinoMa_1_Russian.bsdiff": 1,
            "WiinoMa_3_Russian.bsdiff": 3,
            "WiinoMa_4_Russian.bsdiff": 4,
            "WiinoMa_9_Russian.bsdiff": 9,
            "WiinoMa_C_Russian.bsdiff": 12,
            "WiinoMa_D_Russian.bsdiff": 13,
            "WiinoMa_E_Russian.bsdiff": 14
        })
    elif language == Languages.Portuguese:
        patches.update({
            "WiinoMa_1_Portuguese.bsdiff": 1,
            "WiinoMa_3_Portuguese.bsdiff": 3,
            "WiinoMa_4_Portuguese.bsdiff": 4,
            "WiinoMa_D_Portuguese.bsdiff": 13
        })
    else:
        patches.update({
            "WiinoMa_1_Universal.bsdiff": 1
        })

    if language == Languages.Japan:
        channel_title = "Wii no Ma"
    else:
        channel_title = "Wii Room"
        patches.update({
            "WiinoMa_0_Universal.bsdiff": 0
        })

    patch_channel("WiinoMa", channel_title, "000100014843494a", patches, ChannelTypes.Regional, language=language)


def digicam_patch(translated: bool):
    """Patch the Digicam Prints Channel for English or Japanese"""
    if translated:
        language = Languages.English
        channel_title = "Photo Prints Channel"
        patches = {
            "Digicam_0_English.bsdiff": 0,
            "Digicam_1_English.bsdiff": 1,
            "Digicam_2_English.bsdiff": 2
        }
    else:
        language = Languages.Japan
        channel_title = "Digicam Print Channel"
        patches = {
            "Digicam_1_Japan.bsdiff": 1
        }

    patch_channel("Digicam", channel_title, "000100014843444a", patches, ChannelTypes.Regional, language=language)


def demae_patch(translated: bool, demae_version: DemaeConfigs, region: Regions):
    """Patch the Demae Channel for Fake Ordering or Domino's, in English or Japanese"""
    patches = {}
    channel_name = ""

    match demae_version:
        case DemaeConfigs.Standard:
            if translated:
                patches = {
                    "Demae_0_English.bsdiff": 0,
                    "Demae_1_English.bsdiff": 1,
                    "Demae_2_English.bsdiff": 2
                }
            else:
                patches = {
                    "Demae_1_Japan.bsdiff": 1
                }

            channel_name = "Demae"

        case DemaeConfigs.Dominos:
            patches = {
                "Dominos_0.bsdiff": 0,
                "Dominos_1.bsdiff": 1,
                "Dominos_2.bsdiff": 2
            }

            ic_ids = {
                Regions.USA: "0001000148414445",
                Regions.PAL: "0001000148414450",
                Regions.Japan: "000100014841444a"
            }

            ic_id = ic_ids[region]

            channel_name = "Dominos"

            # Download WiiLink Account Linker, as this is needed for Demae Dominos
            download_osc_app("wiilink-account-linker")

            # Download Internet Channel to allow on-console order tracking
            download_channel("Internet Channel", ic_id, 1024, region)

    if translated:
        channel_title = "Food Channel"
        language = Languages.English
    else:
        channel_title = "Demae Channel"
        language = Languages.Japan

    patch_channel(channel_name, f"{channel_title} ({demae_version.name})", "000100014843484a", patches, ChannelTypes.Regional, language=language)



def kirbytv_patch():
    """Patch the Kirby TV Channel"""
    patches = {
        "ktv_2.bsdiff": 2
    }

    additional_files = {
        ".tmd": os.path.join(title_directory, f"tmd.257"),
        ".tik": os.path.join(title_directory, "tik")
    }

    patch_channel("ktv", "Kirby TV Channel", "0001000148434d50", patches, ChannelTypes.Regional, additional_files=additional_files)

def wiispeak_patch(region: Regions, network: WFCNetworks):
    """Patch the Wii Speak Channel for the specified region and WFC network"""
    patches = {
        f"WiiSpeak_1_{region.name}.bsdiff": 1
    }

    title_ids = {
        Regions.USA: "0001000148434645",
        Regions.PAL: "0001000148434650",
        Regions.Japan: "000100014843464a",
    }

    channel_id = title_ids[region]

    patch_channel("ws", "Wii Speak Channel", channel_id, patches, ChannelTypes.WFC, wfc_network=network)