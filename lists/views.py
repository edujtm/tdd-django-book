from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm


def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})


def new_list(request):
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
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
