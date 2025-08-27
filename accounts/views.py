from django.shortcuts import  redirect
# import random
# from .models import VerificationCode
# from .forms import RegisterForm, UsernameLoginForm, EmailLoginForm, ForgetPasswordForm, VerifyCodeForm, ResetPasswordForm, EditProfileForm, ChangePasswordForm
# from django.utils import timezone
# from datetime import timedelta
# from django.core.mail import send_mail
# from django.contrib import messages
# from django.conf import settings
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from django.urls import reverse

@csrf_exempt
def submit_sign_in_form(request):
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
            obj = User.objects.create_user(
                                         first_name=first_name ,
                                         last_name=last_name ,
                                         phone_number=phone_number,
                                        )
            obj.save()
            print(request.build_absolute_uri(reverse("main:user_dashboard")))
            return JsonResponse({
                'msg': "Ok I'm Mohammad Wlcome to my site!" ,
                'status': "ok" ,
                "redirect_url": request.build_absolute_uri(reverse("main:user_dashboard")) ,
                
            })

    return JsonResponse({'error': 'فرم نا معتبر'}, status=400)

class SingIn(TemplateView):
    template_name = "accounts/sing_in.html"


























# def generate_verification_code():
#     return ''.join(random.choices('0123456789', k=5))


# def register(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.is_active = False
#             user.save()
#             code = generate_verification_code()
#             VerificationCode.objects.create(
#                 user=user,
#                 code=code,
#                 code_expiry=timezone.now() + timedelta(minutes=2)
#             )
#             # send_mail(
#             #     'کد تایید ثبت ‌نام',
#             #     f'خوش آمدید! ثبت‌ نام شما با موفقیت انجام شد.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
#             #     settings.EMAIL_HOST_USER,
#             #     [user.email],
#             #     fail_silently=False,
#             # )
#             request.session['verification_type'] = 'register'
#             messages.success(request, 'ثبت ‌نام انجام شد. کد تایید به ایمیل شما ارسال شد.')
#             return redirect('accounts:verify_code')
#     else:
#         form = RegisterForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/register.html', context)


# def username_login(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if request.method == 'POST':
#         form = UsernameLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('accounts:dashboard')
#             messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
#     else:
#         form = UsernameLoginForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/username_login.html', context)


# def email_login(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if request.method == 'POST':
#         form = EmailLoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             try:
#                 user = User.objects.get(email=email)
#                 code = generate_verification_code()
#                 VerificationCode.objects.create(
#                     user=user,
#                     code=code,
#                     code_expiry=timezone.now() + timedelta(minutes=2)
#                 )
#                 # send_mail(
#                 #     'کد تایید ورود',
#                 #     f'خوش آمدید! برای ورود به حساب کاربری خود از کد زیر استفاده کنید.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
#                 #     settings.EMAIL_HOST_USER,
#                 #     [email],
#                 #     fail_silently=False,
#                 # )
#                 request.session['verification_type'] = 'login'
#                 request.session['verified_user_id'] = user.id
#                 messages.success(request, 'کد تایید به ایمیل شما ارسال شد.')
#                 return redirect('accounts:verify_code')
#             except User.DoesNotExist:
#                 messages.error(request, 'ایمیل وارد شده وجود ندارد.')
#     else:
#         form = EmailLoginForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/email_login.html', context)


# def forget_password(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if request.method == 'POST':
#         form = ForgetPasswordForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             try:
#                 user = User.objects.get(email=email)
#                 code = generate_verification_code()
#                 VerificationCode.objects.create(
#                     user=user,
#                     code=code,
#                     code_expiry=timezone.now() + timedelta(minutes=2)
#                 )
#                 # send_mail(
#                 #     'کد تایید بازیابی رمز عبور',
#                 #     f'خوش آمدید! برای بازیابی رمز عبور خود از کد زیر استفاده کنید.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
#                 #     settings.EMAIL_HOST_USER,
#                 #     [email],
#                 #     fail_silently=False,
#                 # )
#                 request.session['verification_type'] = 'reset_password'
#                 messages.success(request, 'کد تایید به ایمیل شما ارسال شد.')
#                 return redirect('accounts:verify_code')
#             except User.DoesNotExist:
#                 messages.error(request, 'ایمیل وارد شده وجود ندارد.')
#     else:
#         form = ForgetPasswordForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/forget_password.html', context)


# def verify_code(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     VerificationCode.clean_expired_codes()

#     if request.method == 'POST':
#         form = VerifyCodeForm(request.POST)
#         if form.is_valid():
#             code = form.cleaned_data['code']
#             try:
#                 verification = VerificationCode.objects.get(code=code, is_used=False)
#                 if verification.is_valid(code):
#                     verification.is_used = True
#                     verification.save()
#                     verification.delete()

#                     verification_type = request.session.get('verification_type')
#                     user = verification.user

#                     if verification_type == 'register':
#                         user.is_active = True
#                         user.save()
#                         login(request, user)
#                         messages.success(request, 'تایید موفقیت‌ آمیز بود. وارد شدید.')
#                         return redirect('accounts:dashboard')
#                     elif verification_type == 'login':
#                         user.is_active = True
#                         user.save()
#                         login(request, user)
#                         messages.success(request, 'تایید موفقیت ‌آمیز بود. وارد شدید.')
#                         return redirect('accounts:dashboard')
#                     elif verification_type == 'reset_password':
#                         request.session['verified_user_id'] = user.id
#                         return redirect('accounts:reset_password')
#                 else:
#                     messages.error(request, 'کد تایید نامعتبر یا منقضی شده است.')
#             except VerificationCode.DoesNotExist:
#                 messages.error(request, 'کد تایید نامعتبر است.')
#     else:
#         form = VerifyCodeForm()

#     try:
#         latest_code = VerificationCode.objects.filter(is_used=False).latest('code_expiry')
#         remaining_seconds = int((latest_code.code_expiry - timezone.now()).total_seconds())
#     except VerificationCode.DoesNotExist:
#         remaining_seconds = 120

#     context = {
#         'form': form,
#         'remaining_seconds': remaining_seconds
#     }
#     return render(request, 'accounts/verify_code.html', context)


# def reset_password(request):
#     if request.user.is_authenticated:
#         return redirect('core:home')

#     if 'verified_user_id' not in request.session:
#         return redirect('accounts:forget_password')
#     user = User.objects.get(id=request.session['verified_user_id'])
#     if request.method == 'POST':
#         form = ResetPasswordForm(request.POST)
#         if form.is_valid():
#             user.set_password(form.cleaned_data['new_password'])
#             user.save()
#             del request.session['verified_user_id']
#             messages.success(request, 'رمز عبور با موفقیت تغییر کرد. لطفاً وارد شوید.')
#             return redirect('accounts:username_login')
#     else:
#         form = ResetPasswordForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/reset_password.html', context)


# @require_POST
# def resend_code(request):
#     try:
#         latest_code = VerificationCode.objects.filter(is_used=False).latest('code')
#         user = latest_code.user

#         VerificationCode.objects.filter(user=user, is_used=False).delete()

#         code = generate_verification_code()
#         VerificationCode.objects.create(
#             user=user,
#             code=code,
#             code_expiry=timezone.now() + timedelta(minutes=2)
#         )
#         # send_mail(
#         #     'کد تایید جدید',
#         #     f'خوش آمدید! کد تایید جدیدی برای شما ایجاد شده است.\n\nکد تایید شما: {code}\nلطفاً این کد را در صفحه تایید وارد کنید.',
#         #     settings.EMAIL_HOST_USER,
#         #     [user.email],
#         #     fail_silently=False
#         # )
#         return JsonResponse({'success': True})
#     except VerificationCode.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'No active verification code found.'})


# def user_logout(request):
#     logout(request)
#     return redirect('core:home')


# @login_required
# def dashboard(request):
#     return render(request, 'accounts/dashboard.html', {'user': request.user})


# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()

#             if 'image-clear' in request.POST:
#                 profile = request.user.profile
#                 profile.image.delete()
#                 profile.image = None
#                 profile.save()

#             return redirect('accounts:dashboard')
#     else:
#         form = EditProfileForm(instance=request.user)

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/edit_profile.html', context)


# @login_required
# def change_password(request):
#     if request.method == 'POST':
#         form = ChangePasswordForm(request.POST)
#         if form.is_valid():
#             user = request.user
#             if user.check_password(form.cleaned_data['current_password']):
#                 user.set_password(form.cleaned_data['new_password'])
#                 user.save()
#                 logout(request)
#                 messages.success(request, 'رمز عبور تغییر کرد. لطفاً دوباره وارد شوید.')
#                 return redirect('accounts:username_login')
#             messages.error(request, 'رمز عبور فعلی اشتباه است.')
#     else:
#         form = ChangePasswordForm()

#     context = {
#         'form': form
#     }
#     return render(request, 'accounts/change_password.html', context)
