# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import datetime
import pytz
from capital_call.models import FundInvestment, Call, Fund, Commitment

def get_date(date_str):
	return pytz.UTC.localize(datetime.datetime.strptime(date_str[:10], "%d/%m/%Y"))


class CallTestCase(TestCase):
	
	def setUp(self):
		fund1 = Fund.objects.create(fund_name="Fund 1")
    	fund2 = Fund.objects.create(fund_name="Fund 2")
    	fund3 = Fund.objects.create(fund_name="Fund 3")
    	fund4 = Fund.objects.create(fund_name="Fund 4")

    	Commitment.objects.create(fund=fund1, date=get_date('31/12/2017'), amount=10000000)
    	Commitment.objects.create(fund=fund2, date=get_date('31/03/2018'), amount=15000000)
    	Commitment.objects.create(fund=fund3, date=get_date('30/06/2018'), amount=10000000)
    	Commitment.objects.create(fund=fund4, date=get_date('30/09/2018'), amount=15000000)
    	Commitment.objects.create(fund=fund1, date=get_date('31/12/2018'), amount=10000000)


	def test_first_call(self):
		commitments = Commitment.objects.build_call_commitments(9500000)
		self.assertEqual(commitments[0].get('drawdown'), 9500000)
		self.assertEqual(commitments[0].get('remainder'), 500000)
		Call.objects.create_call(commitments=commitments, name='inv1', date=get_date('16/06/2020'), amount=9500000)
		new_call = Call.objects.get(investment_name='inv1')
		investments = FundInvestment.objects.filter(call=new_call)
		self.assertEqual(len(investments), 1)
		self.assertEqual(investments[0].investment_amount, 9500000)
		self.assertEqual(investments[0].commitment.fund.fund_name, 'Fund 1')

	def test_multiple_calls(self):
		# on top of first call taking funds from 3 commitments
		commitments = Commitment.objects.build_call_commitments(9500000)
		Call.objects.create_call(commitments=commitments, name='inv1', date=get_date('16/06/2020'), amount=9500000)
		commitments = Commitment.objects.build_call_commitments(16000000)
		Call.objects.create_call(commitments=commitments, name='inv2', date=get_date('16/06/2020'), amount=15000000)
		new_call = Call.objects.get(investment_name='inv2')
		investments = FundInvestment.objects.filter(call=new_call)
		self.assertEqual(len(investments), 3)
		self.assertEqual(investments[0].investment_amount, 500000)
		self.assertEqual(investments[0].commitment.fund.fund_name, 'Fund 1')
		self.assertEqual(investments[1].investment_amount, 15000000)
		self.assertEqual(investments[1].commitment.fund.fund_name, 'Fund 2')
		self.assertEqual(investments[2].investment_amount, 500000)
		self.assertEqual(investments[2].commitment.fund.fund_name, 'Fund 3')






