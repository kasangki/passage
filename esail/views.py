import sys
sys.path.append('./')


from django.shortcuts import get_object_or_404, render
import esail.algm.passage_main as passage_main

from django.http import HttpResponseRedirect
from django.urls import reverse



def index(request):
    # latest_question_list = Question.objects.all().order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    # return render(request, 'polls/index.html', context)
    #passage_main.main()
    return render(request, 'esail/index.html')

def passage(request,passage_id):
    # latest_question_list = Question.objects.all().order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    # return render(request, 'polls/index.html', context)
    final_route,final_route_marker,passage_plan_dict = passage_main.main(passage_id)
    title = ""
    if(passage_id == 1) :
        title = '울산 -> 광양'
    else :
        title = '광양 -> 싱가폴'

    context = {'passages': final_route,
               'markers':final_route_marker,
               'passage_plan_dict':passage_plan_dict,
               'title':title}

    return render(request, 'esail/passage.html', context)


# Create your views here.
