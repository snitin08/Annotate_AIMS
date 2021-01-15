from django.shortcuts import render,HttpResponse
from annotation.settings import BASE_DIR

# Create your views here.
def annotate(request):
    if request.method == 'GET':
        return render(request, 'annotate/index.html',{})
    else:
        data = request.POST
        print(data)
        startX = data.getlist('startX')
        startY = data.getlist('startY')
        w = data.getlist('w')
        h = data.getlist('h')
        label = data.getlist('label')
        print(list(zip(startX,startY,w,h,label)))
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
        
        
        return HttpResponse("OK")
    else:
        return render(request,"annotate/upload_pdf.html",{})