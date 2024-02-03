class UtilityPerUnitView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.occupied_days_value = None
        self.total_utility_sum = None
        self.total_bill_days = None
        self.total_units = None

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
            utility_per_unit = (Decimal(self.total_utility_sum) / Decimal(self.total_units)) * (
                    Decimal(self.occupied_days_value) / Decimal(self.total_bill_days))
        else:
            utility_per_unit = Decimal(0)

        # Serialize the result
        serializer = UtilityPerUnitSerializer({'utility_per_unit': utility_per_unit})

        return Response(serializer.data, status=status.HTTP_200_OK)
