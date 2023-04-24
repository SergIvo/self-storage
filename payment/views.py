import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from storage.models import Warehouse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db.models import Count, F, Min

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request, pk):
    YOUR_DOMAIN = 'http://127.0.0.1:8000'
    warehouse = Warehouse.objects.prefetch_related('storages').annotate(
        free_storages=F('total_storages') - Count('storages_in_use'),
        min_price=Min('storages__price')
    ).get(id=pk)
    # warehouse = warehouses.objects.get(id=pk)
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'rub',
                    'unit_amount_decimal': (warehouse.min_price * 100),
                    'product_data': {
                        'name': f'Номер заказа {warehouse.id}'
                    }
                },
                'quantity': 1,
            },
        ],
        metadata={
          'product_id': warehouse.id
        },
        mode='payment',
        success_url=YOUR_DOMAIN + '/payment/success',
        cancel_url=YOUR_DOMAIN + '/payment/cancel',
    )

    return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_KEY
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )

        customer_email = session['customer_details']['email']
        order_id = session['metadata']['product_id']

        # order = Order.objects.get(id=order_id)
        # order.paid = True
        # order.save()

        send_mail(
            subject='Ваш заказ оплачен',
            message=f'Спасибо! Ваш заказ {order_id} оплачен!',
            recipient_list=[customer_email],
            from_email='test@test.com',
        )

    return HttpResponse(status=200)


def success_payment(request):
    return render(request, 'payment/success.html')


def cansel_payment(request):
    return render(request, 'payment/cansel.html')
