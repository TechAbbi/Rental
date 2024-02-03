from django.shortcuts import render,redirect

# to calculate sum
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from datetime import date
from django.db.models import Sum, Avg

# Create your views here.

from rest_framework import generics
from rest_framework import viewsets
from .models import Property, UtilityBills, Tenant, Building, BillDetails, PropertyBill
from .serializers import PropertySerializer, UtilityBillsSerializer, TenantSerializer,BuildingSerializer, \
    BillDetailsSerializer, PropertyBillSerializer, FinalBillSerializer

from decimal import Decimal

from . form import BillDetailsForm


from django.http import HttpResponse
from rest_framework.decorators import api_view
from reportlab.pdfgen import canvas
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class UtilityBillsListCreateView(generics.ListCreateAPIView):
    queryset = UtilityBills.objects.all()
    serializer_class = UtilityBillsSerializer


class TenantListCreateView(generics.ListCreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class BuildingListCreateView(generics.ListCreateAPIView):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer


class BillDetailsListCreateView(generics.ListCreateAPIView):
    queryset = BillDetails.objects.all()
    serializer_class = BillDetailsSerializer


class BillDetailsUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BillDetails.objects.all()
    serializer_class = BillDetailsSerializer


class FinalBillView(generics.ListAPIView):
    queryset = BillDetails.objects.all()
    serializer_class = FinalBillSerializer

class UtilityBillSumView(APIView):
    def get(self, request, *args, **kwargs):
        # Assuming you want to calculate the sum for January 2024
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        total_utility_sum = UtilityBills.objects.filter(generation_date__range=(start_date, end_date)).aggregate(
            Sum('bill_amount'))
        sum_amount = total_utility_sum['bill_amount__sum']

        # Serialize the result
        serializer = UtilityBillSerializer({'utility_sum': sum_amount})

        return Response(serializer.data, status=status.HTTP_200_OK)

class UtilityPerUnitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.occupied_days_value = None
        self.total_utility_sum = None
        self.total_bill_days = None
        self.total_units = None
        self.utility_per_unit = None

    def get_utility_bill_sum(self):
        # Assuming you want to calculate for January 2024
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        # Calculate total utility sum for the month
        self.total_utility_sum = \
            UtilityBills.objects.filter(generation_date__range=(start_date, end_date)).aggregate(Sum('bill_amount'))[
                'bill_amount__sum']

        self.total_bill_days = (end_date - start_date).days + 1

    def get_unit_count(self):

        # Calculate total number of flats
        self.total_units = Apartment.objects.count()

    def get_occupied_days(self, request, *args, **kwargs):
        try:
            # Try to get a BillDetails instance using the provided primary key (your_instance_pk)
            bill_details_instance = BillDetails.objects.get(pk=kwargs.get('pk'))

            # If the instance is found, retrieve the occupied_days value
            self.occupied_days_value = bill_details_instance.occupied_days


        except BillDetails.DoesNotExist:
            # Handle the case where the instance is not found
            self.occupied_days_value = 0

    def get(self, request, *args, **kwargs):
        # Handle GET requests here, for example, return some information about the view
        return Response({'detail': 'This endpoint supports POST requests. Use POST to calculate utility per unit.'},
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Handle POST requests here, calculate utility per unit, and return the result
        self.get_utility_bill_sum()
        self.get_unit_count()
        self.get_occupied_days(request, *args, **kwargs)

        # Calculate utility per unit
        if self.total_units and self.total_bill_days:
            # Convert values to Decimal before performing the calculation
            self.utility_per_unit = (Decimal(self.total_utility_sum) / Decimal(self.total_units)) * (
                    Decimal(self.occupied_days_value) / Decimal(self.total_bill_days))
        else:
            self.utility_per_unit = Decimal(0)

        # Serialize the result
        serializer = UtilityPerUnitSerializer({'utility_per_unit': utility_per_unit})

        return Response(serializer.data, status=status.HTTP_200_OK)



class PropertyBillViewSet(viewsets.ModelViewSet):
    queryset = PropertyBill.objects.all()
    serializer_class = PropertyBillSerializer

def bill_details(request):
    form = BillDetailsForm(request.POST or None)
    if request.method == "POST":
        form = BillDetailsForm(request.POST or None)
        if form.is_valid():
            form.save()
        return redirect('rental_app:final-bill')
    return render(request, "rental_app/bill_details.html", {"form": form})


@api_view(['GET'])
def generate_pdf(request):
    # Assuming you have a queryset or instance of FinalBillSerializer data
    # If not, you need to fetch the data to be displayed in the PDF
    data = BillDetails.objects.all() # Replace with your actual data

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="final_bill.pdf"'

    # Create the PDF
    p = canvas.Canvas(response)


    # Customize the PDF content based on your requirements
    for item in data:
        p.drawString(100, 800, f"Property Name: {item.property_name}")
        p.drawString(100, 780, f"Building Name: {item.building_name}")
        p.drawString(100, 760, f"Unit No: {item.unit_no}")
        p.drawString(100, 740, f"Tenant Name: {item.tenant_name}")
        p.drawString(100, 720, f"Rent Days: {item.rent_days}")
        p.drawString(100, 700, f"Status: {item.status}")
        p.drawString(100, 680, f"Utility Per Unit: {item.utility_per_unit}")
        p.drawString(100, 660, f"Rent Amount: {item.rent_amount}")
        p.drawString(100, 640, f"Payable: {item.payable}")
        # Add more lines based on your data structure

        # Move to the next page if needed
        p.showPage()

    p.save()

    return response
