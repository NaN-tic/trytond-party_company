# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from . import party

__all__ = ['Activity']


class Activity(party.PartyCompanyMixin, metaclass=PoolMeta):
    __name__ = "activity.activity"

    @classmethod
    def __setup__(cls):
        super(Activity, cls).__setup__()
        cls.party.required = True
