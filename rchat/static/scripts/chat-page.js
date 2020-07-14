document.addEventListener('DOMContentLoaded', () => {

    document.addEventListener('keyup',(event)=>{
        if(event.keyCode===13){
        document.getElementById('send_message').click()
        }
    })

})