from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from annotation.settings import BASE_DIR, MEDIA_ROOT
from pdf2image import convert_from_path
from .table_detect import *
import os
import sys
import json
import subprocess
import traceback
import math

IMG_DISPLAY_WIDTH = 900
IMG_DISPLAY_HEIGHT = 1200

# Create your views here.


def annotate(request):
    if request.method == "GET":
        return render(request, "annotate/index.html", {})
    else:
        data = request.POST
        startX = data.getlist("startX")
        startY = data.getlist("startY")
        w = data.getlist("w")
        h = data.getlist("h")
        label = data.getlist("label")
        return HttpResponse("OK")


def upload_pdf(request):
    if request.method == "POST":
        data = request.POST
        files = request.FILES
        file1 = files.getlist("file_name")[0]
        f = open(BASE_DIR + "/media/current.pdf", "wb")
        x = file1.read()
        f.write(x)
        f.close()
        if len(files.getlist("file_name")) == 2:
            file2 = files.getlist("file_name")[1]
            x = file2.read()
            f = open(BASE_DIR + "/media/currentcoors.json", "wb")
            f.write(x)
            f.close()
        else:
            if os.path.exists(BASE_DIR + "/media/currentcoors.json"):
                os.remove(BASE_DIR + "/media/currentcoors.json")
        pages = convert_from_path(BASE_DIR + "/media/current.pdf", dpi=300)
        picture_path = MEDIA_ROOT
        del_image_counter = 1
        while True:
            if os.path.exists(
                os.path.join(picture_path, "page-" + str(del_image_counter) + ".jpeg")
            ):
                os.remove(
                    os.path.join(
                        picture_path, "page-" + str(del_image_counter) + ".jpeg"
                    )
                )
                del_image_counter += 1
            else:
                break
        image_counter = 1
        for page in pages:
            # Save the image of the page in system
            filename = "page-" + str(image_counter) + ".jpeg"
            page.save(picture_path + filename, "JPEG")
            # os.remove(filename)                              #comment if u want to operate on extracted images
            image_counter = image_counter + 1
        return redirect("annotate:annotate")
    else:
        return render(request, "annotate/upload_pdf.html", {})


def process_receipt(request):
    if request.method == "GET":
        return render(request, "annotate/upload_files.html", {})
    elif request.method == "POST":
        data = request.POST.dict()
        del data["csrfmiddlewaretoken"]
        # print(request.FILES)
        file1 = request.FILES["file1"]
        file2 = request.FILES["file2"]
        x = file1.read()
        f = open(BASE_DIR + "/media/current.pdf", "wb")
        f.write(x)
        f.close()
        # convert coordinates to scaled coordinates here and extract
        y = file2.read()
        g = open(BASE_DIR + "/media/template.json", "wb")
        g.write(y)
        g.close()
        with open(BASE_DIR + "/media/template.json") as json_file:
            data = json.load(json_file)
        for page in data:
            if page == "ncols":
                break
            pagedata = data[page]
            pageNumber = int(page[-1]) - 1
            IMG_ACTUAL_HEIGHT = pagedata[-1]["IMAGE_ACTUAL_HEIGHT"]
            IMG_ACTUAL_WIDTH = pagedata[-1]["IMAGE_ACTUAL_WIDTH"]
            for ele in pagedata[:-1:]:
                if ele["label"] != "Start Of Table" and ele["label"] != "End Of Table":
                    ele["width"] = math.floor(
                        (ele["width"] * IMG_ACTUAL_WIDTH) / IMG_DISPLAY_WIDTH
                    )
                    ele["height"] = math.floor(
                        (ele["height"] * IMG_ACTUAL_HEIGHT) / IMG_DISPLAY_HEIGHT
                    )
                    ele["left"] = math.floor(
                        (ele["left"] * IMG_ACTUAL_WIDTH) / IMG_DISPLAY_WIDTH
                    )
                    ele["top"] = math.floor(
                        (ele["top"] * IMG_ACTUAL_HEIGHT) / IMG_DISPLAY_HEIGHT
                    )
            # after coordinates scaled for that page delete the image size references
            del pagedata[-1]
        json_object = json.dumps(data)
        with open(BASE_DIR + "/media/template.json", "w") as json_file:
            json_file.write(json_object)
        try:
            annotation, table, below_table = process_invoice(
                BASE_DIR + "/media/current.pdf", BASE_DIR + "/media/template.json"
            )
            if annotation is None and table is None and below_table is None:
                return HttpResponse(
                    "<h1>Error occured, Please upload new template</h1>"
                )
        except Exception as e:
            print(e)
            print(traceback.print_exception(*sys.exc_info()))
            return HttpResponse("<h1>Error occured, Please upload new template</h1>")
        if annotation is None:
            annotation = []
        if table is None:
            table = []
        if below_table is None:
            below_table = []
        print(annotation)
        print(table)
        print(below_table)
        context = {
            "annotation": annotation,
            "table": table,
            "below_table": below_table,
        }
        return render(request, "annotate/processed_invoice.html", context)


def process_invoice(filename, templatename):
    images = convert_from_path(filename, dpi=300)
    annotate_dict = get_annotations_json(templatename)
    print("Images length: ", len(images))
    if len(images) > 0:
        if "Start Of Table" in annotate_dict["Page1"]:
            start_of_table = annotate_dict["Page1"]["Start Of Table"][1]
        else:
            start_of_table = None

        if "End Of Table" in annotate_dict["Page1"]:
            end_of_table = annotate_dict["Page1"]["End Of Table"][3]
        else:
            end_of_table = float('inf')
        #

        extracted_text = []
        below_tab_result = []
        tab_result = []
        for i, image in enumerate(images):
            if "Start Of Table" in annotate_dict["Page" + str(i + 1)]:
                start_of_table = annotate_dict["Page" + str(i + 1)]["Start Of Table"][1]
            else:
                start_of_table = None

            if "End Of Table" in annotate_dict["Page" + str(i + 1)]:
                end_of_table = annotate_dict["Page" + str(i + 1)]["End Of Table"][3]
            else:
                end_of_table = float('inf')

            image.save(str(BASE_DIR) + "\\media\\page_1.jpeg", "JPEG")
            document_image = cv2.imread(str(BASE_DIR) + "\\media\\page_1.jpeg")
            result = get_text(
                annotate_dict["Page" + str(i + 1)], document_image, 900, 1200
            )
            extracted_text.append(result)
            if start_of_table is not None:
                flg = False
                cmd = f'"E:\Downloads\ImageMagic\ImageMagick-6.9.11-Q16-20201228T144714Z-001\ImageMagick-6.9.11-Q16\convert.exe" "{BASE_DIR}/media/page_1.jpeg" -type Grayscale -negate -define morphology:compose=darken -morphology Thinning "Rectangle:1x80+0+0<" -negate "{BASE_DIR}/media/page_1-t.jpeg"'
                # print(cmd)
                subprocess.call(cmd, shell=True)
                new_img = cv2.imread(str(BASE_DIR) + "\\media\\page_1-t.jpeg")
                new_img2 = cv2.imread(str(BASE_DIR) + "\\media\\page_1.jpeg")
                new_img2 = cv2.bilateralFilter(new_img2, 5, 75, 75)
                #        print(annotate_dict)
                #        print(new_img.shape[0],new_img.shape)
                rgb = np.copy(new_img)
                # print("RGB", rgb.shape)
                new_crd = table_detect(rgb)
                NO_OF_COLS = annotate_dict["ncols"]
                new_lst = list()
                below_table = list()
                for x in new_crd:
                    if colfilter(x, rgb, NO_OF_COLS, start_of_table, end_of_table) == int(NO_OF_COLS):
                        new_lst.append(x)
                    elif x[3] > start_of_table:
                        below_table.append(x)
                    else:
                        pass
                tmp3 = np.copy(rgb)
                # if len(new_lst)>=1:
                #     new_lst = new_lst[1:]
                tab_result += find_table(tmp3, new_img2, new_lst)
                if flg == False:
                    below_tab_result += find_below_table(np.copy(new_img2), below_table)
                    flg = True

        return extracted_text, tab_result, below_tab_result
    return None, None, None