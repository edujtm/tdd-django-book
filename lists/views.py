from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

from lists.models import List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm

User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'home.html', {'form': form})


def view_list(request, pk):
    list_ = List.objects.get(id=pk)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, "form": form})


def share_list(request, pk):
    list_ = List.objects.get(id=pk)
    sharee_email = request.POST['sharee']
    sharee = User.objects.get(email=sharee_email)
    list_.shared_with.add(sharee)
    return redirect(list_)


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'my_list.html', {'owner': owner})
