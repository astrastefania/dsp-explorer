window.$ = window.jQuery = require('jquery')

require("bootstrap-sass")
require("../style/index.scss")
require('../../../node_modules/bootstrap-additions/dist/bootstrap-additions.min.css');

import  * as  _  from 'lodash'
import * as angular from 'angular';

require('angular-ui-bootstrap');
require('angular-toastr');
require('angular-sanitize');
require('angular-animate');
require('angular-strap');
require("../../../node_modules/cookieconsent/build/cookieconsent.min");
require('ng-infinite-scroll')

let app = angular.module('dashboard', ['ui.bootstrap', 'toastr' , 'ngSanitize', 'ngAnimate','mgcrea.ngStrap', 'infinite-scroll'])
    .config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{$');
            $interpolateProvider.endSymbol('$}');
    }]);

app.config(['$qProvider', function ($qProvider) {
    $qProvider.errorOnUnhandledRejections(false);
}]);

app.controller('baseController', require('../../../static/js/controllers/base.controller').default )
require("../../../static/js/footer/header.footer.behaviour")


export { app };

app.controller('dashboardController', require('./controllers/dashboard.controller').default )
app.controller('themesController', require('./controllers/themes.controller').default )
app.controller('searchController', require('./controllers/searchmembers.controller').default )

require("../../../static/js/cookie/cookie.policy.behaviour");