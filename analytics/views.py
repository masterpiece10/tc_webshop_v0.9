from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.utils import timezone

from .utilis import get_last_month_data, get_month_data_range
from orders.models import Order



# Create your views here.

class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_week_range(weeks_ago=5, number_of_weeks=5)
            if request.GET.get('type') == 'week':
                days = 7
                start_date = timezone.now().today() - timedelta(days=days-1)
                # datetime_list = [start_date + timedelta(days=x) for x in range(0, days)]
                datetime_list = []
                labels = []
                sales_items = []
                for x in range(0, days):
                    new_time = start_date + timedelta(days=x)
                    datetime_list.append(
                        new_time
                    )
                    labels.append( 
                        new_time.strftime("%a")
                    )
                    new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
                    new_total = new_qs.totals_data()['total__sum'] or 0
                    
                    sales_items.append(
                         new_total                        
                    )
                data['labels'] = labels
                data['data'] = sales_items
            if request.GET.get('type') == '4weeks':
                current = 5
                week_sales = []
                for i in range(0, 5):
                    new_qs = qs.by_week_range(weeks_ago=current, number_of_weeks=1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    
                    week_sales.append(sales_total)
                    current -= 1

                data['data'] = week_sales
                data['labels'] = ['Four Weeks Ago','Three Weeks Ago','Two Weeks Ago','Last Week','This Week']
                
        return JsonResponse(data)


class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(SalesView, self).dispatch(request, *args, **kwargs)
    

    def get_context_data(self, *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        #
        # date range for qs
        #
        
        qs = Order.objects.all() #.by_week_range(weeks_ago=10, number_of_weeks=10 )
        #
        #
        #
        context["today"] = qs.by_range(start_date=timezone.now().date()).get_breakdown_data()
        context["this_week"] = qs.by_week_range(weeks_ago=1, number_of_weeks=1).get_breakdown_data()
        context["last_four_weeks"] = qs.by_week_range(weeks_ago=5, number_of_weeks=5).get_breakdown_data()
        print(context["last_four_weeks"])
        return context
    