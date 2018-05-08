# This file is part party_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import activity
from . import commission
from . import bank
from . import carrier
from . import party
from . import user


def register():
    Pool.register(
        party.Party,
        party.Address,
	user.User,
        user.UserCompany,
        party.PartyIdentifier,
        party.ContactMechanism,
        module='party_company', type_='model')
    Pool.register(
        activity.Activity,
        depends=['activity'],
        module='party_company', type_='model')
    Pool.register(
        bank.Bank,
        bank.BankAccount,
        depends=['bank'],
        module='party_company', type_='model')
    Pool.register(
        carrier.Carrier,
        depends=['carrier'],
        module='party_company', type_='model')
    Pool.register(
	commission.Manager,
	commission.Agent,
        depends=['commission'],
        module='party_company', type_='model')
