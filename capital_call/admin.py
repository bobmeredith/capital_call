# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Fund, Commitment, Call, FundInvestment

# Register your models here.
admin.site.register(Fund)
admin.site.register(Commitment)
admin.site.register(Call)
admin.site.register(FundInvestment)

