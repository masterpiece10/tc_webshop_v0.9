import random

from.models import Ads

from products.models import Product


class ADSMiddleware(object):
    #
    # initial setup when the server is startet
    #


    def __init__(self, get_response): 
        self.get_response = get_response
        
        

    #
    # will be called each time a new page is requested
    #

    def __call__(self, request):
        response = self.get_response(request)
        return response

    #
    # here will be the context added which will be generated in __call__
    #
    

    def process_template_response(self, _request, response):
        try:
            if _request.session['cart'] is False:
                current_page = _request.META.get('HTTP_REFERER')
                print("IP:", _request.META.get('REMOTE_ADDR'))
                
                if current_page is None or "admin" not in current_page:
                    prod_obj = Product.objects.featured()
                    count = prod_obj.count()
                    ads_obj = prod_obj[random.randint(0, count-1)] 
                    ads_obj_db , created = Ads.objects.get_or_create(product = ads_obj)
                    ads_obj_db.views += 1
                    try:
                        ads_obj_db.user.add(_request.user.id)
                    except:
                        pass
                    ads_obj_db.save()

                else:
                    ads_obj = {}
                response.context_data['ads_obj'] = ads_obj
                self.c =0
        except:
            pass
        return response