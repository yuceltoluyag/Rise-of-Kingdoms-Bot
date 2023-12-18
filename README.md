![issues](https://img.shields.io/github/issues/yuceltoluyag/Rise-of-Kingdoms-Bot)
![forks](https://img.shields.io/github/forks/yuceltoluyag/Rise-of-Kingdoms-Bot)
![stars](https://img.shields.io/github/stars/yuceltoluyag/Rise-of-Kingdoms-Bot)
![lincense](https://img.shields.io/github/license/yuceltoluyag/Rise-of-Kingdoms-Bot)

- [Rise of Kingdom Bot](#rise-of-kingdom-bot)
    + [**Introduction**](#--introduction--)
    + [Requirements](#requirements)
    + [Functions](#functions)
- [Can it do captcha?](#can-it-do-captcha-)
    + [Set Up](#set-up)
    + [Configurations](#configurations)
    + [Show case](#show-case)
  * [WARNING](#warning)
- [Disclaimer](#disclaimer)

# Rise of Kingdom Bot

### **Introduction**

Rise of Kingdom Bot can do following job: claim quests/vip/gifts, collecting resource, gathering resource, donate techology, train troops and pass verification.

If you have any problem, suggestions or new features, please feel free to submit issues directly on GitHub

- Link: https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot/issues

If you don't know where to download the files, you can check this file.

- Link: [links.txt](https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot/blob/main/links.txt)

If you like this project, give me a star or feedback , that is great help for me. **:smile:**

---

**Update:**

- Enable Sunset Canyon.
- Enable LOST Canyon.
- Use Items(Some Features)

Note: Don't forget to move your **'save'**, **'config.json'** and **'devices_config.json'** to new version folder

---

### Requirements

- python

  version >= 3.7

- software

  - ADB version 29.0.5-5949299 (1.0.41)
  - tesseract

- libraries

  - opencv-python

  - pytesseract

  - numpy

  - pillow

  - pure-python-adb

  - requests

  - requests-toolbelt

### Functions

| Name                                                   | Status                                                                                                          |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Automatically start the game when game is not running  | **<u>Done</u>**                                                                                                 |
| Automatically locating building                        | **<u>Done</u>**                                                                                                 |
| Collecting resource, troops, and help alliance         | **<u>Done</u>**                                                                                                 |
| Produce material                                       | **<u>Done</u>**                                                                                                 |
| Open free chest in tavern                              | **<u>Done</u>**                                                                                                 |
| Claim quest and daily objectives                       | **<u>Done</u>**                                                                                                 |
| Claim VIP chest                                        | **<u>Done</u>**                                                                                                 |
| Claim Event                                            | not yet                                                                                                         |
| Collecting allied resource, gifs and donate technology | **<u>Done</u>**                                                                                                 |
| Upgrade and train troops                               | <u>**Done**</u>                                                                                                 |
| Attack barbarians                                      | <u>**Done**</u>                                                                                                 |
| Heal troops                                            | <u>**Done**</u>                                                                                                 |
| Gather resource                                        | **<u>Done</u>**                                                                                                 |
| Mystery Merchant                                       | <u>**Done**</u>                                                                                                 |
| A simple GUI                                           | **<u>Done</u>**                                                                                                 |
| Allow bot control multi-devices/emulator               | **<u>Done</u>**                                                                                                 |
| Pass verification with haoi API                        | **<u>not yet</u>**                                                                                              |
| Pass verification with 2captcha API                    | **<u>[BETA](https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot/releases/tag/0.0.1-Beta)</u> Please Test : )** |

# Can it do captcha?

- Yes, it does, you need to get a paid membership from one of the 9:29 [Videotime](https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot#show-case) hapi or 2captcha Sites, you will paste the key you bought from there in the settings section. 9:29 [Videotime](https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot#show-case) If you want to support [2captcha.com](https://2captcha.com?from=11847506)

### Set Up

- Use following commands to install package into you **python** / **python virtual environment** (version 3.7)

  ```
  pip install -r requirements.txt

  ```

- Download **ADB** version 29.0.5-5949299 (1.0.41) (require for same version or you can change version in adb.py)

  - move all **adb** files under: **project folder/adb/**

- Download **tesseract** version v5.0.0-alpha.20201127 (no require for same version)

  - move all **tesseract** files under: **project folder/tesseract/**

- Use following command to run project

  ```
  python main.py
  ```

- Directory Structure Image:

  ![](https://github.com/yuceltoluyag/Rise-of-Kingdoms-Bot/blob/main/docs/structure.png?raw=true)

### Configurations

- Emulator resolution must be <u>**720x1280**</u> or <u>**1280x720**</u>
- Emulator must **Enable** Android Debug Bridge (ADB)
- Game language must be <u>**English**</u>

### Show case

[![](https://markdown-videos.deta.dev/youtube/6IObh_HJvrk)](https://youtu.be/6IObh_HJvrk)

- [Youtube Shorts](https://www.youtube.com/@yuceltoluyag/shorts)

## WARNING

- **Use it at your own risk!**
- **I don't know will your account be banned by using it!**

# Disclaimer

```python
#import disclaimer
/*
 *
 * We are not responsible for banned account or any other punishment by this game's GM. 
 * Please do some research if you have any concerns about features included in this repo
 * before using it! YOU are choosing to use these scripts, and if
 * you point the finger at us for messing up your account, we will laugh at you.
 *
 */
```

