# Generated by Django 4.2.7 on 2024-09-13 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsw_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyperformance',
            name='company',
        ),
        migrations.RemoveField(
            model_name='companyreport',
            name='company',
        ),
        migrations.AlterUniqueTogether(
            name='dailytransaction',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='dailytransaction',
            name='company',
        ),
        migrations.DeleteModel(
            name='IDXMarketCap',
        ),
        migrations.AlterUniqueTogether(
            name='indexdailytransaction',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='indexdailytransaction',
            name='index',
        ),
        migrations.DeleteModel(
            name='MostTradedStock',
        ),
        migrations.RemoveField(
            model_name='subsectorreport',
            name='subsector',
        ),
        migrations.AlterUniqueTogether(
            name='topcompanygrowth',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='topcompanygrowth',
            name='subsector',
        ),
        migrations.DeleteModel(
            name='TopCompanyMover',
        ),
        migrations.AlterUniqueTogether(
            name='toprankedcompany',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='toprankedcompany',
            name='subsector',
        ),
        migrations.DeleteModel(
            name='CompanyPerformance',
        ),
        migrations.DeleteModel(
            name='CompanyReport',
        ),
        migrations.DeleteModel(
            name='DailyTransaction',
        ),
        migrations.DeleteModel(
            name='IndexDailyTransaction',
        ),
        migrations.DeleteModel(
            name='SubsectorReport',
        ),
        migrations.DeleteModel(
            name='TopCompanyGrowth',
        ),
        migrations.DeleteModel(
            name='TopRankedCompany',
        ),
    ]
