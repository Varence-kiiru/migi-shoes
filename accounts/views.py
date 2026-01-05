from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import signupform , loginform
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.conf import settings

# Create your views here.
###      login 
def log_in(request):

    next_param = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == "POST":
        form = loginform(request,data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request,user)
                messages.success(request,'You have successfully logged in.')
                # Validate next; fallback to LOGIN_REDIRECT_URL
                if next_param:
                    return redirect(next_param)
                return redirect(settings.LOGIN_REDIRECT_URL or 'storefront:home')
            else:
                messages.error(request,'Error. User does not exist.')

            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
        else:
            messages.success(request,"There was an error logging in.") 
    else:
        form = loginform()

    return render(request,"accounts/login.html", {"loginform" : form, "next": next_param})
    

###           logout
def logOut(request):
    logout(request)
    messages.success(request,"You have successfully logged out.")
    return redirect('storefront:home')


#######   sign up
def signup(request):
    if request.method == 'POST':
        form = signupform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has successfully been created.')
            return redirect('accounts:login')  # or your dashboard
    else:
        form = signupform()

    return render(request,"accounts/signup.html", {'form' : form})



############# FORGOT PASSWORD ##########################


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/registration/password_reset_form.html"
    email_template_name = "accounts/registration/password_reset_email.html"
    subject_template_name = "accounts/registration/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "domain": "localhost:8000",  # change in prod (e.g., myapp.com)
            "protocol": "http",          # use "https" in production
        })
        return ctx


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/registration/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/registration/password_reset_complete.html"


# For backward compatibility
forgot_password_view = CustomPasswordResetView
