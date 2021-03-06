document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    let room="Lounge";
    joinRoom(room);
    socket.on('message', (data) => {
        const p = document.createElement('p');
        const span_username=document.createElement('span')
        const span_time=document.createElement('span')
        const br = document.createElement('br');
        if(data.username){
        span_username.innerHTML=data.username;
        span_time.innerHTML = data.time_stamp;
        p.innerHTML= span_username.outerHTML+br.outerHTML+data.msg+br.outerHTML+span_time.innerHTML+br.outerHTML;
        document.getElementById('display-message-section').append(p);
        }
        else{
            printSysMsg(data.msg)
        }
    })

    document.getElementById('send_message').onclick=()=>{
        socket.send({ 'msg':document.getElementById('user_message').value,'username':username,'room':room})
        document.getElementById('user_message').value='';
    }

    document.querySelectorAll('.select-room').forEach(p =>{
        p.onclick=()=>{
            let newRoom = p.innerHTML;
            if(newRoom===room){
                msg=`You are already in ${room} room`;
                printSysMsg(msg);
            }
            else{
                leaveRoom(room);
                joinRoom(newRoom);
                room=newRoom;

            }
        }
    })

    function leaveRoom(room){
        socket.emit('leave',{'username':username,'room':room})
    }
    
    function joinRoom(room){
        socket.emit('join',{'username':username,'room':room})
        document.getElementById('display-message-section').innerHTML=''

    }


    function printSysMsg(msg){
        const p = document.createElement('p');
        p.innerHTML=msg;
        document.getElementById('display-message-section').append(p)
    }


})