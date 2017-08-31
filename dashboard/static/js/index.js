import * as angular from 'angular';

// Import this app style
require("../style/index.scss")
// Require static angular componenets
let baseImports = require("../../../static/js/index")
// Angular form imports
baseImports.angularForm()

// Stuff
require('ng-infinite-scroll')
require("../../../node_modules/vsGoogleAutocomplete/dist/vs-google-autocomplete");
require("../../../static/js/footer/header.footer.behaviour")

// Init Angular APP
var app = angular.module('dashboard', ['ui.bootstrap', 'toastr', 'ui.select','ngSanitize', 'ngAnimate','mgcrea.ngStrap', 'infinite-scroll', 'vsGoogleAutocomplete'])
    .config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{$');
            $interpolateProvider.endSymbol('$}');
    }])
    .config(['$qProvider', function ($qProvider) {$qProvider.errorOnUnhandledRejections(false);}]);

// Require base angular componenets
baseImports.angularBase(app)


app.controller('dashboardController', require('./controllers/dashboard.controller').default )
app.controller('onboardingController', require('./controllers/onboarding.controller').default )
app.controller('themesController', require('./controllers/themes.controller').default )
app.controller('searchController', require('./controllers/searchmembers.controller').default )

