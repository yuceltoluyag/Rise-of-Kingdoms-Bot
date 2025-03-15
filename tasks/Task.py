from bot_related.device_gui_detector import GuiName, GuiDetector
from bot_related.bot_config import TrainingAndUpgradeLevel, BotConfig
from bot_related import haoi, twocaptcha
from bot_related import aircve as aircv
from config import HAO_I, TWO_CAPTCHA
from filepath.file_relative_paths import (
    GuiCheckImagePathAndProps,
    ImagePathAndProps,
    BuffsImageAndProps,
    ItemsImageAndProps,
)
from datetime import datetime, timedelta
from utils import aircv_rectangle_to_box, stop_thread, resource_path
from enum import Enum

import config
import traceback
import time
import os
import shutil
import cv2
import numpy as np
import random


from filepath.constants import (
    RESOURCES,
    SPEEDUPS,
    BOOSTS,
    EQUIPMENT,
    OTHER,
    MAP,
    HOME,
    WINDOW,
    GREEN_HOME,
)
from random import randrange, uniform


class Task:
    center = (640, 360)

    def __init__(self, bot):
        self.bot = bot
        self.device = bot.device
        self.gui = bot.gui
        self.debug_mode = False  # Debug modu varsayılan olarak kapalı

        # Debug ayarları
        self.debug_dir = "debug_images"
        self.debug_enabled = False  # Varsayılan olarak kapalı

        # Debug klasörünü oluştur ve temizle
        try:
            print("Debug: Bot baslatiliyor, debug klasoru temizleniyor...")

            # Her başlangıçta debug klasörünü tamamen temizle
            self.clean_debug_directory_completely()

            # Debug modunu bot yapılandırmasından al
            if hasattr(self.bot, "config") and hasattr(
                self.bot.config, "debug_mode"
            ):
                print(
                    f"Debug: Bot config debug_mode değeri: {self.bot.config.debug_mode}"
                )

                # Yapılandırma dosyasını kontrol et
                try:
                    import json
                    from utils import resource_path
                    from filepath.file_relative_paths import FilePaths

                    # Aktif cihazın yapılandırma dosyasını bul
                    if hasattr(self.bot.device, "save_file_prefix"):
                        config_file_path = resource_path(
                            FilePaths.SAVE_FOLDER_PATH.value
                            + "{}_config.json".format(
                                self.bot.device.save_file_prefix
                            )
                        )
                        print(
                            f"Debug: Yapılandırma dosyası: {config_file_path}"
                        )

                        if os.path.exists(config_file_path):
                            with open(config_file_path) as f:
                                config_dict = json.load(f)
                                print(
                                    f"Debug: Yapılandırma dosyasından debug_mode: {config_dict.get('debug_mode', False)}"
                                )
                                # Yapılandırma dosyasından debug_mode değerini doğrudan al
                                self.debug_mode = config_dict.get(
                                    "debug_mode", False
                                )
                        else:
                            print(
                                f"Debug: Yapılandırma dosyası bulunamadı: {config_file_path}"
                            )
                    else:
                        print(
                            "Debug: Cihazın save_file_prefix özelliği bulunamadı"
                        )
                except Exception as e:
                    print(
                        f"Debug: Yapılandırma dosyası kontrolünde hata: {str(e)}"
                    )
                    import traceback

                    traceback.print_exc()
                    # Hata durumunda bot yapılandırmasından al
                    self.debug_mode = self.bot.config.debug_mode

                print(
                    f"Debug: Task.debug_mode değeri ayarlandı: {self.debug_mode}"
                )

                if self.debug_mode:
                    print(
                        "Debug: Bot yapilandirmasindan debug modu etkinlestirildi"
                    )
                    # Debug modunu GUI'ye de bildir
                    if hasattr(self.gui, "debug"):
                        self.gui.debug = True
                        print("Debug: GUI debug modu etkinleştirildi")
            else:
                print("Debug: Bot yapılandırmasında debug_mode bulunamadı!")
        except Exception as e:
            print(f"Debug: Klasor olusturma/temizleme hatasi: {str(e)}")
            traceback.print_exc()
            # Hata durumunda debug modunu devre dışı bırak
            self.debug_mode = False

    def to_ascii(self, text):
        """
        Türkçe karakterleri ASCII karakterlere dönüştürür

        Args:
            text: Dönüştürülecek metin

        Returns:
            str: ASCII karakterlere dönüştürülmüş metin
        """
        tr_chars = {
            "ç": "c",
            "Ç": "C",
            "ğ": "g",
            "Ğ": "G",
            "ı": "i",
            "İ": "I",
            "ö": "o",
            "Ö": "O",
            "ş": "s",
            "Ş": "S",
            "ü": "u",
            "Ü": "U",
        }

        for tr_char, ascii_char in tr_chars.items():
            text = text.replace(tr_char, ascii_char)

        return text

    def call_idle_back(self):
        self.set_text(insert="call back idle commander")
        self.back_to_map_gui()
        while True:
            _, _, commander_pos = self.gui.check_any(
                ImagePathAndProps.HOLD_ICON_SMALL_IMAGE_PATH.value
            )
            if commander_pos is not None:
                x, y = commander_pos
                self.tap(x - 10, y - 10, 2)
                x, y = self.center
                self.tap(x, y)
                self.tap(x, y, 1)
            else:
                return
            _, _, return_btn_pos = self.gui.check_any(
                ImagePathAndProps.RETURN_BUTTON_IMAGE_PATH.value
            )
            if return_btn_pos is not None:
                x, y = return_btn_pos
                self.tap(x, y, 1)
            else:
                return

    def heal_troops(self):
        self.set_text(insert="Heal Troops")
        heal_button_pos = (960, 590)
        self.back_to_home_gui()
        self.home_gui_full_view()
        self.tap(
            self.bot.building_pos["hospital"][0],
            self.bot.building_pos["hospital"][1],
            2,
        )
        self.tap(285, 20, 0.5)
        _, _, heal_icon_pos = self.gui.check_any(
            ImagePathAndProps.HEAL_ICON_IMAGE_PATH.value
        )
        if heal_icon_pos is None:
            return
        self.tap(heal_icon_pos[0], heal_icon_pos[1], 2)
        self.tap(heal_button_pos[0], heal_button_pos[1], 2)
        self.tap(
            self.bot.building_pos["hospital"][0],
            self.bot.building_pos["hospital"][1],
            2,
        )
        self.tap(
            self.bot.building_pos["hospital"][0],
            self.bot.building_pos["hospital"][1],
            2,
        )

    # Home
    def back_to_home_gui(self):
        loop_count = 0
        gui_name = None
        while True:
            result = self.get_curr_gui_name()
            gui_name, info = ["UNKNOW", None] if result is None else result
            if gui_name == GuiName.HOME.name:
                break
            elif gui_name == GuiName.MAP.name:
                x_pos, y_pos = info
                self.tap(x_pos, y_pos)
            elif gui_name == GuiName.WINDOW.name:
                self.back(1)
            else:
                self.back(1)
            loop_count = loop_count + 1
            time.sleep(0.5)
        return loop_count

    def find_home(self):
        has_green_home, _, pos = self.gui.check_any(
            ImagePathAndProps.GREEN_HOME_BUTTON_IMG_PATH.value
        )
        if not has_green_home:
            return None
        x, y = pos
        self.tap(x, y, 2)

    def home_gui_full_view(self):
        self.tap(60, 540, 0.5)
        self.tap(1105, 200, 1)
        self.tap(1220, 35, 2)
        self.tap(43, 37, 3)
        self.tap(42, 38, 3)

    # Building Position
    def find_building_title(self):
        result = self.gui.has_image_props(
            ImagePathAndProps.BUILDING_TITLE_MARK_IMG_PATH.value
        )
        if result is None:
            return None
        x0, y0, x1, y1 = aircv_rectangle_to_box(result["rectangle"])
        return x0, y0, x1, y1

    # Menu
    def menu_should_open(self, should_open=False):
        # close menu if open
        (
            path,
            size,
            box,
            threshold,
            least_diff,
            gui,
        ) = ImagePathAndProps.MENU_BUTTON_IMAGE_PATH.value
        x0, y0, x1, y1 = box
        c_x, c_y = x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2
        is_open, _, _ = self.gui.check_any(
            ImagePathAndProps.MENU_OPENED_IMAGE_PATH.value
        )
        if should_open and not is_open:
            self.tap(c_x, c_y, 0.5)
        elif not should_open and is_open:
            self.tap(c_x, c_y, 0.5)

    # Map
    def back_to_map_gui(self):
        loop_count = 0
        gui_name = None
        while True:
            result = self.get_curr_gui_name()
            gui_name, pos = ["UNKNOW", None] if result is None else result
            if gui_name == GuiName.MAP.name:
                break
            elif gui_name == GuiName.HOME.name:
                x_pos, y_pos = pos
                self.tap(x_pos, y_pos)
            elif gui_name == GuiName.WINDOW.name:
                self.back(1)
            else:
                self.back(1)
            loop_count = loop_count + 1
            time.sleep(0.5)
        return loop_count

    def get_curr_gui_name(self):
        if not self.isRoKRunning():
            self.set_text(insert="game is not running, try to start game")
            self.runOfRoK()
            start = time.time()
            end = start
            while end - start <= 300 and self.isRoKRunning():
                result = self.gui.get_curr_gui_name()
                if result is None:
                    time.sleep(5)
                    end = time.time()
                else:
                    break

        pos_list = None
        for i in range(0, 1):
            result = self.gui.get_curr_gui_name()
            gui_name, pos = ["UNKNOW", None] if result is None else result
            if gui_name == GuiName.VERIFICATION_VERIFY.name:
                self.check_capcha()
            elif gui_name == GuiName.VERIFICATION_CHEST.name:
                self.check_capcha()
            elif gui_name == GuiName.VERIFICATION_CHEST1.name:
                self.check_capcha()
            # elif gui_name == GuiName.VERIFICATION_CLOSE_REFRESH_OK.name and pos_list is None:
            #     pos_list = self.pass_verification()
            else:
                return result
        if not pos_list:
            raise Exception("Could not pass verification")

    def pass_verification(self):
        pos_list = None
        try:
            self.set_text(insert="pass verification")
            box = (400, 70, 880, 625)
            ok = [780, 680]
            img = self.gui.get_curr_device_screen_img()
            img = img.crop(box)
            if config.global_config.method == HAO_I:
                pos_list = haoi.solve_verification(img)
            elif config.global_config.method == TWO_CAPTCHA:
                pos_list = twocaptcha.solve_verification(img)

            if pos_list is None:
                self.set_text(insert="fail to pass verification")
                return None

            for pos in pos_list:
                self.tap(400 + pos[0], pos[1] + 70, 1)
            self.tap(randrange(700, 800), randrange(565, 605), 5)

        except Exception as e:
            self.tap(100, 100)
            traceback.print_exc()

        return pos_list

    def check_capcha(self):
        """
        CAPTCHA kontrolü yapar ve çözer
        Not: Bu fonksiyon her zaman debug modu olmadan çalışır
        """
        # Geçici olarak debug modunu devre dışı bırak
        original_debug_mode = self.debug_mode
        self.debug_mode = False

        try:
            (found, _, pos) = self.gui.check_any(
                ImagePathAndProps.VERIFICATION_VERIFY_TITLE_IMAGE_PATH.value
            )
            if found:
                self.set_text(insert="CAPTCHA doğrulama ekranı tespit edildi")
                self.tap(pos[0], pos[1] + 258, 1)
                time.sleep(5)
                self.pass_verification()

            (found, _, pos) = self.gui.check_any(
                ImagePathAndProps.VERIFICATION_VERIFY_BUTTON_IMAGE_PATH.value
            )
            if found:
                self.set_text(insert="CAPTCHA doğrulama butonu tespit edildi")
                self.tap(pos[0], pos[1], 1)
                time.sleep(5)
                self.pass_verification()

            (found, _, pos) = self.gui.check_any(
                GuiCheckImagePathAndProps.VERIFICATION_CHEST_IMG_PATH.value,
                GuiCheckImagePathAndProps.VERIFICATION_CHEST1_IMG_PATH.value,
            )
            if found:
                self.set_text(insert="CAPTCHA sandık tespit edildi")
                self.tap(pos[0], pos[1], 1)
                time.sleep(5)
                self.pass_verification()
        finally:
            # Debug modunu eski haline getir
            self.debug_mode = original_debug_mode

    def has_buff(self, checking_location, buff_img_props):
        # Where to check
        if checking_location == HOME:
            self.back_to_home_gui()
        elif checking_location == MAP:
            self.back_to_map_gui()
        else:
            return False
        # Start Checking
        has, _, _ = self.gui.check_any(buff_img_props)
        return has

    def use_item(self, using_location, item_img_props_list):
        # Where to use the item
        if using_location == HOME:
            self.back_to_home_gui()
        elif using_location == MAP:
            self.back_to_map_gui()
        else:
            return False

        items_icon_pos = (930, 675)
        use_btn_pos = (980, 600)

        for item_img_props in item_img_props_list:
            path, size, box, threshold, least_diff, tab_name = item_img_props

            tabs_pos = {
                RESOURCES: (250, 80),
                SPEEDUPS: (435, 80),
                BOOSTS: (610, 80),
                EQUIPMENT: (790, 80),
                OTHER: (970, 80),
            }
            # open menu
            self.menu_should_open(True)
            # open items window
            x, y = items_icon_pos
            self.tap(x, y, 2)
            # tap on tab
            x, y = tabs_pos[tab_name]
            self.tap(x, y, 1)
            # find item, and tap it
            _, _, item_pos = self.gui.check_any(item_img_props)
            if item_pos is None:
                continue
            x, y = item_pos
            self.tap(x, y, 0.5)
            # tap on use Item
            x, y = use_btn_pos
            self.tap(x, y)
            return True
        return False

    # Action
    def back(self, sleep_time=0.5):
        cmd = "input keyevent 4"
        self.device.shell(cmd)
        time.sleep(sleep_time)

    # duration is in milliseconds
    def swipe(self, x_f, y_f, x_t, y_t, times=1, duration=300):
        cmd = "input swipe {} {} {} {} {}".format(x_f, y_f, x_t, y_t, duration)
        for i in range(times):
            self.device.shell(cmd)
            time.sleep(duration / 1000 + 0.2)

    def zoom(self, x_f, y_f, x_t, y_t, times=1, duration=300, zoom_type="out"):
        cmd_hold = "input swipe {} {} {} {} {}".format(
            x_t, y_t, x_t, y_t, duration + 50
        )
        if type == "out":
            cmd_swipe = "input swipe {} {} {} {} {}".format(
                x_f, y_t, x_f, y_t, duration
            )
        else:
            cmd_swipe = "input swipe {} {} {} {} {}".format(
                x_t, y_t, x_f, y_f, duration
            )

        for i in range(times):
            self.device.shell(cmd_hold)
            self.device.shell(cmd_swipe)
            time.sleep(duration / 1000 + 0.5 + 0.2)

    def move(self, direction="up"):
        cmd_hold = "input swipe 200 300 200 400 200"
        if direction == "down":
            cmd_hold = "input swipe 200 300 200 200 200"
        elif direction == "right":
            cmd_hold = "input swipe 200 300 100 300 200"
        elif direction == "left":
            cmd_hold = "input swipe 200 300 300 300 200"
        self.device.shell(cmd_hold)
        time.sleep(0.1)

    # long_press_duration is in milliseconds
    def tap(self, x, y, sleep_time=0.1, long_press_duration=-1):
        cmd = None
        if long_press_duration > -1:
            cmd = "input swipe {} {} {} {} {}".format(
                x, y, x, y, long_press_duration
            )
            sleep_time = long_press_duration / 1000 + 0.2
        else:
            cmd = "input tap {} {}".format(x, y)

        str = self.device.shell(cmd)
        time.sleep(sleep_time)

    # edit by seashell-freya, github: https://github.com/seashell-freya
    def isRoKRunning(self):
        cmd = "dumpsys window windows | grep mCurrentFocus"
        str = self.device.shell(cmd)
        return (
            str.find("com.lilithgame.roc.gp/com.harry.engine.MainActivity")
            != -1
        )

    def runOfRoK(self):
        cmd = "am start -n com.lilithgame.roc.gp/com.harry.engine.MainActivity"
        str = self.device.shell(cmd)

    def stopRok(self):
        cmd = "am force-stop com.lilithgame.roc.gp"
        str = self.device.shell(cmd)

    def set_text(self, **kwargs):
        dt_string = datetime.now().strftime("[%H:%M:%S]")
        title = "title"
        text_list = "text_list"
        insert = "insert"
        remove = "remove"
        replace = "replace"
        index = "index"
        append = "append"

        if title in kwargs:
            self.bot.text[title] = kwargs[title]
            print(kwargs[title])

        if replace in kwargs:
            self.bot.text[text_list][kwargs[index]] = (
                dt_string + " " + kwargs[replace].lower()
            )
            print(f"\t* {dt_string} {kwargs[replace].lower()}")

        if insert in kwargs:
            self.bot.text[text_list].insert(
                kwargs.get(index, 0), dt_string + " " + kwargs[insert].lower()
            )
            print(f"\t* {dt_string} {kwargs[insert].lower()}")

        if append in kwargs:
            self.bot.text[text_list].append(
                dt_string + " " + kwargs[append].lower()
            )
            print(f"\t* {dt_string} {kwargs[append].lower()}")

        if remove in kwargs and kwargs.get(remove, False):
            self.bot.text[text_list].clear()

        self.bot.text_update_event(self.bot.text)

    def do(self, next_task):
        return next_task

    def enable_debug(self):
        """Debug modunu etkinleştirir"""
        self.debug_mode = True
        self.gui.debug = True
        print("Debug modu etkinleştirildi")

    def disable_debug(self):
        """Debug modunu devre dışı bırakır"""
        self.debug_mode = False
        self.gui.debug = False
        print("Debug modu devre dışı bırakıldı")

    def toggle_debug(self):
        """Debug modunu açar veya kapatır"""
        if self.debug_mode:
            self.disable_debug()
        else:
            self.enable_debug()
        return self.debug_mode

    def save_debug_image(self, prefix):
        """
        Ekran görüntüsünü debug_images klasörüne kaydeder

        Args:
            prefix: Dosya adı öneki

        Returns:
            str: Kaydedilen dosyanın yolu
        """
        print(
            f"Debug: save_debug_image çağrıldı, prefix={prefix}, debug_mode={self.debug_mode}"
        )

        try:
            # Tarih ve saat bilgisini al
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Dosya adını oluştur - sadece ASCII karakterler kullan
            # Türkçe karakterleri ve özel karakterleri temizle
            safe_prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")
            filename = f"{safe_prefix}_{timestamp}.png"

            # Tam dosya yolunu oluştur
            filepath = os.path.join(self.debug_dir, filename)

            # Debug klasörünün varlığını kontrol et
            if not os.path.exists(self.debug_dir):
                os.makedirs(self.debug_dir)
                print(f"Debug: '{self.debug_dir}' klasoru olusturuldu")

            # Ekran görüntüsünü kaydet
            print(f"Debug: Ekran görüntüsü alınıyor: {filepath}")
            screen_img = self.gui.get_curr_device_screen_img_byte_array()
            with open(filepath, "wb") as f:
                f.write(screen_img)

            print(f"Debug: Ekran goruntusu kaydedildi: {filepath}")

            return filepath
        except Exception as e:
            print(f"Debug: Ekran goruntusu kaydedilirken hata olustu: {str(e)}")
            traceback.print_exc()
            return None

    def create_reference_image(self, x, y, width, height, output_path):
        """
        Ekran görüntüsünden belirli bir bölgeyi keserek referans görüntü oluşturur

        Args:
            x, y: Kesilen bölgenin sol üst köşesinin koordinatları
            width, height: Kesilen bölgenin genişliği ve yüksekliği
            output_path: Kaydedilecek dosyanın yolu

        Returns:
            bool: Başarılı ise True, değilse False
        """
        if not self.debug_mode:
            return False

        try:
            # Ekran görüntüsünü al
            screen_img = self.gui.get_curr_device_screen_img_byte_array()
            # NumPy dizisine dönüştür
            np_arr = np.frombuffer(screen_img, np.uint8)
            # OpenCV ile görüntüyü oku
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Koordinatları sınırla
            h, w = img.shape[:2]
            x = max(0, min(x, w - 1))
            y = max(0, min(y, h - 1))
            width = max(1, min(width, w - x))
            height = max(1, min(height, h - y))

            # Belirtilen bölgeyi kes
            cropped = img[y : y + height, x : x + width]

            # Çıktı klasörünü kontrol et
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Dosyaya kaydet
            cv2.imwrite(output_path, cropped)
            print(f"Debug: Referans goruntu olusturuldu: {output_path}")
            print(
                f"Debug: Kesilen bolge: x={x}, y={y}, genislik={width}, yukseklik={height}"
            )

            return True
        except Exception as e:
            print(
                f"Debug: Referans goruntu olusturulurken hata olustu: {str(e)}"
            )
            traceback.print_exc()
            return False

    def debug_image_match(self, image_path_and_props, screen_img=None):
        """
        Görüntü eşleştirme işleminin debug bilgilerini gösterir ve kaydeder

        Args:
            image_path_and_props: Eşleştirilecek görüntünün özellikleri
            screen_img: Ekran görüntüsü (None ise yeni bir ekran görüntüsü alınır)

        Returns:
            tuple: (found, name, pos) - Eşleşme sonucu
        """
        if not self.debug_mode:
            # Debug modu kapalıysa normal check_any fonksiyonunu kullan
            return self.gui.check_any(image_path_and_props)

        try:
            # Ekran görüntüsünü al
            if screen_img is None:
                screen_img = self.gui.get_curr_device_screen_img_byte_array()

            # NumPy dizisine dönüştür
            np_arr = np.frombuffer(screen_img, np.uint8)
            # OpenCV ile görüntüyü oku
            screen_cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Referans görüntüyü oku
            path, size, box, threshold, least_diff, gui = image_path_and_props
            ref_img_path = resource_path(path)
            ref_cv_img = cv2.imread(ref_img_path)

            if ref_cv_img is None:
                print(f"Debug: Referans goruntu yuklenemedi: {path}")
                return False, None, None

            # Zaman damgası oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Görüntüleri kaydet
            # Dosya adlarını daha anlamlı hale getir
            image_name = os.path.basename(path).split(".")[0]  # Uzantıyı kaldır
            screen_debug_path = os.path.join(
                self.debug_dir, f"screen_{image_name}_{timestamp}.png"
            )
            ref_debug_path = os.path.join(
                self.debug_dir, f"ref_{image_name}_{timestamp}.png"
            )

            cv2.imwrite(screen_debug_path, screen_cv_img)
            cv2.imwrite(ref_debug_path, ref_cv_img)

            # Görüntü eşleştirme işlemini gerçekleştir
            result = aircv.find_template(ref_cv_img, screen_cv_img, threshold)

            # Debug bilgilerini göster
            print(f"Debug: Goruntu eslestirme - {os.path.basename(path)}")
            print(f"Debug: Referans goruntu boyutu: {ref_cv_img.shape}")
            print(f"Debug: Ekran goruntusu boyutu: {screen_cv_img.shape}")
            print(f"Debug: Eslesme esigi: {threshold}")

            if result is not None:
                confidence = result["confidence"]
                match_pos = result["result"]
                print(f"Debug: Eslesme bulundu - Konum: {match_pos}")
                print(f"Debug: Eslesme guveni: {confidence}")

                # Eşleşen bölgeyi işaretle ve kaydet
                match_x, match_y = match_pos
                h, w = ref_cv_img.shape[:2]
                top_left = (int(match_x - w / 2), int(match_y - h / 2))
                bottom_right = (int(match_x + w / 2), int(match_y + h / 2))

                result_img = screen_cv_img.copy()
                cv2.rectangle(
                    result_img, top_left, bottom_right, (0, 255, 0), 2
                )
                cv2.circle(
                    result_img, (int(match_x), int(match_y)), 5, (0, 0, 255), -1
                )

                result_debug_path = os.path.join(
                    self.debug_dir, f"match_{image_name}_{timestamp}.png"
                )
                cv2.imwrite(result_debug_path, result_img)

                print(
                    f"Debug: Eslesme goruntusu kaydedildi: {result_debug_path}"
                )
                return True, gui, match_pos
            else:
                print("Debug: Eslesme bulunamadi")

                # Eşleşme bulunamadığında olası nedenleri analiz et
                # 1. Boyut farkı kontrolü
                h1, w1 = ref_cv_img.shape[:2]
                h2, w2 = screen_cv_img.shape[:2]
                if abs(h1 / h2 - 1) > 0.2 or abs(w1 / w2 - 1) > 0.2:
                    print(
                        "Debug: Boyut farki tespit edildi - Referans goruntu ve ekran goruntusu arasinda onemli boyut farki var"
                    )

                # 2. Renk farkı kontrolü
                ref_hsv = cv2.cvtColor(ref_cv_img, cv2.COLOR_BGR2HSV)
                screen_hsv = cv2.cvtColor(screen_cv_img, cv2.COLOR_BGR2HSV)

                ref_hist = cv2.calcHist(
                    [ref_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256]
                )
                screen_hist = cv2.calcHist(
                    [screen_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256]
                )

                cv2.normalize(ref_hist, ref_hist, 0, 1, cv2.NORM_MINMAX)
                cv2.normalize(screen_hist, screen_hist, 0, 1, cv2.NORM_MINMAX)

                color_similarity = cv2.compareHist(
                    ref_hist, screen_hist, cv2.HISTCMP_CORREL
                )
                print(f"Debug: Renk benzerligi: {color_similarity:.2f}")

                if color_similarity < 0.5:
                    print(
                        "Debug: Renk farki tespit edildi - Referans goruntu ve ekran goruntusu arasinda onemli renk farki var"
                    )

                # 3. Eşik değeri önerisi
                print(f"Debug: Mevcut esik degeri: {threshold}")
                if threshold > 0.7:
                    print(
                        f"Debug: Daha dusuk bir esik degeri denenebilir, ornegin: {threshold-0.1:.2f}"
                    )

                # Eşleşme bulunamadığında, eşleşme olmadığını gösteren bir görüntü oluştur
                no_match_img = screen_cv_img.copy()
                # Ekranın ortasına referans görüntüyü yerleştir (küçük boyutta)
                ref_small = cv2.resize(ref_cv_img, (w1 // 2, h1 // 2))
                h_small, w_small = ref_small.shape[:2]
                center_y, center_x = h2 // 2, w2 // 2
                y_offset, x_offset = (
                    center_y - h_small // 2,
                    center_x - w_small // 2,
                )

                # Referans görüntüyü ekran görüntüsüne yerleştir
                try:
                    no_match_img[
                        y_offset : y_offset + h_small,
                        x_offset : x_offset + w_small,
                    ] = ref_small
                    # Çerçeve çiz
                    cv2.rectangle(
                        no_match_img,
                        (x_offset, y_offset),
                        (x_offset + w_small, y_offset + h_small),
                        (0, 0, 255),
                        2,
                    )
                    # "Eşleşme bulunamadı" yazısı ekle
                    cv2.putText(
                        no_match_img,
                        "Eslesme bulunamadi",
                        (x_offset, y_offset - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )
                except:
                    # Yerleştirme hatası olursa geç
                    pass

                no_match_path = os.path.join(
                    self.debug_dir, f"no_match_{image_name}_{timestamp}.png"
                )
                cv2.imwrite(no_match_path, no_match_img)
                print(
                    f"Debug: Eslesme bulunamadi goruntusu kaydedildi: {no_match_path}"
                )

                return False, None, None

        except Exception as e:
            print(f"Debug: Goruntu eslestirme debug isleminde hata: {str(e)}")
            traceback.print_exc()
            # Hata durumunda normal check_any fonksiyonunu kullan
            return self.gui.check_any(image_path_and_props)

    def debug_check_any(self, *props_list):
        """
        Birden fazla görüntü için eşleştirme işleminin debug bilgilerini gösterir

        Args:
            props_list: Eşleştirilecek görüntülerin özellikleri

        Returns:
            tuple: (found, name, pos) - Eşleşme sonucu
        """
        print(
            f"Debug: debug_check_any çağrıldı, debug_mode = {self.debug_mode}"
        )

        if not self.debug_mode:
            # Debug modu kapalıysa normal check_any fonksiyonunu kullan
            print("Debug: debug_mode kapalı, normal check_any kullanılıyor")
            return self.gui.check_any(*props_list)

        try:
            # Ekran görüntüsünü bir kez al ve tüm eşleştirmelerde kullan
            print("Debug: Ekran görüntüsü alınıyor")
            screen_img = self.gui.get_curr_device_screen_img_byte_array()

            # Eşleştirme başlangıç zamanını kaydet
            start_time = time.time()

            # Tüm görüntüleri kontrol et
            for props in props_list:
                try:
                    print(
                        f"Debug: Görüntü eşleştiriliyor: {props[0] if len(props) > 0 else 'bilinmeyen'}"
                    )
                    result = self.debug_image_match(props, screen_img)
                    if result[0]:  # Eşleşme bulundu
                        # Eşleştirme süresini hesapla
                        elapsed_time = time.time() - start_time
                        print(
                            f"Debug: Eslestirme suresi: {elapsed_time:.3f} saniye"
                        )
                        return result
                except Exception as e:
                    print(f"Debug: Goruntu eslestirme hatasi: {str(e)}")
                    traceback.print_exc()
                    continue

            # Eşleştirme süresini hesapla
            elapsed_time = time.time() - start_time
            print(
                f"Debug: Eslestirme bulunamadi, toplam sure: {elapsed_time:.3f} saniye"
            )

            # Eşleşme bulunamadı, debug görüntüsü kaydet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_img_path = os.path.join(
                self.debug_dir, f"no_match_any_{timestamp}.png"
            )
            with open(debug_img_path, "wb") as f:
                f.write(screen_img)
            print(
                f"Debug: Eslesme bulunamadi goruntusu kaydedildi: {debug_img_path}"
            )

            return False, None, None
        except Exception as e:
            print(f"Debug: debug_check_any fonksiyonunda hata: {str(e)}")
            traceback.print_exc()
            # Hata durumunda normal check_any fonksiyonunu kullan
            return self.gui.check_any(*props_list)

    def clean_debug_directory_completely(self):
        """
        Debug klasöründeki tüm dosyaları temizler
        """
        if not os.path.exists(self.debug_dir):
            try:
                os.makedirs(self.debug_dir)
                print(f"Debug: '{self.debug_dir}' klasoru olusturuldu")
            except Exception as e:
                print(f"Debug: Klasor olusturulurken hata: {str(e)}")
            return

        try:
            # Klasördeki dosya sayısını kontrol et
            file_count = len(
                [
                    f
                    for f in os.listdir(self.debug_dir)
                    if os.path.isfile(os.path.join(self.debug_dir, f))
                ]
            )

            # Klasördeki tüm dosyaları sil
            for filename in os.listdir(self.debug_dir):
                filepath = os.path.join(self.debug_dir, filename)
                try:
                    if os.path.isfile(filepath) or os.path.islink(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                except Exception as e:
                    print(f"Debug: Dosya silinirken hata: {str(e)}")

            print(
                f"Debug: Tum dosyalar temizlendi. Toplam {file_count} dosya silindi."
            )

        except Exception as e:
            print(f"Debug: Klasor temizleme hatasi: {str(e)}")
            traceback.print_exc()

            # Hata durumunda klasörü yeniden oluşturmayı dene
            try:
                shutil.rmtree(self.debug_dir)
                os.makedirs(self.debug_dir)
                print(f"Debug: '{self.debug_dir}' klasoru yeniden olusturuldu")
            except Exception as e2:
                print(f"Debug: Klasor yeniden olusturulurken hata: {str(e2)}")
