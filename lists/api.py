import json
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from rest_framework import routers, serializers, viewsets

from lists.forms import EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
from lists.models import List, Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'list', 'text')


class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, source='item_set')

    class Meta:
        model = List
        fields = ('id', 'items')


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


router = routers.SimpleRouter()
router.register('lists', ListViewSet)
router.register('items', ItemViewSet)


def get_list(request, pk):
    list_ = List.objects.get(id=pk)

    if request.method == 'POST':
        text = request.POST.get('text')

        if not text or not text.strip():   # Check if string is not blank
            return json_response({'error': EMPTY_ITEM_ERROR}, status=400)

        item = Item(list=list_, text=text)
        try:
            item.validate_unique()
            item.save()
            return HttpResponse(status=201)
        except ValidationError:
            return json_response({'error': DUPLICATE_ITEM_ERROR}, status=400)

    item_dicts = [
        {'id': item.id, 'text': item.text}
        for item in list_.item_set.all()
    ]
    return json_response(item_dicts)


def json_response(json_struct, status=200):
    return HttpResponse(
        json.dumps(json_struct),
        status=status,
        content_type='application/json'
    )
