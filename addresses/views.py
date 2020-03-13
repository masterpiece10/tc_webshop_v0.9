from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import UpdateView, View, ListView, CreateView

from .forms import AddressForm, AddressChangeForm
from .models import Address
from billing.models import BillingProfile
# Create your views here.

def checkout_address_create_view(request):
    request.session['cart'] = False
    form = AddressForm(request.POST or None)
    context = {
        'form': form,
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()

            request.session[address_type + "_address_id"] = instance.id
        else:
            messages.error(request, "No billing profile found. Please contact support for help.")
            return redirect("carts:checkout")

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)

    return redirect("carts:checkout")


def checkout_address_reuse_view(request):
    request.session['cart'] = False
    if request.user.is_authenticated:
            
        context = {}
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if request.method == "POST":
            shipping_address = request.POST.get('shipping_address', None)
            address_type = request.POST.get('address_type', 'shipping')
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            
            if shipping_address is not None:
                qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
                if qs.exists():
                    request.session[address_type + "_address_id"] = shipping_address

                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)

    return redirect("carts:checkout")


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'addresses/address-update.html'
    form_class = AddressChangeForm
    success_url = '/addresses'
    
    def get_queryset(self):
        self.request.session['cart'] = False
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)

    
class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'addresses/home.html'

    def get_queryset(self):
        self.request.session['cart'] = False
        request = self.request
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return Address.objects.filter(billing_profile=billing_profile)

class AddressCreateView(LoginRequiredMixin, CreateView):
    template_name = "addresses/address-update.html"
    form_class = AddressForm
    success_url = "/addresses"

    def form_valid(self, form):
        self.request.session['cart'] = False
        request = self.request
        billing_profile, billing_profile_created = BillingProfile.objects. new_or_get(request)
        instance = form.save(commit=False)
        instance.billing_profile = billing_profile
        instance.save()
        return super(AddressCreateView, self).form_valid(form)
