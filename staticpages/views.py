from django.shortcuts import render


def about_us(request):
    return render(request, 'staticpages/about_us.html')

def contact_us(request):
    return render(request, 'staticpages/contact_us.html')
# Create your views here.


# def contact_us(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
#         # Process the data or send an email
#         return HttpResponse("Thank you for contacting us!")
#     return render(request, 'staticpages/contact_us.html')