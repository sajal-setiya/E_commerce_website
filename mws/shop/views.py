from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm




def index(request):

    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1,nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "No result found for this search"}
    return render(request, 'shop/search.html', params)

def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.subcategory.lower() \
            or query in item.category.lower():
        return True
    else:
        return False



def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})



def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        #return HttpResponse(f"{orderId} and {email}")
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates":updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)

            else:
                return HttpResponse('{"status":"No items"}')
        except Exception as e:
            return HttpResponse('{"status":"Error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    #fetch the product using myid
    product = Product.objects.filter(id=myid)
    print(product)

    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone1', '') + " / " + request.POST.get('phone2', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')
        order = Orders(items_json=items_json, name=name, email=email, phone=phone, address=address, city=city, zip_code=zip_code, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        id = order.order_id
        request.session['order_id'] = id
        return redirect('process_payment')

    return render(request, 'shop/checkout.html')


def process_payment(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Orders, order_id=order_id)


    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': format(order.amount),
        'item_name': "Order ID = " + format(order.order_id) + " & Items : " + format(order.items_json),
        'invoice': str(order.order_id),
        'currency_code': 'INR',
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'shop/process_payment.html', {'order': order, 'form': form})


@csrf_exempt
def payment_done(request):
    return render(request, 'shop/payment_done.html')