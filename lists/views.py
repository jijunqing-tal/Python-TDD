from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from lists.models import Item,List
from lists.forms import ItemForm,ExistingListItemForm
from django.contrib.auth import get_user_model

User=get_user_model()
# Create your views here.
def home_page(request):
    return render(request,'home.html',{'form':ItemForm()})
def view_lists(request,list_id):
    list_=List.objects.get(id=list_id)
    form=ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form=ExistingListItemForm(for_list=list_,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    if request.user.is_authenticated:
        return render(request, 'list.html', {'list': list_,'form':form})
    return render(request,'my_lists.html',{'error_message':"You can't get item with not log in",'form':form})
def new_lists(request):
    form=ItemForm(data=request.POST)
    if form.is_valid():
        list_=List()
        if request.user.is_authenticated:
            list_.owner=request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request,'home.html',{"form":form})
def my_lists(request,email):
    if request.user.is_authenticated:
        owner=User.objects.get(email=email)
        return render(request,'my_lists.html',{'owner':owner})
    return render(request,'my_lists.html',{'error_message':f'{email} not logged in'})
