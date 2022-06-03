import os
from django.shortcuts import redirect, render
from django.http import JsonResponse
import random
import time
from agora_token_builder import RtcTokenBuilder

from friend.models import FriendList
from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def lobby(request):
    friends = FriendList.objects.filter(user=request.user)[0].friends.all()
    context = {
        'friends':friends
    }
    return render(request, 'videocall/lobby.html', context)

def room(request):
    return render(request, 'videocall/room.html')
    # vc_UID = request.POST["vc_UID"]
    # vc_token = request.POST["vc_token"]
    # vc_to = request.POST["vc_to"]
    # vc_from = request.POST["vc_from"]

    # friends = FriendList.objects.filter(user=request.user)[0].friends.all()
    # id_list = list(friends.values_list('id',flat=True))

    # context = {
    #     'UID': vc_UID,
    #     'token': vc_token,
    #     'room': "VCROOM_" + vc_to + "_" + vc_from if vc_to < vc_from else "VCROOM_" + vc_from + "_" + vc_to,
    #     'name': request.user.username
    # }
    # if vc_to in id_list and vc_from == str(request.user.id):
    #     return render(request, 'videocall/room.html', context)
    # else:
    #     redirect('vc-lobby')

def validateVC(request,vc_to):
    friends = FriendList.objects.filter(user=request.user)[0].friends.all()
    id_list = list(friends.values_list('id',flat=True))
    if vc_to in id_list:
        return True
    else:
        return False

def getToken(request):
    appId = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = request.GET.get('channel')

    try:
        if validateVC(request,int(channelName)) == True: pass
        else: return JsonResponse(status=404, data={'status':'false','message':'ID mismatch'})
    except:
        return JsonResponse(status=404, data={'status':'false','message':'ID mismatch'})

    vc_to = channelName
    vc_from = request.user.id
    room_name = "VCROOM_" + str(vc_to) + "_" + str(vc_from) if int(vc_to) < int(vc_from) else "VCROOM_" + str(vc_from) + "_" + str(vc_to)
    
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, room_name, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid, 'room_name':room_name}, safe=False)


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )
    member.delete()
    return JsonResponse('Member deleted', safe=False)