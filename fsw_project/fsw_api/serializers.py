from rest_framework import serializers
from .models import *

class SubsectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'

class SubIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubIndustry
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        depth = 2

class CompaniesByIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = ['symbol', 'company_name', 'index']

class CompaniesBySubsectorSerializer(serializers.ModelSerializer):
    #subsector = SubsectorSerializer("subsector")
    class Meta:
        model = Company 
        fields = ['symbol', 'company_name', 'subsector']
        depth = 1

class CompaniesBySubindustySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company 
        fields = ['symbol', 'company_name', 'subindustry']

# class CompanyPerformanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CompanyPerformance
#         fields = '__all__'

# class CompanyReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CompanyReport
#         fields = '__all__'

# class SubsectorReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subsector
#         fields = '__all__'

# class MostTradedStockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MostTradedStock
#         fields = '__all__'

# class TopRankedCompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TopRankedCompany
#         fields = '__all__'

# class TopCompanyMoverSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TopCompanyMover
#         fields = '__all__'

# class TopCompanyGrowthSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TopCompanyGrowth
#         fields = '__all__'

# class IDXMarketCapSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IDXMarketCap
#         fields = '__all__'

# class DailyTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DailyTransaction
#         fields = '__all__'

# class IndexDailyTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IndexDailyTransaction
#         fields = '__all__'