from filepath.file_relative_paths import ImagePathAndProps
from tasks.Task import Task
import traceback

from tasks.constants import TaskName


class Expedition(Task):
    def __init__(self, bot):
        super().__init__(bot)

    def do(self, next_task=TaskName.MYSTERY_MERCHANT.value):
        self.set_text(title="Expedition")

        # Debug modu kontrolü
        if self.debug_mode:
            print("Debug: Expedition gorevi baslatiliyor")

        self.back_to_home_gui()
        self.home_gui_full_view()

        # Open the expedition page
        # Click expedition
        # Find the reward icon and click it
        # Click confirm
        # Add option to buy Constance, Aeth
        # Add option to buy legendary and epic sculptures
        # Add option to buy resources

        # Debug modu aktifse debug_check_any kullan
        if self.debug_mode:
            found, _, pos = self.debug_check_any(
                ImagePathAndProps.MERCHANT_ICON_IMAGE_PATH.value
            )
            if not found:
                self.save_debug_image("expedition_merchant_icon_not_found")
        else:
            found, _, pos = self.gui.check_any(
                ImagePathAndProps.MERCHANT_ICON_IMAGE_PATH.value
            )

        if not found:
            self.set_text(insert="Mystery Merchant not found", index=0)
            return next_task
        self.set_text(insert="Open Mystery Merchant")
        x, y = pos
        self.tap(x, y, 2)

        while True:
            for i in range(5):
                self.set_text(insert="buy item with food")

                # Debug modu aktifse debug görüntüsü kaydet
                if self.debug_mode:
                    self.save_debug_image("expedition_before_find_food_buttons")

                list = self.gui.find_all_image_props(
                    ImagePathAndProps.MERCHANT_BUY_WITH_FOOD_IMAGE_PATH.value
                )

                if self.debug_mode and not list:
                    self.save_debug_image("expedition_food_buttons_not_found")

                for buy_with_food_btn in list:
                    x, y = buy_with_food_btn["result"]
                    self.tap(x, y, 0.5)

                self.set_text(insert="buy item with wood")

                # Debug modu aktifse debug görüntüsü kaydet
                if self.debug_mode:
                    self.save_debug_image("expedition_before_find_wood_buttons")

                list = self.gui.find_all_image_props(
                    ImagePathAndProps.MERCHANT_BUY_WITH_WOOD_IMAGE_PATH.value
                )

                if self.debug_mode and not list:
                    self.save_debug_image("expedition_wood_buttons_not_found")

                for buy_with_wood_btn in list:
                    x, y = buy_with_wood_btn["result"]
                    self.tap(x, y, 0.5)

                self.swipe(730, 575, 730, 475, 1, 1000)

            # tap on free refresh
            found, _, pos = self.gui.check_any(
                ImagePathAndProps.MERCHANT_FREE_BTN_IMAGE_PATH.value
            )
            if not found:
                return next_task
            self.set_text(insert="Refresh")
            x, y = pos
            self.tap(x, y, 2)
