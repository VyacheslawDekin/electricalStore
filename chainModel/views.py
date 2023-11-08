import random

from rest_framework import generics
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.decorators import api_view

from .serializers import SupplierSerializer, SupplierSerializerGet, PermissionIsActive, ProductSerializer, PermissionAffiliations
from chainModel.models import Product, Address, Supplier
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from faker import Faker
from django.http import HttpResponse
from .tasks import send_email


class SupplierListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    permission_classes = [PermissionIsActive | HasAPIKey]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SupplierSerializerGet
        return SupplierSerializer

    # def perform_create(self, serializer):
    #     address = Address.objects.get_or_create(
    #         **serializer.validated_data.get("address"))[0]
    #
    #     serializer.save(address=address)

    def get_queryset(self):
        query = Q()
        country = self.request.GET.get("country")
        id_product = self.request.GET.get("id")
        avg = self.request.GET.get("avg")  #для получения задложенности больше средней просто передадим параметр с любым значением

        if not self.request.user.is_anonymous:
            query &= Q(employee=self.request.user)

        if country:
            query &= Q(address__country=country)

        if id_product:
            query &= Q(product__pk=id_product)

        if avg:
            debt_avg = float(Supplier.objects.aggregate(Avg('debt')).get("debt__avg"))
            query &= Q(debt__gt=debt_avg)

        return Supplier.objects.filter(query)


class SupplierRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    permission_classes = [PermissionIsActive | HasAPIKey, PermissionAffiliations]

    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SupplierSerializerGet
        return SupplierSerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [PermissionIsActive | HasAPIKey]


class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [PermissionIsActive | HasAPIKey]

    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'


def create_data(request):

    faker_ = Faker('en_US')

    products = []
    for i in range(100):
        products.append(
            Product(name=faker_.sentence(nb_words=2),
                    model_product=faker_.sentence(nb_words=2),
            )
        )
    Product.objects.bulk_create(products)

    employees = []
    for i in range(20):
        employees.append(
            User(
                username=faker_.name(),
                first_name=faker_.first_name(),
                email=faker_.email(),
                password=faker_.sentence(nb_words=2)
            )
        )
    User.objects.bulk_create(employees)

    addresses = []
    for i in range(20):
        addresses.append(
            Address(country=faker_.country(),
                    city=faker_.city(),
                    street=faker_.street_name(),
                    house_number=random.randint(1, 100)
            )
        )
    Address.objects.bulk_create(addresses)

    types_suppliers = [
        ("factory", "factory"),
        ("distributor", "distributor"),
        ("dealership", "dealership"),
        ("retail_chain", "retail_chain"),
        ("individual_entrepreneur", "individual_entrepreneur")
    ]

    suppliers = []
    for i in range(30):

        parent = Supplier.objects.order_by('?').first()
        if parent.level == 4:
            parent = None

        index = parent.level + 1 if parent else 0

        supplier_created = Supplier.objects.create(
            name=faker_.company(),
            email=faker_.email(),
            address=Address.objects.order_by('?').first(),
            parent=parent,
            type=types_suppliers[index][0],
            debt=random.uniform(-20, 20)
        )
        supplier_created.product.set([Product.objects.order_by('?').first()])
        supplier_created.employee.set([User.objects.order_by('?').first()])

    return HttpResponse("Data created")


@api_view(['GET'])
def send_qr(request, pk):
    user_email = request.user.email
    send_email.delay(user_email, pk)
    return HttpResponse('Qr will be send')





