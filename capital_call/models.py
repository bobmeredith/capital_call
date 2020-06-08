# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, transaction
from django.db.models import Count, Sum


class BaseModel(models.Model):

	created_at = models.DateTimeField(auto_now_add=True, null=False)
	last_modified = models.DateTimeField(auto_now=True, null=True)

	class Meta:
		abstract = True

	def __str__(self):
		return f'{self.id}'


class Fund(BaseModel):
	fund_name = models.CharField(max_length=250)

	def __str__(self):
		return f'{self.id} - {self.fund_name}'

class CommitmentManager(models.Manager):

	def build_call_commitments(self, amount):
		commitments = []
		for commitment in Commitment.objects.annotate(allocated=Sum('fund_investments__investment_amount')).order_by('date'):
			undrawn = commitment.amount - (commitment.allocated or 0)
			drawdown = min(amount, undrawn)
			amount -= drawdown
			commitments.append({
				'commitment': commitment,
				'undrawn': undrawn,
				'drawdown': drawdown,
				'remainder': undrawn - drawdown,
			})
		return commitments


class Commitment(BaseModel):
	fund = models.ForeignKey('Fund', on_delete=models.PROTECT )
	date = models.DateTimeField(null=False)
	amount = models.DecimalField(max_digits=10, decimal_places=2)

	objects = CommitmentManager()

	def __str__(self):
		return f'{self.id} - {self.fund.fund_name} - {self.amount}'


class CallManager(models.Manager):

	@transaction.atomic
	def create_call(self, date, name, amount, commitments):
		call = self.create(
			date=date,
			investment_name=name,
			capital_required=amount,
		)
		for commitment in commitments:
			if commitment['drawdown'] > 0:
				new_investment = FundInvestment.objects.create_investment(
					commitment=commitment.get('commitment'),
					call=call, 
					amount=commitment['drawdown']
				)
		return call


class Call(BaseModel):
	date = models.DateTimeField(null=False)
	investment_name = models.CharField(max_length=250)
	capital_required = models.DecimalField(max_digits=10, decimal_places=2)

	objects = CallManager()

	def __str__(self):
		return f'{self.id} - {self.investment_name} - {self.capital_required}'


class InvestmentManager(models.Manager):

    def create_investment(self, commitment, call, amount):
        investment = self.create(
        	commitment=commitment,
        	call=call,
        	investment_amount=amount
        )
        return investment

class FundInvestment(BaseModel):
	commitment = models.ForeignKey('Commitment', on_delete=models.PROTECT, related_name='fund_investments')
	call = models.ForeignKey('Call', on_delete=models.PROTECT, related_name='fund_investments' )
	investment_amount = models.DecimalField(max_digits=10, decimal_places=2)

	objects = InvestmentManager()

	def __str__(self):
		return f'{self.id} - {self.commitment.fund.fund_name} - {self.call.investment_name} - {self.investment_amount}'

