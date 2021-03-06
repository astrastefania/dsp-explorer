export default
    ['$scope','$uibModal','$http','$rootScope','toastr','MessageModal', 'ModalFactory',
    function ($scope,$uibModal,$http,$rootScope,toastr, MessageModal, ModalFactory) {
    
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
    
    $scope.modal_message = null;
    
    $scope.$watch('toastrMessage', function (newValue, oldValue) {
        _.forEach( newValue, (el) => {
            
            el.tags = el.tags.split(" ")
            let toastr_tags = [ 'debug', 'info', 'success', 'warning', 'error' ]
            
            // Is a Modal
            if( el.tags.indexOf('modal') > -1 ){
                try{

                    console.log(el.message);

                    let modal_options = JSON.parse( el.message );
                    modal_options.body = modal_options.body.replace(/ESCAPE/g, '"');
                    modal_options.title
                        && modal_options.body
                        && MessageModal.openModal(
                            modal_options.title || null,
                            modal_options.body || null,
                            null,
                            null,
                            null,
                            modal_options.footer
                        )
                }
                catch(e){console.log('[ERROR] : modal message object is not valid');}
                return
            }
            // Is a Toastr
            else
            {
                _.forEach(el.tags, (tag)=>{
                    let tag_index = toastr_tags.indexOf(tag)
                    if(tag_index > -1) toastr[toastr_tags[tag_index]](el.message);
                })
            }
            
        })
    })

    // $scope.fitImageToCircle = (image)=> {
    //
    //     if( !image || !image.get(0) ) return
    //     image.removeAttr('style')
    //
    //     let width = image.get(0).naturalWidth
    //     let height = image.get(0).naturalHeight
    //     let css = {'display':'block', 'position': 'absolute'}
    //     width > height? css.height = '100%' : css.width = '100%'
    //     image.css({ display:'block' , width: 'auto'})
    //     image.css(css)
    //
    // }
    //
    // $scope.resizeCircleImages = () =>{
    //     _.each($('.profile-image-static img'), function( el, i){ $scope.fitImageToCircle($(el))})
    //     $scope.fitImageToCircle($('#profile-image'))
    // }
    //
    // angular.element(document).ready(function (a,b,c) {$scope.resizeCircleImages()});

}]