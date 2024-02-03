
from django.urls import path, include
from .views import PropertyListCreateView, UtilityBillsListCreateView, TenantListCreateView, BuildingListCreateView, \
    BillDetailsListCreateView, BillDetailsUpdateDestroyView, PropertyBillViewSet, FinalBillView, bill_details, generate_pdf
from rest_framework import routers
router = routers.DefaultRouter()
router.register("property_bill", PropertyBillViewSet)

app_name = "rental_app"
urlpatterns = [
    path('property/', PropertyListCreateView.as_view(), name='property-list-create'),
    path('utility_bills/', UtilityBillsListCreateView.as_view(), name='utility-bills-list-create'),
    path('tenant/', TenantListCreateView.as_view(), name='tenant-list-create'),
    path('buildings/', BuildingListCreateView.as_view(), name='building-list-create'),
    path('bill_details/', BillDetailsListCreateView.as_view(), name='bill-details-list-create'),
    path('bill_details_update/<int:pk>/', BillDetailsUpdateDestroyView.as_view(), name='bill-details-update'),
    path('final_bill', FinalBillView.as_view(), name="final-bill"),
    path("bill_form", bill_details, name="bill-form"),
    path('generate_pdf/', generate_pdf, name='generate-pdf'),
    # path('utility_bill_sum/', UtilityBillSumView.as_view(), name='utility-bill-sum'),
    # path('utility_per_unit/<int:pk>/', UtilityPerUnitView.as_view(), name='utility-per-unit'),
    path('', include(router.urls))
]
