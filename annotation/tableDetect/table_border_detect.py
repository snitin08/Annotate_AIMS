import os
import cv2
import numpy as np
from annotation.settings import BASE_DIR
import pytesseract
from .deskew import *


def detect_border(image):
    image_base_path = os.path.join(BASE_DIR, "media", "masked_table.jpg")
    masked_tables = cv2.imread(image_base_path)
    img_gray = cv2.cvtColor(masked_tables, cv2.COLOR_BGR2GRAY)
    masked_tables_edge = np.zeros_like(masked_tables)
    _, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    canny = cv2.Canny(thresh, 127, 255, 1)
    contours, hierarchy = cv2.findContours(
        canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    image_height = masked_tables.shape[0]
    image_width = masked_tables.shape[1]
    table_index = 0
    image_save_base_path = os.path.join(BASE_DIR, "media", "tables")
    # Remove all files in image_save_base_path
    for file in os.listdir(image_save_base_path):
        os.remove(os.path.join(image_save_base_path, file))

    for (i, cnt) in enumerate(contours):
        if (
            cv2.contourArea(cnt) > image_height // 20 * 0.5 * image_width
            and hierarchy[0, i, 3] == -1
        ):
            x, y, w, h = cv2.boundingRect(cnt)
            sub_img = image[y : y + h, x : x + w]
            # print("TABLE {}".format(table_index + 1))
            cv2.imwrite(
                os.path.join(
                    image_save_base_path, "TABLE {}.jpg".format(table_index + 1)
                ),
                sub_img,
            )
            cv2.drawContours(masked_tables_edge, [cnt], -1, (0, 255, 0), 3)
            table_index = table_index + 1
    # cv2.imwrite(
    #     os.path.join(image_save_base_path, "masked_table_border.jpg"),
    #     masked_tables_edge,
    # )


def extract_text_ocr():
    # Tables base path
    tables_base_path = os.path.join(BASE_DIR, "media", "tables")
    extracted_text = []
    for file in os.listdir(tables_base_path):
        table_path = os.path.join(tables_base_path, file)
        image = cv2.imread(table_path)
        deskewed_image = deskewImage(image)
        table_text = pytesseract.image_to_string(
            deskewed_image, lang="eng_layer", config="--psm 6"
        )
        extracted_text.append(table_text)

        # Write Extracted text to file
        table_text_file_path = os.path.join(
            tables_base_path, "table_text_{}.txt".format(file.split(".")[0])
        )
        with open(table_text_file_path, "w") as f:
            f.write(table_text)
    return extracted_text