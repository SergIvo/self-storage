import stripe
import smtplib
from email.message import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from storage.models import Warehouse, UserStorage
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from .qr_code import make_qr
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='index')
def create_checkout_session(request, pk):
    YOUR_DOMAIN = 'http://127.0.0.1:8000'
    rented_storage = UserStorage.objects.get(id=pk)
    storage_price = rented_storage.storage.storage_type.price
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'rub',
                    'unit_amount_decimal': (storage_price * 100),
                    'product_data': {
                        'name': f'Номер заказа {rented_storage.id}'
                    }
                },
                'quantity': 1,
            },
        ],
        metadata={
          'product_id': rented_storage.id
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

        rented_storage = UserStorage.objects.get(id=order_id)
        rented_storage.paid = True
        rented_storage.save()

        make_qr(
            {
                'owner': rented_storage.user.email,
                'storage': rented_storage.storage.number.replace('№', '#'),
                'expires_at': rented_storage.rent_end.isoformat()
            },
            'payment/qr.png'
        )

        send_email(customer_email)

    return HttpResponse(status=200)


def success_payment(request):
    context = {'user_authorised': request.user.is_authenticated}
    return render(request, 'payment/success.html', context)


def cansel_payment(request):
    return render(request, 'payment/cansel.html')


def send_email(customer_email):
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_HOST_USER
    msg["Subject"] = "Спасибо за заказ в SelfStorage!"
    msg["To"] = customer_email
    msg.set_content("QR код от ячейки находится во вложении!")
    msg.add_attachment(open("payment/qr.png", "rb").read(), maintype='image', subtype='png', filename="qr.png")

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.send_message(msg)
    server.quit()
