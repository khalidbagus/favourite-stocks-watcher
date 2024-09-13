from .views import *
from django.urls import path, include

urlpatterns = [
    path('get-subsectors', SubsectorsView.as_view(), name='get-subsectors'),
    path('get-industries', IndustriesView.as_view(), name='get-industries'),
    path('get-subindustries', SubIndustryView.as_view(), name='get-subindustries'),
    path('get-companies-by-index', CompaniesByIndexView.as_view(), name='get-companies-by-index'),
    path('get-companies-by-subsector', CompaniesBySubsectorView.as_view(), name='get-companies-by-subsector'),
    path('get-companies-by-subindustry', CompaniesBySubindustryView.as_view(), name='get-companies-by-subindustry'),
    path('get-companies', CompanyView.as_view(), name='get-companies')
]