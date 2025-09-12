from django.contrib.auth.mixins import LoginRequiredMixin , UserPassesTestMixin
from django.shortcuts import redirect


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, "فقط ادمین‌ها اجازه دسترسی دارند!")
        return redirect("home") 



class CustomLoginRequiredMixin(LoginRequiredMixin):
    login_url = "pages:login"
    redirect_field_name = None


class AnonymousRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return redirect("home")

        return super().dispatch(request, *args, **kwargs)


