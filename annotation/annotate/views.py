from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from annotation.settings import BASE_DIR,MEDIA_ROOT
from pdf2image import convert_from_path
import os

# Create your views here.
def annotate(request):
    if request.method == 'GET':
        return render(request, 'annotate/index.html',{})
    else:
        data = request.POST
        startX = data.getlist('startX')
        startY = data.getlist('startY')
        w = data.getlist('w')
        h = data.getlist('h')
        label = data.getlist('label')
        return HttpResponse("OK")

def upload_pdf(request):    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        file1 = request.FILES['file_name']
        x = file1.read()
        f = open(BASE_DIR + '/media/current.pdf', 'wb')
        f.write(x)
        f.close()
        pages = convert_from_path(
            BASE_DIR+'/media/current.pdf', fmt="jpeg", size=(900,1200))
        picture_path = MEDIA_ROOT
        del_image_counter = 1
        while True:
            if os.path.exists(os.path.join(picture_path, "page-"+str(del_image_counter)+".jpeg")):
                os.remove(os.path.join(picture_path, "page-" +str(del_image_counter)+".jpeg"))
                del_image_counter+=1
            else:
                break
        image_counter = 1
        for page in pages:
            # Save the image of the page in system
            filename = "page-"+str(image_counter)+".jpeg"
            page.save(picture_path+filename, 'JPEG')
            # os.remove(filename)                              #comment if u want to operate on extracted images
            image_counter = image_counter + 1
        return redirect('http://127.0.0.1:8000/annotate/')
    else:
        return render(request,"annotate/upload_pdf.html",{})
