odoo.define('pos_qty_updation.RewardButton', function(require) {
'use strict';
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { posbus } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require('web.custom_hooks');
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');
   const { isRpcError } = require('point_of_sale.utils');
   var core = require('web.core');
   var rpc = require('web.rpc');
    var QWeb = core.qweb;
   class CustomQtyButtons extends PosComponent {
       constructor() {
           super(...arguments);
           useListener('click', this.onClick);
       }
       is_available() {
           const order = this.env.pos.get_order();
           return order
       }


       async onClick() {
            try {
//            var self = this;
                // ping the server, if no error, show the screen

            var read= []
            var qty_read= []
           var posted = false;
           await this.rpc({
                model: "product.qty.updation",
                method: "read_file_button",
                args: [this.id] // empty parameters
            }).then(function (data) {
            read.push(parseFloat(data));
            qty_read.push(data);
            if(read){
            return read[0]
            }


           console.log(data); });

           var order = this.env.pos.get_order();
            var value = order.selected_orderline
             if (qty_read && qty_read[0]=='QTY'){

             this.showPopup('ErrorPopup', {
                        title: this.env._t('Missing Quantity'),
                        body: this.env._t('Cannot Update the Quantity.'),
                    });
//                alert("Update Quantity is Missing ")
                }
            if (isNaN(read)){
                console.log(read);
                }
            else
                 {
                    order.selected_orderline.set_quantity(read)
                 }

         } catch (error) {
                if (isRpcError(error) && error.message.code < 0) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Cannot access order screen if offline.'),
                    });
                } else {
                    throw error;
                }
            }
        }


   }
   CustomQtyButtons.template = 'CustomQtyButtons';
   ProductScreen.addControlButton({
       component: CustomQtyButtons,
       condition: function() {
           return this.env.pos;
       },
   });
   Registries.Component.add(CustomQtyButtons);
   return CustomQtyButtons;
});