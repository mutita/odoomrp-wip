# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    @api.one
    @api.depends('package_totals', 'package_totals.quantity')
    def _compute_num_packages(self):
        self.num_packages = 0
        self.num_packages = sum(x.quantity for x in self.package_totals)

    packages = fields.Many2many(
        comodel_name='stock.quant.package',
        relation='rel_wave_package', column1='wave_id',
        column2='package_id', string='Packages')
    package_totals = fields.One2many(
        "stock.picking.package.total", "wave",
        string="Total UL Packages Info", readonly=True)
    num_packages = fields.Integer(
        string='# Packages', compute='_compute_num_packages', store=True)

    def _catch_operations(self):
        self.packages = [
            operation.result_package_id.id for operation in
            self.pickings_operations if operation.result_package_id]
        self._calculate_package_totals()

    def _calculate_package_totals(self):
        if self.package_totals:
            self.package_totals.unlink()
        if self.packages:
            products_ul = self.env['product.ul'].search([])
            for product_ul in products_ul:
                cont = len(self.packages.filtered(lambda x: x.ul_id.id ==
                                                  product_ul.id))
                if cont > 0:
                    values = {'wave': self.id,
                              'ul': product_ul.id,
                              'quantity': cont}
                    self.env['stock.picking.package.total'].create(values)

    @api.one
    def button_refresh_package_totals(self):
        self._calculate_package_totals()


class StockPickingPackageTotal(models.Model):
    _inherit = 'stock.picking.package.total'

    wave = fields.Many2one('stock.picking.wave', string='Wave')
