from django.db import models

# Create your models here.
# Set up appropriate tables for appropriate api response calls later on

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Subsector(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='subsectors')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('sector', 'name')

    def __str__(self):
        return f"{self.sector.name} - {self.name}"

class Industry(models.Model):
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE, related_name='industries')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('subsector', 'name')

    def __str__(self):
        return f"{self.subsector.name} - {self.name}"

class SubIndustry(models.Model):
    # industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name='subindustries')
    industry = models.ManyToManyField(Industry, related_name='subindustries')
    name = models.CharField(max_length=100)

    # class Meta:
    #     unique_together = ('industry', 'name')

    def __str__(self):
        return f"{self.industry.name} - {self.name}"

class Index(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    index = models.ManyToManyField(Index)
    # index = models.ForeignKey('Index', on_delete=models.CASCADE, related_name='companies', null=True, blank=True)
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE, related_name='companies', null=True, blank=True)
    subindustry = models.ForeignKey(SubIndustry, on_delete=models.CASCADE, related_name='companies', null=True, blank=True)

    class Meta:
        unique_together = ('symbol', 'subsector', 'subindustry')

    def __str__(self):
        return f"{self.company_name} ({self.symbol})"
    
class CompanyPerformance(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='performance')
    chg_7d = models.FloatField(null=True, blank=True)
    chg_30d = models.FloatField(null=True, blank=True)
    chg_90d = models.FloatField(null=True, blank=True)
    chg_365d = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Performance of {self.company.company_name} ({self.company.symbol})"
    
class CompanyReport(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='report')
    overview = models.JSONField(blank=True, null=True)
    valuation = models.JSONField(blank=True, null=True)
    future = models.JSONField(blank=True, null=True)
    financials = models.JSONField(blank=True, null=True)
    dividend = models.JSONField(blank=True, null=True)
    management = models.JSONField(blank=True, null=True)
    ownership = models.JSONField(blank=True, null=True)
    peers = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Report of {self.company.company_name} ({self.company.symbol})"
    
class SubsectorReport(models.Model):
    subsector = models.OneToOneField(Subsector, on_delete=models.CASCADE, related_name='report')
    statistics = models.JSONField(blank=True, null=True)
    market_cap = models.JSONField(blank=True, null=True)
    stability = models.JSONField(blank=True, null=True)
    valuation = models.JSONField(blank=True, null=True)
    growth = models.JSONField(blank=True, null=True)
    companies = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Report for Subsector: {self.subsector.name}"

class MostTradedStock(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    volume = models.BigIntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    adjusted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('symbol', 'date')

    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - {self.date}"
    
class TopRankedCompany(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    classification = models.CharField(max_length=50)  # e.g., 'dividend_yield', 'revenue'
    value = models.DecimalField(max_digits=20, decimal_places=2)
    year = models.IntegerField()  # Year for which the ranking is calculated
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE, related_name='ranked_companies', null=True, blank=True)

    class Meta:
        unique_together = ('symbol', 'classification', 'year')

    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - {self.classification} ({self.year})"

class TopCompanyMover(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    classification = models.CharField(max_length=50)  # 'top_gainers' or 'top_losers'
    period = models.CharField(max_length=10)  # e.g., '1d', '7d', '30d'
    price_change = models.FloatField()
    last_close_price = models.DecimalField(max_digits=20, decimal_places=2)
    latest_close_date = models.DateField()

    class Meta:
        unique_together = ('symbol', 'classification', 'period', 'latest_close_date')

    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - {self.classification} ({self.period})"

class TopCompanyGrowth(models.Model):
    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=255)
    classification = models.CharField(max_length=50)  # 'top_earnings_growth_gainers', 'top_revenue_growth_gainers', etc.
    yoy_growth = models.FloatField()  # Year-on-year growth (earnings or revenue)
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE, related_name='growth_companies', null=True, blank=True)

    class Meta:
        unique_together = ('symbol', 'classification')

    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - {self.classification}"

class IDXMarketCap(models.Model):
    date = models.DateField()
    idx_total_market_cap = models.BigIntegerField()
    
    class Meta:
        unique_together = ('date',)

    def __str__(self):
        return f"{self.date}: Market Cap {self.idx_total_market_cap} IDR"

class DailyTransaction(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='daily_transactions')
    date = models.DateField()
    close_price = models.DecimalField(max_digits=20, decimal_places=2)
    volume = models.BigIntegerField()
    market_cap = models.BigIntegerField()

    class Meta:
        unique_together = ('company', 'date')

    def __str__(self):
        return f"Transaction for {self.company.company_name} on {self.date}"
    
class IndexDailyTransaction(models.Model):
    index = models.ForeignKey('Index', on_delete=models.CASCADE, related_name='daily_transactions')
    date = models.DateField()
    closing_price = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        unique_together = ('index', 'date')

    def __str__(self):
        return f"Transaction for {self.index.name} on {self.date}"