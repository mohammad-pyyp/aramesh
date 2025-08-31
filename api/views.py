from django.shortcuts import render

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
