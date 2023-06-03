// $(function(){

//     $("#sendcode").click(function(event) {
//         event.preventDefault();
//         var user_nameInput = $("input[name='user_name1']").val();
//         if (!user_name1){
//             console.log('please enter user_name');
//             return;
//         }
//         zlajax.get({
//             'url':'/resetpassword',
//             'data': {
//                 'user_name1': user_name1
//             },
//             'success':function (data){
//                 if(data['code'] == 200){
//                     xtalert.alertSuccessToast('code has been sent');
//                 }else{
//                     xtalert.alertInfo(data['message']);
//                 }
//             },
//             'fail':function(error){
//                 xtalert.alertNetworkError();
//             }
//         });
//     });
// });
