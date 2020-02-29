from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from .forms import RegisterForm, LoginForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import GuestEmail, EmailActivation
from .signals import user_logged_in
from billing.models import BillingProfile
from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin

# Create your views here.
  

class AccountHomeVIew(LoginRequiredMixin, DetailView):
    template_name = "accounts/home.html"
    def get_object(self):
        return self.request.user

class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    template = 'registration/activation-error.html'
    key = None
    def get(self, request, key=None, *args, **kwargs):
        self.key= key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs= qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, "Your eMail already has been confirmed. Now you can login.")
                return redirect('login')
            else:
                activated_qs = qs.filter(activated = True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = f"""Your eMail has already been confirmed.
                    Do you need to <a href={reset_link}>reset your password?</a>              
                    """
                    messages.success(request, mark_safe(msg))
                    return redirect('login')
            template = 'registration/activation-error.html'
            context = {'form': self.get_form(),
                        'key': key,}
            return render(request, template, context )
        template = 'registration/activation-error.html'
        context = {'form': self.get_form(),
                        'key': key,}
        return render(request, template, context)

    def post(self, request, *args, **kwargs):
        # create form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = f"""Activation link sent, please check your email.              
                """
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get('email')
        obj = EmailActivation.objects.email_exists(email).first()
        print(email)
        print(obj)
        user = obj.user 
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()
        return super(AccountEmailActivateView, self).form_valid(form)
    
    def form_invalid(self, form):
        request = self.request
        context = {
                'form': form,
                'key': self.key,}
        template = 'registration/activation-error.html'
        return render(request, template, context )

class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = "account/register/"

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self):
        return redirect("account/register/")


class LoginView(RequestFormAttachMixin, NextUrlMixin, FormView):
    form_class = LoginForm
    success_url = "/"
    template_name = "accounts/login.html"
    default_next = "/"

    def form_valid(self, form):   
        next_path = self.get_next_url()
        return redirect(next_path)
       
# def login_page(request):
#     form = LoginForm(request.POST or None)
#     template = "accounts/login.html"
#     context = {
#         'title': "Login Page",
#         'content': "Please input your credentials",
#         'form': form,
#     }
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         username = form.cleaned_data.get("username")
#         password = form.cleaned_data.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             try:
#                 del request.session.get['guest_email_id']
#             except:
#                 print('could not delete guest_email_id from session')
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect("/")
#         else:
#             return redirect("/")

#     return render(request, template, context)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = "/"

class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-form.html'
    

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Change Your Account Details'
        return context
    
    def get_success_url(self):
        return reverse('accounts:home') 

def logout_page(request):
    pass

