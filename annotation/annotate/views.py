from django.shortcuts import render,HttpResponse

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

