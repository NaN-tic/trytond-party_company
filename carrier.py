# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, ModelView
from . import party

__all__ = ['Carrier']


class Carrier(ModelSQL, ModelView, party.PartyCompanyMixin):
    __name__ = 'carrier'
