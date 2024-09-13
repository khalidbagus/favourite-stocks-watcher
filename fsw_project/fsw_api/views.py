from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import *
from .serializers import *

# Create your views here.
class SubsectorsView(ListAPIView):
    queryset = Subsector.objects.all()
    serializer_class = SubsectorSerializer
    
    """ Set up caching mechanism
    def list(self, request):
    """

class IndustriesView(ListAPIView):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    
    """ Set up caching mechanism
    def list(self, request):
    """

class SubIndustryView(ListAPIView):
    queryset = SubIndustry.objects.all()
    serializer_class = SubIndustrySerializer
    
    """ Set up caching mechanism
    def list(self, request):
    """

class CompanyView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        ticker = self.request.query_params.get('ticker', None)
        if ticker:
            queryset = queryset.filter(symbol__iexact=ticker)
        return queryset

class CompaniesByIndexView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompaniesByIndexSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        index = self.request.query_params.get('index', None)
        if index:
            queryset = queryset.filter(index=index)
        return queryset
    """ Set up caching mechanism
    def list(self, request):
    """

class CompaniesBySubsectorView(ListAPIView):
    queryset = Company.objects.all().prefetch_related('subsector')
    serializer_class = CompaniesBySubsectorSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sub_sector = self.request.query_params.get('sub-sector', None)
        if sub_sector:
            queryset = queryset.filter(subsector=sub_sector)
        return queryset.values()
    """ Set up cacing mechanism
    def list(self, request):
    """

class CompaniesBySubindustryView(ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompaniesBySubindustySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sub_industry = self.request.query_params.get('sub-industry', None)
        if sub_industry:
            queryset = queryset.filter(subindustry=sub_industry)
        return queryset
    """ Set up cacing mechanism
    def list(self, request):
    """

# class CompanyPerformanceView(ListAPIView):
#     queryset = CompanyPerformance.objects.all()
#     serializer_class = CompanyPerformanceSerializer
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         ticker = self.request.query_params.get('ticker', None)
#         if ticker:
#             queryset = queryset.filter(company__symbol=ticker)
#         return queryset
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """


# class CompanyReportView(ListAPIView):
#     queryset = CompanyReport.objects.all()
#     serializer_class = CompanyReportSerializer
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         ticker = self.request.query_params.get('ticker', None)
#         section = self.request.query_params.get('section', None)

#         if ticker:
#             queryset = queryset.filter(company__symbol=ticker)

#         if section and section in ['overview', 'valuation', 'future', 'peers', 'financials', 'dividend', 'management', 'ownership']:
#             queryset = queryset.values('company', section) 

#         return queryset
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class SubsectorReportView(ListAPIView):
#     queryset = SubsectorReport.objects.all()
#     serializer_class = SubsectorReportSerializer

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         sub_sector = self.request.query_params.get('sub_sector', None)

#         if sub_sector:
#             queryset = queryset.filter(subsector__name=sub_sector)
#         return queryset
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# # TO DO LATER
# class MostTradedStockView(ListAPIView):
#     queryset = MostTradedStock.objects.all()
#     serializer_class = MostTradedStockSerializer

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         start = self.request.query_params.get('start', None)
#         end = self.request.query_params.get('end', None)
#         n_stock = self.request.query_params.get('n_stock', None)
#         adjusted = self.request.query_params.get('adjusted', None)
#         sub_sector = self.request.query_params.get('sub_sector', None)
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class TopRankedCompanyView(ListAPIView):
#     queryset = TopRankedCompany.objects.all()
#     serializer_class = TopRankedCompanySerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class TopCompanyMoverView(ListAPIView):
#     queryset = TopCompanyMover.objects.all()
#     serializer_class = TopCompanyMoverSerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class TopCompanyGrowthView(ListAPIView):
#     queryset = TopCompanyGrowth.objects.all()
#     serializer_class = TopCompanyGrowthSerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class IDXMarketCapView(ListAPIView):
#     queryset = IDXMarketCap.objects.all()
#     serializer_class = IDXMarketCapSerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class DailyTransactionView(ListAPIView):
#     queryset = DailyTransaction.objects.all()
#     serializer_class = DailyTransactionSerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """

# class IndexDailyTransactionView(ListAPIView):
#     queryset = IndexDailyTransaction.objects.all()
#     serializer_class = IndexDailyTransactionSerializer
    
#     """ Set up cacing mechanism
#     def list(self, request):
#     """