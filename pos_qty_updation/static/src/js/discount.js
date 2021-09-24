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


        onClick() {



                     $.ajax({
   url: 'http://localhost:8069/sample.json?fetch=jsoncallbackjson',
   type: 'GET',
   mode: 'cors',
   crossDomain: true,
    xhrFields: {
      withCredentials: true
   },
   dataType : 'jsonp',
//   Content-Type:'application/json',
      headers: {
  'Access-Control-Allow-Credentials' : true,
  'Access-Control-Allow-Origin':'*',
  'Access-Control-Allow-Methods':'GET',
  'Access-Control-Allow-Headers':'application/json',
   "accept": "application/json",
//     'X-CSRF-Token': token ,
    'Content-Type':'application/json'
},
       success: function (data) {
           alert(data);
       }
   })


//        fetch("http://127.0.0.1/sample.json", {
//            method: 'GET',
//            body: JSON.stringify(data),
//            mode: 'no-cors',
//            headers: {
//                'Content-Type': 'application/json',
//                "Accept": 'application/json',
//            }
//        })
//    .then((data) => data.json())
//    .then((resp) => console.log(resp))
//    .catch((err) => console.log(err))

///             $.ajax({
//   url: 'http://localhost/sample.json',
//   type: 'GET',
//   mode: 'cors',
//   crossDomain: false,
//    xhrFields: {
//      withCredentials: true
//   },
//   dataType : 'json',
//      headers: {
//  'Access-Control-Allow-Credentials' : true,
//  'Access-Control-Allow-Origin':'*',
//  'Access-Control-Allow-Methods':'GET',
//  'Access-Control-Allow-Headers':'application/json',
//   "accept": "application/json",
////     'X-CSRF-Token': token ,
//    'Content-Type':'application/json'
//},
//       success: function (data) {
//           alert(data);
//       }
//   })
//             $.ajax({
//    type: "GET",
//    url: 'http://127.0.0.1',
//    mode: 'cors',
//    contentType: 'application/json',
//    responseType:'application/json',
//    headers: {
//    'Access-Control-Allow-Credentials' : true,
//    'Access-Control-Allow-Origin':'*',
//    'Access-Control-Allow-Methods':'GET',
//    'Access-Control-Allow-Headers':'application/json',
//     "accept": "application/json",
//  },
//
//    dataType : 'jsonp',   //you may use jsonp for cross origin request
//    crossDomain:true,
//    success: function(data) {
//        alert(data);
//     console.log(data);
//    }
//
//    })

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