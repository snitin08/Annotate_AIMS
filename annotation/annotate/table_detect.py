import pytesseract
from pytesseract import Output
import numpy as np
import cv2
import pandas as pd
import ast
import regex as re

# pytesseract.pytesseract.tesseract_cmd = "E:\\Downloads\\Tesseract OCR\\tesseract.exe"


def get_annotations_json(path):
    import json

    annotate_dict = json.load(open(path))

    new_dict = {}
    for k in annotate_dict.keys():
        new_dict[k] = {}
        if k != "ncols":
            for item in annotate_dict[k]:
                label = item["label"]
                x1 = int(item["left"])
                x2 = x1 + int(item["width"])
                y1 = int(item["top"])
                y2 = y1 + int(item["height"])
                new_dict[k][label] = (x1, y1, x2, y2)
        else:
            new_dict[k] = annotate_dict[k]
    print(new_dict)
    return new_dict


# get_annotations_json(r"E:\Nitin\RVCE\Projects\PDF-OCR\annotation_tool\annotation\media\data.json")


def colfilter(crds, image, NO_OF_COLS, ye):
    x, y, x1, y1 = crds
    if y1 <= ye:
        return 0
    tmp3 = np.copy(image)
    sub_image1 = tmp3[y:y1, x:x1]
    sub_image = cv2.cvtColor(sub_image1, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(sub_image, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    kernel = np.ones((3, 5), np.uint8)
    th = cv2.erode(th, kernel, iterations=5)
    th = cv2.dilate(th, kernel, iterations=5)
    th = np.pad(
        th,
        ((10, 10), (10, 10)),
        mode="constant",
        constant_values=((255, 255), (255, 255)),
    )
    th = 255 - th
    contours, hierarchy = cv2.findContours(
        th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    #    sbi = np.pad(sub_image1, ((10,10),(10,10),(0,0)), mode = 'constant',constant_values = ((255,255),(255,255),(0,0)))
    mask = np.zeros(th.shape, dtype=np.uint8)
    ct = 0
    li = list()
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y : y + h, x : x + w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y : y + h, x : x + w])) / (w * h)
        if r > 0.4:
            li.append((x, y, w, h))
            ct += 1
    li.sort(key=lambda x: -x[2] - x[3])
    i = 0
    while i < len(li):
        x1, y1, w1, h1 = li[i]
        flg = False
        for j in range(len(li)):
            x, y, w, h = li[j]
            if i == j:
                continue
            if x1 >= x and y1 >= y and x1 + w1 <= x + w:
                li.remove(li[i])
                flg = True
                break
        if not flg:
            i += 1
    #    print(len(li))
    #    for ele in li:
    #        x,y,w,h = ele
    #        cv2.rectangle(sbi, (x,y),(x+w, y+h), (0,0,255), 1)
    #    cv2.imshow("i3", sbi)         #Uncomment to see each img strip and b-box
    #    cv2.imshow("i4", sub_image1)
    #    cv2.waitKey()
    #    print(ct,end = '  ')
    # print(len(li))
    return len(li)


def table_detect(rgb):

    small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 9), np.uint8)
    grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)
    _, bw = cv2.threshold(grad, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy = cv2.findContours(
        connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    mask = np.zeros(bw.shape, dtype=np.uint8)

    TEXT = list()
    abc = np.copy(rgb)
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y : y + h, x : x + w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y : y + h, x : x + w])) / (w * h)

        if r > 0.4 and w > 2 and h > 2:  # hardcoded
            cv2.rectangle(abc, (x - 2, y - 2), (x + w + 2, y + h + 2), (0, 0, 255), 1)
            TEXT.append((x, y, w, h))
    # cv2.imwrite("/Users/nishith/cv/Lib/site-packages/mod_img.jpg",abc)
    # cv2.imshow('rects', abc)
    # cv2.waitKey(0)
    TEXT.sort(key=lambda x: (x[1], x[0]))
    grps = list()
    i = 0
    while i < len(TEXT) - 1:
        tlist = list()
        tlist.append(TEXT[i])
        while (
            i < len(TEXT) - 1
            and abs(
                (TEXT[i][1] + TEXT[i][3] // 2) - (TEXT[i + 1][1] + TEXT[i + 1][3] // 2)
            )
            <= 10
        ):
            tlist.append(TEXT[i + 1])
            i += 1
        grps.append(tlist)
        if i == len(TEXT) - 2 and TEXT[i] != TEXT[i + 1]:
            tlist = list()
            tlist.append(TEXT[i + 1])
            grps.append(tlist)
        i += 1
    tmp2 = np.copy(rgb)
    new_crd = list()
    for txts in grps:
        xmin = min(txts, key=lambda x: x[0])[0]
        ymin = min(txts, key=lambda x: x[1])[1]
        x1, x2, x3, x4 = max(txts, key=lambda x: x[0] + x[2])[:]
        xmax = x1 + x3
        y1, y2, y3, y4 = max(txts, key=lambda x: x[1] + x[3])[:]
        ymax = y2 + y4
        new_crd.append((xmin, ymin, xmax, ymax))
        cv2.rectangle(tmp2, (xmin - 1, ymin - 1), (xmax + 1, ymax + 1), (0, 0, 255), 1)

    #    cv2.imshow("rows", tmp2)
    #    cv2.waitKey()
    return new_crd


def get_text(annotate_dict, tmp_image, w, h):
    tmp3 = tmp_image
    #    tmp4 = np.copy(tmp3)
    #    print(tmp3.shape)
    ind = 0
    result = dict()
    for ind in range(len(annotate_dict) - 1):
        # del annotate_dict["Page" + str(ind + 1)]["Start Of Table"]
        if "Start Of Table" in annotate_dict["Page" + str(ind + 1)]:
            del annotate_dict["Page" + str(ind + 1)]["Start Of Table"]
        coord = list(annotate_dict["Page" + str(ind + 1)].values())
        labels = list(annotate_dict["Page" + str(ind + 1)].keys())
        for crds, label in zip(coord, labels):
            x, y, x1, y1 = crds
            sb_img = tmp3[y - 4 : y1 + 4, x - 4 : x1 + 4]
            #            sb_img = cv2.resize(sb_img,(sb_img.shape[1]*2, sb_img.shape[0]*2),
            #                               interpolation = cv2.INTER_NEAREST)
            sb_img = cv2.bilateralFilter(sb_img, 10, 95, 95)
            # cv2.imshow("TMP_IMG", sb_img)
            # cv2.waitKey()
            # pytesseract.pytesseract.tesseract_cmd = "E:\\Downloads\\Tesseract OCR\\tesseract.exe"
            d = pytesseract.image_to_data(
                sb_img, output_type=Output.DICT, lang="eng_layer", config="--psm 6"
            )
            #            cv2.rectangle(tmp4, (x-2, y-2), (x1+2, y1+2), (0, 0, 255), 1)
            text = ""
            for t in d["text"]:
                text += t + " "
            #                print(t, end='  ')
            result.update({label: clean_text(text)})
    #            print()

    #    cv2.imshow("Img", tmp4)
    #    cv2.waitKey()
    #    cv2.imwrite('output.png', tmp4)
    return result


def get_annotations_xlsx(path):
    df = pd.read_csv(path, header=None)
    annotate_dict = {}
    number_of_rows = df.shape[0]
    for r in range(0, number_of_rows - 1):
        row1 = df.iloc[r, :]
        curr_row = row1.tolist()
        # print(curr_row)
        annotate_dict["page " + str(r + 1)] = dict()
        for i in range(1, len(curr_row)):
            res = ast.literal_eval(curr_row[i])
            label = res["label"]
            x1 = int(res["left"])
            x2 = x1 + int(res["width"])
            y1 = int(res["top"])
            y2 = y1 + int(res["height"])
            annotate_dict["page " + str(r + 1)][label] = (x1, y1, x2, y2)
    annotate_dict["ncols"] = df.iloc[number_of_rows - 1, 1]
    return annotate_dict


def find_table(tmp3, res, new_lst):
    tab_result = list()
    for crds in new_lst:
        x, y, x1, y1 = crds
        sub_image = tmp3[y - 1 : y1 + 1, x - 1 : x1 + 1]
        resultant = res[y - 1 : y1 + 1, x - 1 : x1 + 1]
        #        cv2.imshow("Each Row", sub_image)
        #        cv2.waitKey()
        tmp_image = cv2.cvtColor(sub_image, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(tmp_image, 0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel = np.ones((3, 5), np.uint8)
        th = cv2.erode(th, kernel, iterations=5)
        th = cv2.dilate(th, kernel, iterations=5)
        th = np.pad(
            th,
            ((10, 10), (10, 10)),
            mode="constant",
            constant_values=((255, 255), (255, 255)),
        )
        th = 255 - th
        contours, hierarchy = cv2.findContours(
            th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        sbi = np.pad(
            resultant,
            ((10, 10), (10, 10), (0, 0)),
            mode="constant",
            constant_values=((255, 255), (255, 255), (0, 0)),
        )
        mask = np.zeros(th.shape, dtype=np.uint8)
        li = list()
        for idx in range(len(contours)):
            xe, ye, we, he = cv2.boundingRect(contours[idx])
            mask[ye : ye + he, xe : xe + we] = 0
            cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
            r = float(cv2.countNonZero(mask[ye : ye + he, xe : xe + we])) / (we * he)
            if r > 0.4:
                li.append((xe, ye, we, he))
        li.sort(key=lambda x: -x[2] - x[3])
        i = 0
        while i < len(li):
            x1, y1, w1, h1 = li[i]
            flg = False
            for j in range(len(li)):
                x, y, w, h = li[j]
                if i == j:
                    continue
                if x1 >= x and y1 >= y and x1 + w1 <= x + w:
                    li.remove(li[i])
                    flg = True
                    break
            if not flg:
                i += 1
        li.sort(key=lambda x: x[0])
        row = list()
        contouredImage = tmp3.copy()
        for ele in li:
            x, y, w, h = ele
            col = sbi[y - 2 : y + h + 2, x - 2 : x + w + 2]
            col = cv2.resize(
                col,
                (col.shape[1] * 2, col.shape[0] * 2),
                interpolation=cv2.INTER_NEAREST,
            )
            # cv2.imshow("Each Col", col)
            # cv2.waitKey()
            d = pytesseract.image_to_data(
                col, output_type=Output.DICT, lang="eng_layer", config="--psm 6"
            )
            # cv2.rectangle(
            #     contouredImage, (x, y), (x + w + 1, y + h + 1), (0, 0, 255), 1
            # )
            text = ""
            for t in d["text"]:
                text += t + " "
                print(t, end="  ")
            row.append(clean_text(text))
            print()
        tab_result.append(row)
    # cv2.imshow("Table Output", tmp3)
    # cv2.waitKey()
    # cv2.imwrite("output.png", contouredImage)
    return tab_result


def find_below_table(tmp_img, x):
    below_tab_result = list()
    for c in x:
        x, y, x1, y1 = c
        # cv2.rectangle(tmp_img, (x-1, y-1), (x1+1, y1+1), (0, 0, 255), 1)
        tmp = tmp_img[y - 2 : y1 + 2, x - 2 : x1 + 2]
        tmp = cv2.resize(
            tmp, (tmp.shape[1] * 2, tmp.shape[0] * 2), interpolation=cv2.INTER_NEAREST
        )
        #        cv2.imshow("below", tmp)
        #        cv2.waitKey()
        d = pytesseract.image_to_data(
            tmp, output_type=Output.DICT, lang="eng_layer", config="--psm 6"
        )
        text = ""
        for t in d["text"]:
            text += t + " "
        #            print(t, end='  ')
        #        print()
        below_tab_result.append(clean_text(text))
    return below_tab_result


def clean_text(text):
    bad_chars = [";", "{", "}", "[", "]", "(", ")", '"', "°", "‘", "|"]
    text = "".join((filter(lambda i: i not in bad_chars, text)))
    return str(text).strip()
