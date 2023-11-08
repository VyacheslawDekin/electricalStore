import datetime
from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from django.contrib.auth.models import User


class Address(models.Model):
    class Meta:
        verbose_name_plural = "Addresses"

    country = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    street = models.CharField(max_length=250)
    house_number = models.CharField(max_length=5)

    def __str__(self):
        return f'{self.country}, {self.city}, {self.street}, {self.house_number}'


class Product(models.Model):
    name = models.CharField(max_length=250)
    model_product = models.CharField(max_length=250)
    launch_date = models.DateField(default=datetime.datetime.now().date())

    def __str__(self):
        return f'{self.name}, {self.model_product}, {self.launch_date}'


# class Employee(models.Model):
#     name = models.CharField(max_length=500)
#     created = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f'{self.name}'


types_suppliers = [
        ("factory", "factory"),
        ("distributor", "distributor"),
        ("dealership", "dealership"),
        ("retail_chain", "retail_chain"),
        ("individual_entrepreneur", "individual_entrepreneur")
    ]


class Supplier(MPTTModel):

    name = models.CharField(max_length=250)
    email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ManyToManyField(Product, blank=True)
    employee = models.ManyToManyField(User, blank=True) #Здесь manytomany, потому что проще по коду, чем делать FK в таблице User
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    debt = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    type = models.CharField(max_length=25, choices=types_suppliers, default="factory")
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        index = self.parent.level+1 if self.parent else 0
        if self.parent and self.parent.level == 4:
            raise ValueError('Maximum nesting')

        self.type = types_suppliers[index][0]
        super(Supplier, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'






