from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm

User = get_user_model()


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List()
        list_.owner = request.user
        list_.save()
        form.save_for_list(list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {"form": form})


def view_list(request, pk):
    list_ = List.objects.get(id=pk)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save_for_list(list_)
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, "form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'my_list.html', {'owner': owner})
