import traceback
import random
import time
import cv2
import numpy as np

from filepath.file_relative_paths import ImagePathAndProps
from tasks.constants import TaskName, BuildingNames
from tasks.Task import Task
from tasks.ScreenShot import ScreenShot


class Scout(Task):
    def __init__(self, bot):
        super().__init__(bot)
        # Debug modu kontrolü
        print(f"Scout.__init__: debug_mode = {self.debug_mode}")
        # Debug modunu zorla etkinleştir (test için)
        if not self.debug_mode:
            print("Scout: Debug modu zorla etkinleştiriliyor")
            self.debug_mode = True
            if hasattr(self.gui, "debug"):
                self.gui.debug = True
        # Screenshot sınıfını başlat
        self.screenshot = ScreenShot(bot)

    def take_screenshot(self):
        """
        Ekran görüntüsü alır ve debug modunda kaydeder

        Returns:
            numpy.ndarray: Ekran görüntüsü
        """
        try:
            # Önce GUI'den ekran görüntüsü al
            screenshot = self.gui.get_curr_device_screen_img()

            if screenshot is None:
                # GUI'den alınamazsa ScreenShot sınıfını dene
                screenshot = self.screenshot.do_city_screen()

            if screenshot is not None and self.debug_mode:
                try:
                    # NumPy array'e dönüştür
                    if not isinstance(screenshot, np.ndarray):
                        screenshot = np.array(screenshot)
                    cv2.imwrite("debug_images/current_screen.png", screenshot)
                except Exception as e:
                    print(f"Debug: Screenshot kaydetme hatası: {str(e)}")

            return screenshot

        except Exception as e:
            if self.debug_mode:
                print(f"Debug: Screenshot alma hatası: {str(e)}")
                traceback.print_exc()
            return None

    def detect_exclamation_mark(self, screenshot=None):
        """
        Ekrandaki ünlem işaretlerini renk ve şekil bazlı tespit eder

        Args:
            screenshot: Ekran görüntüsü (None ise yeni görüntü alınır)

        Returns:
            list: Tespit edilen ünlem işaretlerinin koordinatları
        """
        try:
            if screenshot is None:
                screenshot = self.take_screenshot()

            if screenshot is None:
                if self.debug_mode:
                    print("Debug: Screenshot alınamadı")
                return []

            if self.debug_mode:
                self.save_debug_image("exclamation_detection_start")
                print("Debug: Ünlem işareti renk bazlı tespit ediliyor...")

            # Sarı-turuncu renk aralığı (ünlem işareti rengi)
            lower_yellow = np.array([15, 100, 100])  # Daha geniş renk aralığı
            upper_yellow = np.array([45, 255, 255])  # Daha geniş renk aralığı

            # BGR'den HSV'ye dönüştür
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

            # Sarı-turuncu renk maskesi oluştur
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

            if self.debug_mode:
                # Debug için maskeyi kaydet
                cv2.imwrite("debug_images/yellow_mask.png", mask)

            # Maskedeki konturları bul
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Ünlem işareti olabilecek konturları filtrele
            exclamation_marks = []
            for contour in contours:
                # Konturun alanını hesapla
                area = cv2.contourArea(contour)

                # Küçük gürültüleri filtrele (alan aralığını genişlettim)
                if area > 30 and area < 800:
                    # Konturun sınırlayıcı dikdörtgenini al
                    x, y, w, h = cv2.boundingRect(contour)

                    # Ünlem işareti genellikle dikey (h > w)
                    if h > w * 1.2:  # Daha esnek oran
                        # Merkez noktayı hesapla
                        center_x = x + w // 2
                        center_y = y + h // 2
                        exclamation_marks.append((center_x, center_y))

                        if self.debug_mode:
                            # Debug için konturları çiz
                            cv2.rectangle(
                                screenshot,
                                (x, y),
                                (x + w, y + h),
                                (0, 255, 0),
                                2,
                            )

            if self.debug_mode:
                # Debug için işaretlenmiş görüntüyü kaydet
                cv2.imwrite(
                    "debug_images/detected_exclamations.png", screenshot
                )
                print(
                    f"Debug: {len(exclamation_marks)} adet ünlem işareti tespit edildi"
                )

            return exclamation_marks

        except Exception as e:
            if self.debug_mode:
                print(f"Debug: Ünlem işareti tespit hatası: {str(e)}")
                traceback.print_exc()
            return []

    def detect_gift_icon(self, screenshot=None, village_pos=None):
        """
        Köylerdeki hediye paketi simgesini tespit eder

        Args:
            screenshot: Ekran görüntüsü (None ise yeni görüntü alınır)
            village_pos: Köyün pozisyonu (x, y)

        Returns:
            list: Tespit edilen hediye simgelerinin koordinatları
        """
        try:
            if screenshot is None:
                screenshot = self.take_screenshot()

            if screenshot is None:
                if self.debug_mode:
                    print("Debug: Screenshot alınamadı")
                return []

            if self.debug_mode:
                self.save_debug_image("gift_detection_start")
                print("Debug: Hediye paketi simgesi tespit ediliyor...")
                if village_pos:
                    print(f"Debug: Köy pozisyonu: {village_pos}")

            # Hediye paketi için renk aralığı (kahverengi-altın tonları)
            lower_brown = np.array([10, 50, 50])  # Kahverengi tonları için
            upper_brown = np.array(
                [30, 255, 255]
            )  # Altın/kahverengi tonları için

            # BGR'den HSV'ye dönüştür
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

            # Kahverengi-altın renk maskesi oluştur
            mask = cv2.inRange(hsv, lower_brown, upper_brown)

            if self.debug_mode:
                cv2.imwrite("debug_images/gift_mask.png", mask)

            # Maskedeki konturları bul
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Hediye paketi olabilecek konturları filtrele
            gift_icons = []
            for contour in contours:
                area = cv2.contourArea(contour)

                # Alan filtreleme - hediye paketi için daha spesifik
                if area > 100 and area < 2000:  # Biraz daha büyük alan aralığı
                    x, y, w, h = cv2.boundingRect(contour)

                    # Hediye paketi şekil oranı kontrolü
                    aspect_ratio = float(w) / h
                    if 0.7 < aspect_ratio < 1.3:  # Biraz daha esnek oran
                        center_x = x + w // 2
                        center_y = y + h // 2

                        # Eğer köy pozisyonu verilmişse, köye yakın olanları filtrele
                        if village_pos:
                            village_x, village_y = village_pos
                            # Köyün etrafında 150 piksellik bir alan içinde ara
                            if (
                                abs(center_x - village_x) <= 150
                                and abs(center_y - village_y) <= 150
                            ):
                                gift_icons.append((center_x, center_y))

                                if self.debug_mode:
                                    cv2.rectangle(
                                        screenshot,
                                        (x, y),
                                        (x + w, y + h),
                                        (0, 255, 0),
                                        2,
                                    )
                        else:
                            gift_icons.append((center_x, center_y))

                            if self.debug_mode:
                                cv2.rectangle(
                                    screenshot,
                                    (x, y),
                                    (x + w, y + h),
                                    (0, 255, 0),
                                    2,
                                )

            if self.debug_mode:
                cv2.imwrite("debug_images/detected_gifts.png", screenshot)
                print(
                    f"Debug: {len(gift_icons)} adet hediye simgesi tespit edildi"
                )

            return gift_icons

        except Exception as e:
            if self.debug_mode:
                print(f"Debug: Hediye simgesi tespit hatası: {str(e)}")
                traceback.print_exc()
            return []

    def detect_locations(self, screenshot=None):
        """
        Ekrandaki mağara ve köy gibi lokasyonları tespit eder

        Args:
            screenshot: Ekran görüntüsü (None ise yeni görüntü alınır)

        Returns:
            bool: Lokasyon bulundu ve tıklandı ise True, değilse False
        """
        try:
            if screenshot is None:
                screenshot = self.take_screenshot()

            if screenshot is None:
                if self.debug_mode:
                    print("Debug: Screenshot alınamadı")
                return False

            if self.debug_mode:
                self.save_debug_image("location_detection_start")
                print("Debug: Lokasyon tespit ediliyor...")

            # Scout butonunu kontrol et
            found, name, pos = self.debug_check_any(
                ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value
            )

            if found:
                if self.debug_mode:
                    print(f"Debug: Scout butonu bulundu - Pozisyon: {pos}")

                # Scout butonuna tıkla
                x, y = pos
                self.tap(x, y, 2)
                time.sleep(2)  # Oyunun konuma gitmesi için biraz daha bekle

                # Yeni screenshot al
                screenshot = self.take_screenshot()
                if screenshot is None:
                    return False

                # Investigate butonu veya köy görseli var mı kontrol et
                found, name, pos = self.debug_check_any(
                    ImagePathAndProps.INVESTIGATE_BUTTON_IMAGE_PATH.value,
                    ImagePathAndProps.VILLAGE_IMAGE_PATH.value,
                )

                if found:
                    if (
                        name
                        == ImagePathAndProps.INVESTIGATE_BUTTON_IMAGE_PATH.value[
                            5
                        ]
                    ):
                        if self.debug_mode:
                            print(
                                "Debug: Mağara tespit edildi - Investigate butonu bulundu"
                            )
                    else:
                        if self.debug_mode:
                            print("Debug: Köy tespit edildi")

                    # Bulunan görsele tıkla
                    x, y = pos
                    self.tap(x, y, 2)
                    return True
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Investigate butonu veya köy görseli bulunamadı"
                        )
                        self.save_debug_image("location_not_found")
                    # Ekranın ortasına tıklayarak pencereyi kapat
                    self.tap(640, 360, 1)

            if self.debug_mode:
                print("Debug: Scout butonu bulunamadı")
                self.save_debug_image("scout_button_not_found")

            return False

        except Exception as e:
            if self.debug_mode:
                print(f"Debug: Lokasyon tespit hatası: {str(e)}")
                traceback.print_exc()
            return False

    def find_and_tap_exclamation_mark(self):
        """
        Ekrandaki ünlem işaretlerini bulmaya çalışır ve tıklar

        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if self.debug_mode:
                self.save_debug_image("before_find_exclamation")
                print("Debug: Ünlem işareti aranıyor...")

            # Mail ikonuna tıkla (sağ alt köşe)
            mail_pos = [1130, 670]
            self.tap(mail_pos[0], mail_pos[1], 2)

            # Rapor sekmesine tıkla (sol üst köşe)
            report_pos = [263, 42]
            self.tap(report_pos[0], report_pos[1], 1)

            # Ekran görüntüsü al
            screenshot = self.take_screenshot()

            if screenshot is None:
                if self.debug_mode:
                    print("Debug: Screenshot alınamadı")
                return False

            # Önce mağara ve köy gibi lokasyonları tespit etmeyi dene
            if self.detect_locations(screenshot):
                return True

            # Renk bazlı ünlem işareti tespiti
            exclamation_marks = self.detect_exclamation_mark(screenshot)

            if exclamation_marks:
                # Tespit edilen ünlem işaretlerini dene
                for pos in exclamation_marks:
                    if self.debug_mode:
                        print(
                            f"Debug: Tespit edilen ünlem işareti pozisyonu deneniyor: {pos}"
                        )
                    self.tap(pos[0], pos[1], 1)

                    # Keşif raporu veya keşif butonu var mı kontrol et
                    found, name, _ = self.debug_check_any(
                        ImagePathAndProps.MAIL_EXPLORATION_REPORT_IMAGE_PATH.value,
                        ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value,
                    )

                    if found:
                        if self.debug_mode:
                            print(
                                f"Debug: Ünlem işareti bulundu ve tıklandı: {pos}"
                            )
                            self.save_debug_image("exclamation_mark_found")
                        return True

            # Renk bazlı tespit başarısız olursa, sabit pozisyonları dene
            # Ekranın farklı bölgelerinde ünlem işaretlerini kontrol et
            # Sağ taraftaki ünlem işaretleri
            right_side_positions = [
                # Mağara ve köy pozisyonları (gönderilen görsellere göre)
                (1150, 220),
                (1150, 270),
                (1150, 320),
                # Standart pozisyonlar
                (1150, 200),
                (1150, 250),
                (1150, 300),
                (1150, 350),
                (1150, 400),
                (1150, 450),
                # Sol taraf pozisyonları
                (130, 200),
                (130, 250),
                (130, 300),
                (130, 350),
                (130, 400),
                (130, 450),
            ]

            # Rastgele sırayla pozisyonları dene
            random.shuffle(right_side_positions)

            for pos in right_side_positions:
                if self.debug_mode:
                    print(f"Debug: Ünlem işareti pozisyonu deneniyor: {pos}")
                self.tap(pos[0], pos[1], 1)

                # Keşif raporu veya keşif butonu var mı kontrol et
                found, name, _ = self.debug_check_any(
                    ImagePathAndProps.MAIL_EXPLORATION_REPORT_IMAGE_PATH.value,
                    ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value,
                )

                if found:
                    if self.debug_mode:
                        print(
                            f"Debug: Ünlem işareti bulundu ve tıklandı: {pos}"
                        )
                        self.save_debug_image("exclamation_mark_found")
                    return True

            if self.debug_mode:
                print("Debug: Ünlem işareti bulunamadı")
                self.save_debug_image("exclamation_mark_not_found")
            return False

        except Exception as e:
            if self.debug_mode:
                print(f"Debug: Ünlem işareti arama hatası: {str(e)}")
                traceback.print_exc()
            return False

    def do(self, next_task=TaskName.BREAK):
        try:
            # Debug modu kontrolü
            print(f"Scout.do: debug_mode = {self.debug_mode}")
            # Debug modunu zorla etkinleştir (test için)
            if not self.debug_mode:
                print("Scout.do: Debug modu zorla etkinleştiriliyor")
                self.debug_mode = True
                if hasattr(self.gui, "debug"):
                    self.gui.debug = True

            self.set_text(title="Auto Scout")
            mail_pos = [1130, 670]
            report_pos = [263, 42]
            center_pos = (640, 320)

            # Debug modu kontrolü
            if self.debug_mode:
                print("Debug: Scout gorevi baslatiliyor")
                print("Debug: Mail pozisyonu:", mail_pos)
                print("Debug: Rapor pozisyonu:", report_pos)
                print("Debug: Merkez pozisyonu:", center_pos)
                # Test amaçlı debug görüntüsü kaydet
                self.save_debug_image("scout_test_start")

            idx = 0
            while self.bot.config.enableInvestigation:
                self.back_to_map_gui()
                self.set_text(insert="Open mail")

                # Ünlem işaretlerini bul ve tıkla
                if not self.find_and_tap_exclamation_mark():
                    if self.debug_mode:
                        print(
                            "Debug: Ünlem işareti bulunamadı, normal yöntemle devam ediliyor"
                        )

                    # Normal yöntemle devam et
                    x, y = mail_pos
                    self.tap(x, y, 2)
                    self.set_text(insert="Open report")
                    x, y = report_pos
                    self.tap(x, y, 1)

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    found, name, pos = self.debug_check_any(
                        ImagePathAndProps.MAIL_EXPLORATION_REPORT_IMAGE_PATH.value,
                        ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value,
                    )
                    if not found:
                        self.save_debug_image("scout_mail_not_found")
                        print("Debug: Keşif raporu bulunamadı")
                else:
                    found, name, pos = self.gui.check_any(
                        ImagePathAndProps.MAIL_EXPLORATION_REPORT_IMAGE_PATH.value,
                        ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value,
                    )

                if found:
                    if (
                        name
                        == ImagePathAndProps.MAIL_EXPLORATION_REPORT_IMAGE_PATH.value[
                            5
                        ]
                    ):
                        x, y = pos
                        self.tap(x, y, 2)

                    # Debug modunda görüntü arama
                    if self.debug_mode:
                        self.save_debug_image("scout_before_find_buttons")

                    result_list = self.gui.find_all_image_props(
                        ImagePathAndProps.MAIL_SCOUT_BUTTON_IMAGE_PATH.value
                    )

                    if self.debug_mode and not result_list:
                        self.save_debug_image("scout_buttons_not_found")
                        print("Debug: Keşif butonları bulunamadı")

                    result_list.sort(key=lambda result: result["result"][1])

                    if idx < len(result_list):
                        x, y = result_list[idx]["result"]
                        self.tap(x, y, 2)
                    else:
                        if self.debug_mode:
                            print("Debug: Tüm keşif butonları tüketildi")
                        break

                    x, y = pos
                    self.tap(x, y, 2)

                else:
                    if self.debug_mode:
                        print(
                            "Debug: Keşif raporu bulunamadığı için döngü sonlandırılıyor"
                        )
                    break

                x, y = center_pos
                self.tap(x, y, 0.1)
                self.tap(x, y, 0.1)
                self.tap(x, y, 0.1)
                self.tap(x, y, 0.1)
                self.tap(x, y, 0.5)

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    found, name, pos = self.debug_check_any(
                        ImagePathAndProps.INVESTIGATE_BUTTON_IMAGE_PATH.value,
                        ImagePathAndProps.GREAT_BUTTON_IMAGE_PATH.value,
                    )
                    if not found:
                        self.save_debug_image("scout_investigate_not_found")
                        print("Debug: Araştırma butonu bulunamadı")
                else:
                    found, name, pos = self.gui.check_any(
                        ImagePathAndProps.INVESTIGATE_BUTTON_IMAGE_PATH.value,
                        ImagePathAndProps.GREAT_BUTTON_IMAGE_PATH.value,
                    )

                if found:
                    x, y = pos
                    self.tap(x, y, 2)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Araştırma butonu bulunamadığı için devam ediliyor"
                        )
                    continue

                if (
                    name
                    == ImagePathAndProps.INVESTIGATE_BUTTON_IMAGE_PATH.value[5]
                ):
                    # Debug modu aktifse debug_check_any kullan
                    if self.debug_mode:
                        found, name, pos = self.debug_check_any(
                            ImagePathAndProps.SCOUT_IDLE_ICON_IMAGE_PATH.value,
                            ImagePathAndProps.SCOUT_ZZ_ICON_IMAGE_PATH.value,
                        )
                        if not found:
                            self.save_debug_image("scout_idle_icon_not_found")
                            print("Debug: Boşta keşif birliği bulunamadı")
                    else:
                        found, name, pos = self.gui.check_any(
                            ImagePathAndProps.SCOUT_IDLE_ICON_IMAGE_PATH.value,
                            ImagePathAndProps.SCOUT_ZZ_ICON_IMAGE_PATH.value,
                        )

                    if found:
                        x, y = pos
                        self.tap(x - 10, y - 10, 2)
                    else:
                        if self.debug_mode:
                            print(
                                "Debug: Boşta keşif birliği bulunamadığı için döngü sonlandırılıyor"
                            )
                        break

                    # Debug modu aktifse debug_check_any kullan
                    if self.debug_mode:
                        found, name, pos = self.debug_check_any(
                            ImagePathAndProps.SCOUT_SEND_BUTTON_IMAGE_PATH.value,
                        )
                        if not found:
                            self.save_debug_image("scout_send_button_not_found")
                            print("Debug: Gönder butonu bulunamadı")
                    else:
                        found, name, pos = self.gui.check_any(
                            ImagePathAndProps.SCOUT_SEND_BUTTON_IMAGE_PATH.value,
                        )

                    if found:
                        x, y = pos
                        self.tap(x, y, 2)
                    else:
                        if self.debug_mode:
                            print(
                                "Debug: Gönder butonu bulunamadığı için döngü sonlandırılıyor"
                            )
                        break
                else:
                    if self.debug_mode:
                        print("Debug: Araştırma butonu değil, devam ediliyor")
                    continue

                idx = idx + 1

            while True:
                self.set_text(insert="init view")
                self.back_to_home_gui()
                self.home_gui_full_view()

                # open scout interface
                self.set_text(insert="tap scout camp")
                scout_camp_pos = self.bot.building_pos[
                    BuildingNames.SCOUT_CAMP.value
                ]
                if self.debug_mode:
                    print(f"Debug: Scout camp pozisyonu: {scout_camp_pos}")
                    self.save_debug_image("scout_camp_position")

                x, y = scout_camp_pos
                self.tap(x, y, 1)

                # find and tap scout button
                self.set_text(insert="open scout camp")

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    is_found, _, btn_pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_BUTTON_IMAGE_PATH.value
                    )
                    if not is_found:
                        self.save_debug_image("scout_button_not_found")
                        print("Debug: Keşif butonu bulunamadı")
                else:
                    is_found, _, btn_pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_BUTTON_IMAGE_PATH.value
                    )

                if is_found:
                    x, y = btn_pos
                    self.tap(x, y, 1)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Keşif butonu bulunamadığı için görev sonlandırılıyor"
                        )
                    return next_task

                # find and tap explore button
                self.set_text(insert="try to tap explore")

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    is_found, _, btn_pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_EXPLORE_BUTTON_IMAGE_PATH.value
                    )
                    if not is_found:
                        self.save_debug_image("scout_explore_button_not_found")
                        print("Debug: Keşif butonu bulunamadı")
                else:
                    is_found, _, btn_pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_EXPLORE_BUTTON_IMAGE_PATH.value
                    )

                if is_found:
                    x, y = btn_pos
                    self.tap(x, y, 2)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Keşif butonu bulunamadığı için görev sonlandırılıyor"
                        )
                    return next_task

                # find and tap explore button
                self.set_text(insert="try to tap explore 2")

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    is_found, _, btn_pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_EXPLORE2_BUTTON_IMAGE_PATH.value
                    )
                    if not is_found:
                        self.save_debug_image("scout_explore2_button_not_found")
                        print("Debug: Keşif2 butonu bulunamadı")
                else:
                    is_found, _, btn_pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_EXPLORE2_BUTTON_IMAGE_PATH.value
                    )

                self.set_text(insert="try to tap explore3")

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    is_found, _, btn_pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_EXPLORE3_BUTTON_IMAGE_PATH.value
                    )
                    if not is_found:
                        self.save_debug_image("scout_explore3_button_not_found")
                        print("Debug: Keşif3 butonu bulunamadı")
                else:
                    is_found, _, btn_pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_EXPLORE3_BUTTON_IMAGE_PATH.value
                    )

                if is_found:
                    x, y = btn_pos
                    self.tap(x, y, 2)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Keşif3 butonu bulunamadığı için görev sonlandırılıyor"
                        )
                    return next_task

                self.set_text(insert="try to tap send")

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    found, name, pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_IDLE_ICON_IMAGE_PATH.value,
                        ImagePathAndProps.SCOUT_ZZ_ICON_IMAGE_PATH.value,
                    )
                    if not found:
                        self.save_debug_image("scout_idle_icon_not_found_2")
                        print("Debug: Boşta keşif birliği bulunamadı")
                else:
                    found, name, pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_IDLE_ICON_IMAGE_PATH.value,
                        ImagePathAndProps.SCOUT_ZZ_ICON_IMAGE_PATH.value,
                    )

                if found:
                    x, y = pos
                    self.tap(x - 10, y - 10, 2)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Boşta keşif birliği bulunamadığı için görev sonlandırılıyor"
                        )
                    return next_task

                # Debug modu aktifse debug_check_any kullan
                if self.debug_mode:
                    is_found, _, btn_pos = self.debug_check_any(
                        ImagePathAndProps.SCOUT_SEND_BUTTON_IMAGE_PATH.value
                    )
                    if not found:
                        self.save_debug_image("scout_send_button_not_found_2")
                        print("Debug: Gönder butonu bulunamadı")
                else:
                    is_found, _, btn_pos = self.gui.check_any(
                        ImagePathAndProps.SCOUT_SEND_BUTTON_IMAGE_PATH.value
                    )

                if is_found:
                    x, y = btn_pos
                    self.tap(x, y, 2)
                else:
                    if self.debug_mode:
                        print(
                            "Debug: Gönder butonu bulunamadığı için görev sonlandırılıyor"
                        )
                    return next_task
        except Exception as e:
            traceback.print_exc()
            return next_task

        return next_task
