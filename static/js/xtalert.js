
var xtalert = {

    'alertError': function (msg) {
        swal('alert',msg,'error');
    },

    'alertInfo':function (msg) {
        swal('alert',msg,'warning');
    },

    'alertInfoWithTitle': function (title,msg) {
        swal(title,msg);
    },

    'alertSuccess':function (msg,confirmCallback) {
        args = {
            'title': 'Success',
            'text': msg,
            'type': 'success',
        }
        swal(args,confirmCallback);
    }, 

    'alertSuccessWithTitle':function (title,msg) {
        swal(title,msg,'success');
    },

    'alertConfirm':function (params) {
        swal({
            'title': params['title'] ? params['title'] : 'Confirm',
            'showCancelButton': true,
            'showConfirmButton': true,
            'type': params['type'] ? params['type'] : '',
            'confirmButtonText': params['confirmText'] ? params['confirmText'] : 'confirm',
            'cancelButtonText': params['cancelText'] ? params['cancelText'] : 'cancel',
            'text': params['msg'] ? params['msg'] : ''
        },function (isConfirm) {
            if(isConfirm){
                if(params['confirmCallback']){
                    params['confirmCallback']();
                }
            }else{
                if(params['cancelCallback']){
                    params['cancelCallback']();
                }
            }
        });
    },

    'alertOneInput': function (params) {
        swal({
            'title': params['title'] ? params['title'] : 'Please enter',
            'text': params['text'] ? params['text'] : '',
            'type':'input',
            'showCancelButton': true,
            'animation': 'slide-from-top',
            'closeOnConfirm': false,
            'showLoaderOnConfirm': true,
            'inputPlaceholder': params['placeholder'] ? params['placeholder'] : '',
            'confirmButtonText': params['confirmText'] ? params['confirmText'] : 'confirm',
            'cancelButtonText': params['cancelText'] ? params['cancelText'] : 'cancel',
        },function (inputValue) {
            if(inputValue === false) return false;
            if(inputValue === ''){
                swal.showInputError('no content');
                return false;
            }
            if(params['confirmCallback']){
                params['confirmCallback'](inputValue);
            }
        });
    },

    'alertNetworkError':function () {
        this.alertErrorToast('network error');
    },

    'alertInfoToast':function (msg) {
        this.alertToast(msg,'info');
    },

    'alertErrorToast':function (msg) {
        this.alertToast(msg,'error');
    },

    'alertSuccessToast':function (msg) {
        if(!msg){msg = 'success';}
        this.alertToast(msg,'success');
    },

    'alertToast':function (msg,type) {
        swal({
            'title': msg,
            'text': '',
            'type': type,
            'showCancelButton': false,
            'showConfirmButton': false,
            'timer': 1000,
        });
    },

    'close': function () {
        swal.close();
    }
};