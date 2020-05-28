import sys
sys.path.append('./')


from django.shortcuts import get_object_or_404, render
import esail.algm.passage_main as passage_main
from esail.algm.port_code_manage import Port_code_manage

from django.http import HttpResponse, JsonResponse
import simplejson as json
from django.urls import reverse



def index(request):
    port_code_manage = Port_code_manage()
    start_port_code = port_code_manage.get_start_port_code()
    dest_port_code = port_code_manage.get_dest_port_code('KRUSN')

    context = {'start_port_code':start_port_code}
    return render(request, 'esail/index.html',context)

# ajax를 이용해서 호출하는 부분
# 출발항구에서 목적지항구 코드를 가져온다.
def port_code(request,start_code):
    port_code_manage = Port_code_manage()

    dest_port_code = port_code_manage.get_dest_port_code(start_code)
    context = {'start_port_code':dest_port_code}
    return HttpResponse(json.dumps(context),content_type="application/json")




# 항로추천 구현
def passage(request,start_port_code,dest_port_code):
    print("출발코드 = ",start_port_code)
    print("도착코드 = ", dest_port_code)
    #final_route,final_route_marker,passage_plan_dict,barriers_list,final_route_distance,passage_plan_dict_distance,title = passage_main.main(start_port_code,dest_port_code)
    context = passage_main.main(start_port_code,dest_port_code)
    if(context == None) :
        port_code_manage = Port_code_manage()
        start_port_code = port_code_manage.get_start_port_code()
        context = {'start_port_code': start_port_code}
        #return render(request, 'esail/index.html', context)
        return JsonResponse({
           'message': 'FAIL',
        }, json_dumps_params={'ensure_ascii': True})
    #print("항로사전==>",passage_plan_dict)

    # context = {'passages': final_route,
    #            'markers':final_route_marker,
    #            'passage_plan_dict':passage_plan_dict,
    #            'title':title,
    #            'barriers_list':barriers_list,
    #            'final_route_distance':final_route_distance,
    #            'passage_plan_dict_distance':passage_plan_dict_distance
    #           }

    #return render(request, 'esail/passage.html', context)
    #return render(request, '성공', "성공적")
    return JsonResponse({
        'message' : 'SUCCESS',
     }, json_dumps_params = {'ensure_ascii': True})

# 전체항로
def passageAll(request):
    passage_main.makePassagePlanAll()
    port_code_manage = Port_code_manage()
    start_port_code = port_code_manage.get_start_port_code()

    context = {'start_port_code': start_port_code}
    return render(request, 'esail/index.html', context)

