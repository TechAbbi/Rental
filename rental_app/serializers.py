from rest_framework import serializers
from .models import Property, UtilityBills, Tenant, Building, BillDetails, PropertyBill


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class UtilityBillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityBills
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class BillDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillDetails
        fields = '__all__'


class FinalBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillDetails
        fields = ["property_name", "building_name", "unit_no", "tenant_name", "rent_days", "status", "utility_per_unit",
                  "rent_amount", "payable"]



class PropertyBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyBill
        fields = '__all__'
