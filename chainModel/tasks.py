import random

from electricalStore.celery import app
from .models import Supplier
from django.core.mail import EmailMessage
import qrcode
from django.shortcuts import get_object_or_404
from .serializers import SupplierSerializerGet


@app.task
def increase_debt():
    supplier_queryset = Supplier.objects.all()
    for supplier in supplier_queryset:
        supplier.debt += random.randint(5, 500)
    Supplier.objects.bulk_update(supplier_queryset, ['debt'])


@app.task
def decrease_debt():
    supplier_queryset = Supplier.objects.all()
    for supplier in supplier_queryset:
        supplier.debt -= random.randint(100, 1000)
    Supplier.objects.bulk_update(supplier_queryset, ['debt'])


@app.task
def debt_clearance(suppliers_id):
    suppliers = Supplier.objects.filter(id__in=suppliers_id)
    for supplier in suppliers:
        supplier.debt = 0
    Supplier.objects.bulk_update(suppliers, ['debt'])


@app.task
def send_email(user_email, pk):
    supplier = get_object_or_404(Supplier, id=pk)

    serializer = SupplierSerializerGet(supplier)
    path = f'{pk}.png'
    qrcode.make(serializer.data).save(path)

    email = EmailMessage(
        "QR code",
        f"qrcode supplier '{supplier.name}'",
        "vyacheslaw.dekin@yandex.ru",
        [user_email])

    email.content_subtype = "html"

    email.attach_file(path)
    email.send()
