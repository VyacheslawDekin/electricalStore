from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Supplier, Address
from .tasks import debt_clearance


admin.site.register(Address)
admin.site.register(Product)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = ['name', 'parent_link', 'type']
    search_fields = ['name']

    ordering = ['name']
    list_filter = ['address__city']

    fieldsets = (
        ('name', {'fields': ['name']}),
        ('description', {'fields': ['email', 'address', 'type', 'parent', 'debt']}),
        ('tables', {'fields': ['product', 'employee']}),
        ('created', {'fields': ['created']}),
    )

    readonly_fields = ['created', 'type']
    actions = ['debt_clearance']

    @admin.display(description='parent')
    def parent_link(self, supplier):
        return mark_safe(f'<a href="/admin/chainModel/supplier/{supplier.parent_id}"> {supplier.parent} </a>')

    @admin.action(description="Debt clearance")
    def debt_clearance(self, request, queryset):
        if len(queryset) > 20:
            debt_clearance.delay(list(queryset.values_list('id', flat=True)))
        else:
            queryset.update(debt=0)

    # change_list_template = "path/to/change_form.html"
    change_form_template = 'admin/chainModel/Supplier/my_change_form.html'





