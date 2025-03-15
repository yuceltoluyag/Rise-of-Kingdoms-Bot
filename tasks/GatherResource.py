import traceback
import os
import cv2
import numpy as np
from datetime import datetime

from filepath.constants import MAP
from filepath.file_relative_paths import (
    BuffsImageAndProps,
    ItemsImageAndProps,
    ImagePathAndProps,
)
from tasks.Task import Task
from tasks.constants import TaskName, Resource
from utils import resource_path


class GatherResource(Task):
    def __init__(self, bot):
        super().__init__(bot)
        self.max_query_space = 5
        # Debug klasörünü oluştur
        self.debug_dir = "debug_images"
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)

    def save_debug_image(self, prefix):
        try:
            # Tarih ve saat bilgisini al
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Dosya adını oluştur
            filename = f"{prefix}_{timestamp}.png"
            # Tam dosya yolunu oluştur
            filepath = os.path.join(self.debug_dir, filename)
            # Ekran görüntüsünü kaydet
            screen_img = self.gui.get_curr_device_screen_img_byte_array()
            with open(filepath, "wb") as f:
                f.write(screen_img)
            print(f"Debug: Ekran görüntüsü kaydedildi: {filepath}")
            return filepath
        except Exception as e:
            print(f"Debug: Ekran görüntüsü kaydedilirken hata oluştu: {str(e)}")
            return None

    def create_reference_image(self, x, y, width, height, output_path):
        """
        Ekran görüntüsünden belirli bir bölgeyi keserek referans görüntü oluşturur

        Args:
            x, y: Kesilen bölgenin sol üst köşesinin koordinatları
            width, height: Kesilen bölgenin genişliği ve yüksekliği
            output_path: Kaydedilecek dosyanın yolu
        """
        try:
            # Ekran görüntüsünü al
            screen_img = self.gui.get_curr_device_screen_img_byte_array()
            # NumPy dizisine dönüştür
            np_arr = np.frombuffer(screen_img, np.uint8)
            # OpenCV ile görüntüyü oku
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            # Belirtilen bölgeyi kes
            cropped = img[y : y + height, x : x + width]
            # Dosyaya kaydet
            cv2.imwrite(output_path, cropped)
            print(f"Debug: Referans görüntü oluşturuldu: {output_path}")
            return True
        except Exception as e:
            print(
                f"Debug: Referans görüntü oluşturulurken hata oluştu: {str(e)}"
            )
            return False

    def is_dispatch_screen_visible(self):
        """
        Ekranda "Dispatch a new troop from your city" yazısının olup olmadığını kontrol eder

        Returns:
            bool: Yazı varsa True, yoksa False
        """
        try:
            # Ekran görüntüsünü al
            screen_img = self.gui.get_curr_device_screen_img_byte_array()
            # NumPy dizisine dönüştür
            np_arr = np.frombuffer(screen_img, np.uint8)
            # OpenCV ile görüntüyü oku
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Dispatch yazısının olduğu bölgeyi kes (yaklaşık koordinatlar)
            # Gönderdiğiniz ekran görüntüsüne göre ayarlandı
            x, y, width, height = 930, 65, 200, 25
            dispatch_region = img[y : y + height, x : x + width]

            # Debug için kaydet
            cv2.imwrite("debug_images/dispatch_region.png", dispatch_region)

            # Basit bir kontrol: Bölgede açık renkli piksel sayısı
            # Dispatch yazısı açık renkli olduğu için, belirli bir eşiğin üzerinde açık piksel varsa
            # yazının görünür olduğunu varsayabiliriz
            gray = cv2.cvtColor(dispatch_region, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_pixel_count = cv2.countNonZero(binary)

            # Eşik değeri (deneysel olarak ayarlanabilir)
            threshold = 100

            print(
                f"Debug: Dispatch bölgesindeki açık piksel sayısı: {white_pixel_count}"
            )
            return white_pixel_count > threshold

        except Exception as e:
            print(f"Debug: Dispatch ekranı kontrolünde hata: {str(e)}")
            return False  # Hata durumunda False döndür

    def is_all_armies_busy(self):
        """
        Tüm birliklerin meşgul olup olmadığını kontrol eder

        Returns:
            bool: Tüm birlikler meşgulse True, değilse False
        """
        try:
            # Doğrudan AllArmiesBusy1.png ve AllArmiesBusy2.png dosyalarını kullanarak kontrol et
            if self.debug_mode:
                check_result1 = self.debug_image_match(
                    ImagePathAndProps.ALL_ARMIES_BUSY_IMAGE_PATH1.value
                )

                check_result2 = self.debug_image_match(
                    ImagePathAndProps.ALL_ARMIES_BUSY_IMAGE_PATH2.value
                )
            else:
                check_result1 = self.gui.check_any(
                    ImagePathAndProps.ALL_ARMIES_BUSY_IMAGE_PATH1.value
                )

                check_result2 = self.gui.check_any(
                    ImagePathAndProps.ALL_ARMIES_BUSY_IMAGE_PATH2.value
                )

            # Debug için ekran görüntüsünü kaydet
            if check_result1[0] or check_result2[0]:
                debug_img_path = self.save_debug_image(
                    "all_armies_busy_detected"
                )
                print(
                    f"Debug: Tüm birlikler meşgul tespit edildi! Görüntü: {debug_img_path}"
                )

                if check_result1[0]:
                    print("Debug: AllArmiesBusy1.png eşleşti")
                if check_result2[0]:
                    print("Debug: AllArmiesBusy2.png eşleşti")

                return True

            return False

        except Exception as e:
            print(
                f"Debug: Tüm birliklerin meşgul olup olmadığı kontrolünde hata: {str(e)}"
            )
            return False  # Hata durumunda False döndür

    def do(self, next_task=TaskName.BREAK):
        magnifier_pos = (60, 540)
        self.set_text(title="Gather Resource", remove=True)
        self.call_idle_back()

        # Debug modunu etkinleştir (isteğe bağlı olarak kullanılabilir)
        if self.bot.config.debug_mode:
            self.enable_debug()
            print("GatherResource görevi için debug modu etkinleştirildi")

        if self.bot.config.useGatheringBoosts:
            b_buff_props = BuffsImageAndProps.ENHANCED_GATHER_BLUE.value
            p_buff_props = BuffsImageAndProps.ENHANCED_GATHER_PURPLE.value
            b_item_props = ItemsImageAndProps.ENHANCED_GATHER_BLUE.value
            p_item_props = ItemsImageAndProps.ENHANCED_GATHER_PURPLE.value
            has_blue = self.has_buff(MAP, b_buff_props)
            has_purple = self.has_buff(MAP, p_buff_props)
            if not has_blue and not has_purple:
                self.set_text(insert="use gathering boosts")
                self.use_item(MAP, [b_item_props, p_item_props])
            else:
                self.set_text(insert="gathering boosts buff is already on")

        last_resource_pos = []
        should_decreasing_lv = False
        resource_icon_pos = [(450, 640), (640, 640), (830, 640), (1030, 640)]
        try:
            chose_icon_pos = resource_icon_pos[0]
            self.back_to_map_gui()
            resourse_code = self.get_min_resource()
            self.back_to_map_gui()

            if resourse_code == Resource.FOOD.value:
                chose_icon_pos = resource_icon_pos[0]
                self.set_text(insert="Search food")

            elif resourse_code == Resource.WOOD.value:
                chose_icon_pos = resource_icon_pos[1]
                self.set_text(insert="Search wood")

            elif resourse_code == Resource.STONE.value:
                chose_icon_pos = resource_icon_pos[2]
                self.set_text(insert="Search stone")

            elif resourse_code == Resource.GOLD.value:
                chose_icon_pos = resource_icon_pos[3]
                self.set_text(insert="Search gold")

            if self.bot.config.holdOneQuerySpace:
                space = self.check_query_space()
                if space <= 1:
                    self.set_text(
                        insert="Match query space less or equal to 1, stop!"
                    )
                    return next_task

            # tap on magnifier
            x, y = magnifier_pos
            self.tap(x, y, 1)
            self.tap(chose_icon_pos[0], chose_icon_pos[1], 1)

            # Debug modunda check_any yerine debug_check_any kullan
            if self.debug_mode:
                found, _, search_pos = self.debug_check_any(
                    ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value
                )
                found, _, dec_pos = self.debug_check_any(
                    ImagePathAndProps.DECREASING_BUTTON_IMAGE_PATH.value
                )
                found, _, inc_pos = self.debug_check_any(
                    ImagePathAndProps.INCREASING_BUTTON_IMAGE_PATH.value
                )
            else:
                search_pos = self.gui.check_any(
                    ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value
                )[2]
                dec_pos = self.gui.check_any(
                    ImagePathAndProps.DECREASING_BUTTON_IMAGE_PATH.value
                )[2]
                inc_pos = self.gui.check_any(
                    ImagePathAndProps.INCREASING_BUTTON_IMAGE_PATH.value
                )[2]

            self.tap(inc_pos[0] - 33, inc_pos[1], 0.3)

            repeat_count = 0
            for i in range(10):
                # open search resource
                if len(last_resource_pos) > 0:
                    self.back_to_map_gui()

                    if self.bot.config.holdOneQuerySpace:
                        space = self.check_query_space()
                        if space <= 1:
                            self.set_text(
                                insert="Match query space less or equal to 1, stop!"
                            )
                            return next_task

                    x, y = magnifier_pos
                    self.tap(x, y, 1)
                    self.tap(chose_icon_pos[0], chose_icon_pos[1], 1)

                # decreasing level
                if should_decreasing_lv:
                    self.set_text(insert="Decreasing level by 1")
                    self.tap(dec_pos[0], dec_pos[1], 0.3)

                for j in range(5):
                    self.tap(search_pos[0], search_pos[1], 2)

                    # Debug modunda check_any yerine debug_check_any kullan
                    if self.debug_mode:
                        is_found, _, _ = self.debug_check_any(
                            ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value
                        )
                    else:
                        is_found, _, _ = self.gui.check_any(
                            ImagePathAndProps.RESOURCE_SEARCH_BUTTON_IMAGE_PATH.value
                        )

                    if not is_found:
                        break
                    self.set_text(
                        insert="Not found, decreasing level by 1 [{}]".format(j)
                    )
                    self.tap(dec_pos[0], dec_pos[1], 0.3)

                self.set_text(insert="Resource found")
                self.tap(640, 320, 0.5)

                # check is same pos
                new_resource_pos = self.gui.resource_location_image_to_string()
                if new_resource_pos in last_resource_pos:
                    should_decreasing_lv = True
                    repeat_count = repeat_count + 1
                    self.set_text(insert="Resource point is already in match")
                    if repeat_count > 4:
                        self.set_text(insert="stuck! end task")
                        break
                    else:
                        continue
                last_resource_pos.append(new_resource_pos)
                should_decreasing_lv = False

                # Tüm birliklerin meşgul olup olmadığını kontrol et (GATHER butonuna tıklamadan önce)
                if self.is_all_armies_busy():
                    self.set_text(insert="All armies are busy, stopping task")
                    print("Debug: Tüm birlikler meşgul, görev sonlandırılıyor")
                    self.save_debug_image("all_armies_busy_before_gather")
                    return next_task

                # Önce normal yöntemle deneyelim
                if self.debug_mode:
                    check_result = self.debug_image_match(
                        ImagePathAndProps.RESOURCE_GATHER_BUTTON_IMAGE_PATH.value
                    )
                else:
                    check_result = self.gui.check_any(
                        ImagePathAndProps.RESOURCE_GATHER_BUTTON_IMAGE_PATH.value
                    )

                # Eğer bulunamazsa, alternatif yöntem kullanarak GATHER butonunu bulmaya çalışalım
                if not check_result[0]:
                    self.set_text(
                        insert="Trying alternative method to find gather button"
                    )
                    print("Debug: Alternatif yöntem deneniyor...")

                    # Ekran görüntüsünü kaydet
                    debug_img_path = self.save_debug_image(
                        "gather_button_screen"
                    )

                    # Yeni bir referans görüntü oluştur (GATHER butonu için)
                    # Gönderdiğiniz ekran görüntüsünde GATHER butonu yaklaşık olarak bu koordinatlarda
                    ref_img_path = "resource/resource_gather_button_new.png"
                    self.create_reference_image(
                        850, 480, 200, 40, resource_path(ref_img_path)
                    )

                    # Yeni oluşturulan referans görüntüyü kullanarak tekrar dene
                    # Sabit koordinatları kullan (ekran görüntüsünden)
                    gather_button_pos = (950, 500)  # GATHER butonunun merkezi
                    self.tap(gather_button_pos[0], gather_button_pos[1], 2)
                else:
                    gather_button_pos = check_result[2]
                    self.tap(gather_button_pos[0], gather_button_pos[1], 2)

                # Tüm birliklerin meşgul olup olmadığını kontrol et
                if self.is_all_armies_busy():
                    self.set_text(insert="All armies are busy, stopping task")
                    print("Debug: Tüm birlikler meşgul, görev sonlandırılıyor")
                    self.save_debug_image("all_armies_busy")
                    return next_task

                if self.debug_mode:
                    check_result = self.debug_image_match(
                        ImagePathAndProps.NEW_TROOPS_BUTTON_IMAGE_PATH.value
                    )
                else:
                    check_result = self.gui.check_any(
                        ImagePathAndProps.NEW_TROOPS_BUTTON_IMAGE_PATH.value
                    )

                # Eğer bulunamazsa, alternatif yöntem kullanarak NEW_TROOPS butonunu bulmaya çalışalım
                if not check_result[0]:
                    self.set_text(
                        insert="Trying alternative method to find new troops button"
                    )
                    print(
                        "Debug: Yeni birlik butonu için alternatif yöntem deneniyor..."
                    )

                    # Ekran görüntüsünü kaydet
                    debug_img_path = self.save_debug_image(
                        "new_troops_button_screen"
                    )

                    # Ekran görüntüsünde "Dispatch a new troop from your city" yazısı varsa, NEW_TROOPS butonunu kullanabiliriz
                    # Yoksa, muhtemelen daha fazla yürüyüş alanı yok

                    # Yeni bir referans görüntü oluştur (NEW_TROOPS butonu için)
                    ref_img_path = "resource/new_troops_button_new.png"
                    self.create_reference_image(
                        940, 145, 200, 40, resource_path(ref_img_path)
                    )

                    # Sabit koordinatları kullan (ekran görüntüsünden)
                    # Eğer "New Troop" butonu görünüyorsa tıkla, yoksa görevi sonlandır
                    if self.is_dispatch_screen_visible():
                        new_troops_button_pos = (
                            1010,
                            145,
                        )  # NEW_TROOPS butonunun merkezi
                        self.tap(
                            new_troops_button_pos[0],
                            new_troops_button_pos[1],
                            2,
                        )
                    else:
                        self.set_text(insert="Not more space for march")
                        print(
                            "Debug: Yeni birlik butonu bulunamadı ve dispatch ekranı görünmüyor"
                        )
                        print("Debug: Ekran görüntüsü kaydediliyor...")
                        self.save_debug_image("new_troops_button_not_found")
                        return next_task
                else:
                    new_troops_button_pos = check_result[2]
                    self.tap(
                        new_troops_button_pos[0], new_troops_button_pos[1], 2
                    )

                if self.bot.config.gatherResourceNoSecondaryCommander:
                    self.set_text(insert="Remove secondary commander")
                    self.tap(473, 462, 0.5)

                if self.debug_mode:
                    match_button_pos = self.debug_image_match(
                        ImagePathAndProps.TROOPS_MATCH_BUTTON_IMAGE_PATH.value
                    )[2]
                else:
                    match_button_pos = self.gui.check_any(
                        ImagePathAndProps.TROOPS_MATCH_BUTTON_IMAGE_PATH.value
                    )[2]

                self.set_text(insert="March")
                self.tap(match_button_pos[0], match_button_pos[1], 2)
                repeat_count = 0
                self.swipe(300, 720, 400, 360, 1)

        except Exception as e:
            traceback.print_exc()
            return next_task

        # Debug modunu devre dışı bırak
        if self.debug_mode:
            self.disable_debug()

        return next_task

    def get_min_resource(self):
        self.tap(725, 20, 1)
        result = self.gui.resource_amount_image_to_string()
        self.set_text(
            insert="\nFood: {}\nWood: {}\nStone: {}\nGold: {}\n".format(
                result[0], result[1], result[2], result[3]
            )
        )

        ratio = [
            self.bot.config.gatherResourceRatioFood,
            self.bot.config.gatherResourceRatioWood,
            self.bot.config.gatherResourceRatioStone,
            self.bot.config.gatherResourceRatioGold,
        ]

        ras = sum(ratio)
        res = sum(result)

        diff = []
        for i in range(4):
            diff.append(
                (ratio[i] / ras) - ((result[i] if result[i] > -1 else 0) / res)
            )

        m = 0
        for i in range(len(result)):
            if diff[m] < diff[i]:
                m = i
        return m

    def check_query_space(self):
        found, _, _ = self.gui.check_any(
            ImagePathAndProps.HAS_MATCH_QUERY_IMAGE_PATH.value
        )
        curr_q, max_q = self.gui.match_query_to_string()
        if curr_q is None:
            return self.max_query_space
        return max_q - curr_q
