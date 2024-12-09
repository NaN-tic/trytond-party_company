# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import PoolMeta


class Configuration(metaclass=PoolMeta):
    __name__ = 'party.configuration'

    default_companies = fields.Many2Many(
        'party.configuration-company', 'configuration', 'company',
        'Default Companies', help='Default companies when create a party')


class PartyConfigurationCompany(ModelSQL):
    'Party Configuration Company'
    __name__ = 'party.configuration-company'
    configuration = fields.Many2One(
        'party.configuration', "Configuration", ondelete='CASCADE', required=True)
    company = fields.Many2One(
        'company.company', "Company", ondelete='CASCADE', required=True)
