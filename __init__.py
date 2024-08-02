# This file is part party_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import activity
from . import bank
from . import employee
from . import carrier
from . import galatea
from . import party
from . import user
from . import company

def register():
    Pool.register(
        employee.Employee,
        party.PartyCompany,
        party.Party,
        party.Address,
        party.PartyIdentifier,
        party.ContactMechanism,
        user.User,
        company.Company,
        module='party_company', type_='model')
    Pool.register(
        activity.Activity,
        depends=['activity'],
        module='party_company', type_='model')
    Pool.register(
        bank.Bank,
        bank.BankAccount,
        bank.BankAccountNumber,
        depends=['bank'],
        module='party_company', type_='model')
    Pool.register(
        carrier.Carrier,
        depends=['carrier'],
        module='party_company', type_='model')
    Pool.register(
        galatea.GalateaUser,
        depends=['galatea'],
        module='party_company', type_='model')
