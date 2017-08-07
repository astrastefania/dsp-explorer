/**
 * Created by alexcomu on 04/05/17.
 */

export default ['$scope','$http','$sce', function ($scope, $http, $sce) {
    $scope.search_filter = "";
    $scope.results = [];
    $scope.last_members = [];

    $scope.get_last_members = function(search_string){
        if(search_string!=0){
            $scope.preset_search = true;
            $scope.search_filter = search_string;
            $scope.search();
        }
        $http({
            'method': 'GET',
            'url': '/api/v1.0/search/last_members/'
        }).then($scope.handleSearchLastMembersResponse, $scope.handleSearchError);
    };

    $scope.search = function(){
        if($scope.search_filter.length < 3){
            $scope.results = $scope.last_members;
            $scope.is_last_members_label = true;
            return;
        }
        $http({
            'method': 'GET',
            'url': '/api/v1.0/search/members/'+$scope.search_filter+'/'
        }).then($scope.handleSearchResponse, $scope.handleSearchError)
    };

    $scope.highlight = function(text, search) {
        if (!search) {return $sce.trustAsHtml(text);}
        return $sce.trustAsHtml(text.replace(new RegExp(search, 'gi'), '<span class="text-red">$&</span>'));
    };

    $scope.handleSearchLastMembersResponse = function (result) {
        $scope.last_members = result['data']['result'];
        $scope.is_last_members_label = !$scope.preset_search;
        if(!$scope.preset_search)  $scope.results = $scope.last_members;

    };

    $scope.handleSearchResponse = function (result) {
        $scope.is_last_members_label = false;
        $scope.results = result['data']['result']
    };

    $scope.handleSearchError = function(){
        $scope.is_last_members_label = false;
        $scope.results = []
    };

}]