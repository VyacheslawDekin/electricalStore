from datetime import datetime
from rest_framework import serializers, permissions
from chainModel.models import Product, Address, Supplier
from django.contrib.auth.models import User


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ['country', 'city', 'street', 'house_number']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name', 'model_product', 'launch_date']

    def validate(self, data):
        """
        Check that start is before finish.
        """
        # Проверка только при изменении данных
        if self.context.get('request').method in ['PUT', 'PATCH']:
            if len(data['name']) > 25:
                raise serializers.ValidationError("The name must be less than 25 characters")
            if len(data['launch_date']) > datetime.date.today():
                raise serializers.ValidationError("Launch date is not correct")
        return data


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class SupplierSerializerGet(serializers.ModelSerializer):

    address = AddressSerializer()
    product = ProductSerializer(many=True)
    employee = EmployeeSerializer(many=True)

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'address', 'product', 'employee', 'parent', 'debt', 'created']
        read_only_fields = ['debt', 'created']

    def get_fields(self):
        fields = super(SupplierSerializerGet, self).get_fields()
        fields['parent'] = SupplierSerializerGet(many=False)
        return fields


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'address', 'product', 'parent', 'employee', 'debt', 'created']
        read_only_fields = ['debt', 'created']

    def validate_name(self, value):
        # Проверка только при изменении данных
        if self.context.get('request').method in ['PUT', 'PATCH'] and len(value) > 50:
            raise serializers.ValidationError('The name must be less than 50 characters')
        return value


class PermissionIsActive(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Supplier):
        return request.user.is_active


class PermissionAffiliations(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Supplier):
        return request.user in obj.employee.all()






