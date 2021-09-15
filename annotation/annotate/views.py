from tableDetect import table_border_detect
from tableDetect.table_detect_all import recognize_structure
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
    tab_result = list()
    # print(len(images))
    if len(images) > 0:
        result = get_text(annotate_dict, np.copy(images[0]), 900, 1200)

        for image in images:
            image.save(str(BASE_DIR) + "\\media\\page_1.jpeg", "JPEG")
            document_image = cv2.imread(str(BASE_DIR) + "\\media\\page_1.jpeg")
            result = get_text(annotate_dict, document_image, 900, 1200)
            recognize_structure(document_image)
            table_border_detect.detect_border(document_image)

        # Get all files in the directory paths as a list
        tables_path = []
        for file in os.listdir(os.path.join(BASE_DIR, "media", "tables")):
            tables_path.append(os.path.join("tables", file))

        table_border_detect.extract_text_ocr()
    return result, tables_path, None