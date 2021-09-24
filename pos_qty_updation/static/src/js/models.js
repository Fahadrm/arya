odoo.define('pos_qty_updation.models', function(require) {
	"use strict";

    var models = require('point_of_sale.models');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    var SuperOrderline = models.Orderline.prototype;

	models.load_models([
	 {
		model: 'product.qty.updation',
		condition: function(self) {
			return true; },
		fields: ['id', 'name', 'pos_qty'],
		domain: function(self) {
			return []; },
		loaded: function(self, result) {
			self.set({ 'pos_qty_updation': result });
		},
	}], { 'after': 'product.product' });




});
