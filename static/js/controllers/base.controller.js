export default [ '$scope','$uibModal','$http','$rootScope', 'toastr', function ($scope,$uibModal,$http,$rootScope,toastr) {
    
    $scope.rootScope = $rootScope;
    
    $scope.openModal = (m) => {
        let modal = $(m);
        if( modal.length>0 ){
            $scope.modalInstance = $uibModal.open({
                template: modal.html(),
                backdrop: 'static',
                scope: $scope
            });
        }
    }
    
    $scope.closeModal = () => { $scope.modalInstance.close();  $scope.modal_message = null;}
    
    $scope.modal_message = null
    $scope.request_membership = (email) => {
        
        return $http({
            'method':'GET',
            'url' : '/api/v1.0/request_membership/'+email
        }).then(
            r => {$scope.modal_message = { message: r.data.message , status : 'success' }}
            ,
            r => {
                if( r.data.hasOwnProperty('message') ) $scope.modal_message = r.data;
                else $scope.modal_message = { message: r.statusText , status : 'error' }
            }
        )

    }

    $scope.$watch('toastrMessage', function (newValue, oldValue) {
        newValue.forEach(function (el) {
            toastr[el.tags](el.message);
        })
    })

}]