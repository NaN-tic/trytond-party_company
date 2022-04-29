# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.model import fields
from trytond.pyson import Eval

__all__ = ['GalateaUser']


class GalateaUser(metaclass=PoolMeta):
    __name__ = 'galatea.user'
    companies = fields.Function(fields.One2Many(
        'company.company', None, 'Companies'), 'on_change_with_companies')

    @classmethod
    def __setup__(cls):
        super(GalateaUser, cls).__setup__()
        cls.websites.domain += [('company', 'in', Eval('companies'))]
        cls.websites.depends += ['companies']

    @fields.depends('party', '_parent_party.companies')
    def on_change_with_companies(self, name=None):
        User =  Pool().get('res.user')

        if self.party and self.party.companies:
            return [c.id for c in self.party.companies]
        else:
            user = User(Transaction().user)
            return [c.id for c in user.companies]

    @staticmethod
    def default_websites():
        # overwrite default_websites from galatea module because add websites
        # by company
        pool = Pool()
        Website = pool.get('galatea.website')
        User = pool.get('res.user')

        user = User(Transaction().user)
        return [p.id for p in Website.search([
            ('registration', '=', True),
            ('company', '=', user.company)
            ])]
