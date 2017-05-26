# This file is part party_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import carrier
from . import party

def register():
    Pool.register(
        carrier.Carrier,
        party.Party,
        party.Address,
        party.PartyIdentifier,
        party.ContactMechanism,
        module='party_company', type_='model')
