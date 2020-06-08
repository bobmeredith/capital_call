# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from decimal import Decimal
import datetime

from .models import FundInvestment, Call, Fund, Commitment


class WelcomeView(TemplateView):
	template_name = 'welcome.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

class DashboardView(TemplateView):
	template_name = 'dashboard.html'

	def get(self, request, *args, **kwargs):
		# Map fund investments by call
		call_map = {}
		for investment in FundInvestment.objects.all():
			call_id = investment.call.id
			call_funds = call_map.get(call_id, {})
			if not call_funds:
				call_map[call_id] = call_funds
			fund_id = investment.commitment.fund.id
			call_funds[fund_id] = call_funds.get(fund_id,0) + investment.investment_amount
		calls = []
		for call in Call.objects.all():
			calls.append({
				'call': call,
				'funds': call_map.get(call.id)
			})
			call_map[call.id] = {'call'}
		return render(request, self.template_name, {
			'page': 'dashboard',
			'fund_investments': FundInvestment.objects.all(), 
			'calls': calls,
			'funds': Fund.objects.all(),
			'call_map': call_map
		})

class CallView(TemplateView):
	template_name = 'create_call.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {
			'page': 'new_call',
		})

	def post(self, request, *args, **kwargs):
		button = request.POST.get('button')
		required_amount = Decimal(request.POST.get('amount') or '0')
		name = request.POST.get('name')
		date_str = request.POST.get('date')
		date = datetime.datetime.strptime(date_str[:10], "%d/%m/%Y") if date_str else None

		commitments = Commitment.objects.build_call_commitments(required_amount)

		if button == 'calculate':
			return render(request, self.template_name, {
				'page': 'new_call',
				'date': date,
				'name': name,
				'amount': required_amount,
				'commitments': commitments
			})
		elif button == 'confirm':
			Call.objects.create_call(commitments=commitments, name=name, date=date, amount=required_amount)
			return redirect('/capital_call/dashboard/')










