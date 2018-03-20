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
        activity.Activity,
        bank.Bank,
        bank.BankAccount,
        carrier.Carrier,
        party.PartyCompany, # register before party.Party
        party.Party,
        party.Address,
        party.PartyIdentifier,
        party.ContactMechanism,
        commission.Manager,
        commission.Agent,
        user.User,
        user.UserCompany,
        module='party_company', type_='model')
