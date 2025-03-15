import traceback
from filepath.file_relative_paths import ImagePathAndProps
from tasks.Task import Task
from tasks.constants import TaskName
import random
import time


class Alliance(Task):
    def __init__(self, bot):
        super().__init__(bot)

    def do(self, next_task=TaskName.MATERIALS):
        super().set_text(title="Alliance", remove=True)
        alliance_btn_pos = (970, 630)

        # Debug modu kontrolü
        if self.debug_mode:
            print("Debug: Alliance gorevi baslatiliyor")
            print("Debug: Alliance buton pozisyonu:", alliance_btn_pos)

        try:
            for name in ["HELP", "GIFTS", "TERRITORY", "TECHNOLOGY"]:
                super().set_text(insert="Open alliance")
                super().back_to_home_gui()
                super().menu_should_open(True)
                x, y = alliance_btn_pos
                super().tap(x, y, 3)

                if name == "HELP":
                    super().set_text(insert="Help Alliance")
                    super().tap(941, 406)  # enter the help page
                    super().tap(
                        650, 650
                    )  # tap the help button if present, otherwise it will tap on empty space

                elif name == "GIFTS":
                    super().set_text(insert="Claim gift")
                    gifts_pos = (1058, 400)
                    rate_pos = (981, 283)
                    normal_pos = (670, 205)
                    claim_all_pos = (1108, 202)
                    treasure = (332, 438)
                    x, y = gifts_pos
                    super().tap(x, y, 2)

                    # collecting rate gifts
                    super().set_text(insert="Claim rate gift")
                    x, y = rate_pos
                    super().tap(x, y, 1)
                    for i in range(20):
                        # Debug modu aktifse debug_check_any kullan
                        if self.debug_mode:
                            _, _, pos = self.debug_check_any(
                                ImagePathAndProps.GIFTS_CLAIM_BUTTON_IMAGE_PATH.value
                            )
                            if pos is None:
                                self.save_debug_image(
                                    "alliance_claim_button_not_found"
                                )
                                break
                        else:
                            _, _, pos = self.gui.check_any(
                                ImagePathAndProps.GIFTS_CLAIM_BUTTON_IMAGE_PATH.value
                            )
                            if pos is None:
                                break

                        # Buton bulunduysa tıkla
                        x, y = pos
                        super().tap(x, y, 0.5)

                    # collecting normal gifts
                    super().set_text(insert="Claim normal gift")
                    x, y = normal_pos
                    super().tap(x, y, 1)
                    x, y = claim_all_pos
                    super().tap(x, y, 1)

                    # collecting treasure of white crystal
                    x, y = treasure
                    super().tap(x, y, 1)

                elif name == "TERRITORY":
                    super().set_text(insert="Claim resource")
                    territory_pos = (827, 397)
                    claim_pos = (1028, 138)
                    x, y = territory_pos
                    super().tap(x, y, 2)
                    x, y = claim_pos
                    super().tap(x, y, 1)

                elif name == "TECHNOLOGY":
                    super().set_text(insert="Donate technology")
                    technology_pos = (699, 555)
                    x, y = technology_pos
                    super().tap(x, y, 5)

                    # Debug modu aktifse debug_check_any kullan
                    if self.debug_mode:
                        _, _, recommend_image_pos = self.debug_check_any(
                            ImagePathAndProps.TECH_RECOMMEND_IMAGE_PATH.value
                        )
                        if recommend_image_pos is None:
                            self.save_debug_image(
                                "alliance_tech_recommend_not_found"
                            )
                    else:
                        _, _, recommend_image_pos = self.gui.check_any(
                            ImagePathAndProps.TECH_RECOMMEND_IMAGE_PATH.value
                        )

                    if recommend_image_pos is not None:
                        x, y = recommend_image_pos
                        super().tap(x, y + 60, 1)

                        # Debug modu aktifse debug_check_any kullan
                        if self.debug_mode:
                            _, _, donate_btn_pos = self.debug_check_any(
                                ImagePathAndProps.TECH_DONATE_BUTTON_IMAGE_PATH.value
                            )
                            if donate_btn_pos is None:
                                self.save_debug_image(
                                    "alliance_tech_donate_button_not_found"
                                )
                        else:
                            _, _, donate_btn_pos = self.gui.check_any(
                                ImagePathAndProps.TECH_DONATE_BUTTON_IMAGE_PATH.value
                            )

                        if donate_btn_pos is not None:
                            x, y = donate_btn_pos
                            for i in range(20):
                                super().tap(x, y, 0.03)
                    else:
                        super().set_text(
                            insert="Cannot found Officer's Recommendation"
                        )

        except Exception as e:
            traceback.print_exc()
            return next_task
        return next_task
