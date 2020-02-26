from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import CreateView, FormView

from .forms import RegisterForm, LoginForm, GuestForm
from .models import GuestEmail
from .signals import user_logged_in
from billing.models import BillingProfile

# Create your views here.
def guest_register_page(request):
    guest_form = GuestForm(request.POST or None)
    template = "accounts/login.html"
    context = {
        'title': "Login Page",
        'content': "Please input your credentials",
        'guest_form': guest_form,
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if guest_form.is_valid():
        email = guest_form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("register/")
    else:
        print("error with the form")
            
    return redirect("register")

class LoginView(FormView):
    form_class = LoginForm
    success_url = "/"
    template_name = "accounts/login.html"

    def form_valid(self, form):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            user_logged_in.send(user.__class__, instance = user, request = request)
            try:
                del request.session.get['guest_email_id']
            except:
                print('could not delete guest_email_id from session')
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
       
        return super(LoginView, self).form_invalid(form)

def login_page(request):
    form = LoginForm(request.POST or None)
    template = "accounts/login.html"
    context = {
        'title': "Login Page",
        'content': "Please input your credentials",
        'form': form,
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session.get['guest_email_id']
            except:
                print('could not delete guest_email_id from session')
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        else:
            return redirect("/")

    return render(request, template, context)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = "/"

def logout_page(request):
    pass

