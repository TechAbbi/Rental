from django.db import models
from decimal import Decimal
from datetime import date, datetime
from django.db.models import Sum


# Create your models here.

class Property(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UtilityBills(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True)
    property_name = models.CharField(max_length=255, blank=True, null=True)
    utility = models.CharField(max_length=255)
    generation_date = models.DateField()
    vendor = models.CharField(max_length=255)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.property:
            self.property_name = self.property.name

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.utility}: {self.vendor}"


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    family_members = models.IntegerField()
    email = models.EmailField()
    contact_no = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Building(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True)
    property_name = models.CharField(max_length=20, blank=True, null=True)
    building_name = models.CharField(max_length=20, choices=[], default='')
    unit_no = models.IntegerField(default=1)
    area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bed_rooms = models.IntegerField(default=1)
    bath = models.IntegerField(default=1)
    balcony = models.IntegerField(default=0)
    other = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.property:
            self.property_name = self.property.name

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property_name}-{self.building_name}-{self.unit_no}"


class BillDetails(models.Model):
    STATUS_CHOICES = [
        ('Fully Stay', 'Fully Stay'),
        ('Partial Stay', 'Partial Stay'),
        ('Vacant', 'Vacant'),
    ]
    property = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True)
    # utility_bill = models.ForeignKey(UtilityBills, on_delete=models.CASCADE, blank=True, null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, null=True)
    property_name = models.CharField(max_length=20, blank=True, null=True)
    building_name = models.CharField(max_length=20, blank=True, null=True)
    unit_no = models.CharField(max_length=20, default=1)
    tenant_name = models.CharField(max_length=20, blank=True, null=True)
    occupants = models.PositiveIntegerField(blank=True, null=True)
    rent_start_date = models.DateField(blank=True, null=True)
    rent_end_date = models.DateField(blank=True, null=True)
    rent_days = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    month_start_date = models.DateField(blank=True, null=True)
    month_end_date = models.DateField(blank=True, null=True)
    total_bill_days = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Vacant')
    total_number_of_flats = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utility_bills_consider_from_date = models.CharField(max_length=20, default="2024-01-01")
    utility_bills_consider_to_date = models.CharField(max_length=20, default="2024-01-31")
    total_utility_bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    utility_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payable = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.property:
            self.property_name = self.property.name

        # Copy building name and unit no from linked Building to building name, unit no
        if self.building:
            self.building_name = self.building.building_name
            self.unit_no = self.building.unit_no

        # Copy tenant name and family_members from linked Tenant
        if self.tenant:
            self.tenant_name = self.tenant.name
            self.occupants = self.tenant.family_members

        if self.rent_end_date and self.rent_start_date:
            self.rent_days = Decimal((self.rent_end_date - self.rent_start_date).days + 1)

        try:
            if self.month_start_date and self.month_end_date:
                self.total_bill_days = Decimal((self.month_end_date - self.month_start_date).days + 1)
            else:
                raise ValueError("Please select the month's start and end date")
        except ValueError as e:
            print(e)  # or handle the error message as needed
            self.total_bill_days = Decimal(30)

        if self.rent_days == 0:
            self.status = "Vacant"
        elif self.rent_days == self.total_bill_days:
            self.status = "Fully Stay"
        else:
            self.status = "Partial Stay"

        self.total_number_of_flats = Decimal(Building.objects.count())
        print(type(self.total_number_of_flats))
        # start_date = date(2024, 1, 1)
        # end_date = date(2024, 1, 31)

        start_date = self.utility_bills_consider_from_date
        end_date = self.utility_bills_consider_to_date

        # Calculate total utility sum for the month
        self.total_utility_bill_amount = \
            UtilityBills.objects.filter(generation_date__range=(start_date, end_date)).aggregate(Sum('bill_amount'))[
                'bill_amount__sum']
        # self.total_utility_bill_amount = UtilityBills.objects.all().aggregate(Sum("bill_amount"))["bill_amount__sum"]
        print(type(self.total_utility_bill_amount))

        if self.rent_days > Decimal(0):
            self.utility_per_unit = (self.total_utility_bill_amount / self.total_number_of_flats) * (
                        self.rent_days / self.total_bill_days)
        else:
            self.utility_per_unit = (self.total_utility_bill_amount / self.total_number_of_flats)

        print(type(self.utility_per_unit))

        self.payable = self.utility_per_unit + self.rent_amount
        print(type(self.payable))

        print(self.month_start_date)
        print(type(self.month_start_date))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property_name}-{self.building_name} - {self.unit_no}"


class PropertyBill(models.Model):
    details = models.ForeignKey('BillDetails', on_delete=models.CASCADE)
    building = models.CharField(max_length=255, blank=True, null=True)
    flat_no = models.CharField(max_length=10, blank=True, null=True)
    tenant = models.CharField(max_length=255, blank=True, null=True)
    occupants = models.PositiveIntegerField(default=0)
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    utility_per_unit = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        # Copy values from associated BillDetails
        if self.details:
            self.building = self.details.building
            self.flat_no = self.details.apartment.flat_no if self.details.apartment else None
            self.tenant = self.details.apartment.tenant.name if self.details.apartment and self.details.apartment.tenant else None
            self.occupants = self.details.occupants
            self.rent = self.details.rent
            self.payable = self.rent + self.utility_per_unit

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.building} - {self.flat_no}"
