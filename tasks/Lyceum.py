import threading
import time
import numpy as np
from PIL import Image
import cv2
from pytesseract import image_to_string
from random import randrange
import webbrowser, queue
import traceback
from bot_related.bot_config import TrainingAndUpgradeLevel
from utils import resource_path
from filepath.file_relative_paths import ImagePathAndProps
from tasks.constants import TaskName
from tasks.Task import Task


class LyceumBot:
    def __init__(self):
        self.imageG = None
        self.midTerm = False
        self.xRes, self.yRes = 1920, 1080  # Replace with your actual resolution
        self.getTextFromImageQueue = queue.Queue()

    def lyceum_bot(self):
        self.image = self.capture_screenshot()
        self.process_image()

    def capture_screenshot(self):
        image = Task.screencap()
        with open(resource_path("screen.png"), "wb") as f:
            f.write(image)
        image = Image.open(resource_path("screen.png"))
        image = np.array(image, dtype=np.uint8)
        self.imageG = image
        return image

    def process_image(self):
        if not self.midTerm:
            threading.Thread(
                target=self.get_text_from_image, args=[0.2638, 0.90, 0.24, 0.39, True]
            ).start()
            threading.Thread(
                target=self.choose_answer, args=[self.get_text_from_image_queue.get()]
            ).start()
        else:
            threading.Thread(
                target=self.get_text_from_image, args=[0.25, 0.89, 0.31, 0.41, True]
            ).start()
            threading.Thread(
                target=self.choose_answer, args=[self.get_text_from_image_queue.get()]
            ).start()

    def get_text_from_image(self, x_beginning, x_end, y_beginning, y_end, is_title):
        x_local = -1
        y_local = -1
        x_total_pixels = round((x_end - x_beginning) * self.xRes)
        y_total_pixels = round((y_end - y_beginning) * self.yRes)

        new_image = np.zeros((y_total_pixels + 10, x_total_pixels + 10, 4))

        for x in range(round(x_beginning * self.xRes), round(x_end * self.xRes)):
            x_local += 1
            y_local = 0
            for y in range(round(y_beginning * self.yRes), round(y_end * self.yRes)):
                y_local += 1
                new_image[y_local][x_local] = self.image[y][x]

        new_image = np.array(new_image, dtype=np.uint8)
        im = Image.fromarray(new_image)
        random_n = randrange(20)
        ran = f"screenshots/reading{random_n}.png"
        im.save(resource_path(ran))

        img = cv2.imread(resource_path(ran), 0)

        if is_title:
            retval, img = cv2.threshold(img, 140, 90, cv2.THRESH_BINARY)
        else:
            retval, img = cv2.threshold(img, 215, 250, cv2.THRESH_BINARY)
            img = cv2.bitwise_not(img)

        img = cv2.resize(img, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        img = cv2.GaussianBlur(img, (11, 11), 0)
        img = cv2.medianBlur(img, 5)

        question = image_to_string(img, lang="eng").lower()
        self.get_text_from_image_queue.put(question)

    def choose_answer(self, question):
        answers = [...]  # your list of answers
        questions = [...]  # your list of questions

        for i in range(len(questions)):
            certainty = self.similarity(question, questions[i])
            print(f"Certainty for question {i}: {certainty}")

        best_question = max(
            range(len(questions)), key=lambda i: self.similarity(question, questions[i])
        )
        print(
            f"\nBest Question Found with {self.similarity(question, questions[best_question])} accuracy: \n{questions[best_question]}\n"
        )

        if not self.midTerm:
            threading.Thread(
                target=self.get_text_from_image, args=[0.25, 0.54, 0.4, 0.49, False]
            ).start()
            A = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.60, 0.89, 0.4, 0.49, False]
            ).start()
            B = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.25, 0.54, 0.54, 0.62, False]
            ).start()
            C = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.60, 0.89, 0.54, 0.62, False]
            ).start()
            D = self.get_text_from_image_queue.get().lower()

            answer_list = [A, B, C, D]
            best_answer = max(
                range(len(answers)),
                key=lambda i: self.similarity(answer_list[i], answers[i]),
            )
            print(
                f"Best Answer Found with {self.similarity(answer_list[best_answer], answers[best_answer])} accuracy: \n{answers[best_answer]}"
            )
            print(f"Correct answer: {answers[0]}\n")
        else:
            threading.Thread(
                target=self.get_text_from_image, args=[0.20, 0.55, 0.4, 0.49, False]
            ).start()
            A = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.65, 0.90, 0.4, 0.49, False]
            ).start()
            B = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.20, 0.55, 0.54, 0.62, False]
            ).start()
            C = self.get_text_from_image_queue.get().lower()
            threading.Thread(
                target=self.get_text_from_image, args=[0.65, 0.90, 0.54, 0.62, False]
            ).start()
            D = self.get_text_from_image_queue.get().lower()

            answer_list = [A, B, C, D]
            best_answer = max(
                range(len(answers)),
                key=lambda i: self.similarity(answer_list[i], answers[i]),
            )
            print(
                f"Best Answer Found with {self.similarity(answer_list[best_answer], answers[best_answer])} accuracy: \n{answers[best_answer]}"
            )
            print(f"Correct answer: {answers[0]}\n")

    def similarity(self, s1, s2):
        m = max(len(s1), len(s2))
        d = 0
        for i in range(m):
            if i < len(s1) and i < len(s2) and s1[i] != s2[i]:
                d += 1
        return 1 - d / m


if __name__ == "__main__":
    lyceumBot = LyceumBot()
    lyceumBot.lyceum_bot()
