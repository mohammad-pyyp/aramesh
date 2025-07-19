from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView 
from .models import Reserve
import json


def abjad_value(text):
    abjad_dict = {
        'ا': 1, 'ب': 2, 'ج': 3, 'د': 4,
        'ه': 5, 'و': 6, 'ز': 7, 'ح': 8,
        'ط': 9, 'ی': 10, 'ك': 20, 'ک': 20,
        'ل': 30, 'م': 40, 'ن': 50, 'س': 60,
        'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100,
        'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500,
        'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900,
        'غ': 1000
    }

    total = 0
    for char in text:
        if char in abjad_dict:
            total += abjad_dict[char]
    return total

@csrf_exempt
def submit_reserve_form(request):
    if request.method == 'POST':
        # Depending on content-type, parse body accordingly:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        phone_number = data.get('phoneNumber')
        
        if first_name and last_name and phone_number :
            obj = Reserve.objects.create(
                                         first_name=first_name ,
                                         last_name=last_name ,
                                         phone_number=phone_number,
                                        )
            obj.save()
            
            return JsonResponse({
                'message': "Ok I'm Mohammad Wlcome to my site!" ,
                'status': "ok" ,
                'abjad': abjad_value(first_name) ,
            })

    return JsonResponse({'error': 'فرم نا معتبر'}, status=400)










class ReserveTemplateView(TemplateView):
    template_name = "main/reserve.html"


class CommingSoonTemplateView(TemplateView):
    template_name = "comming_soon.html"

