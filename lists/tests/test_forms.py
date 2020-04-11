from django.test import TestCase

from lists.models import List, Item
from lists.forms import ItemForm, EMPTY_ITEM_ERROR


class ItemFormTest(TestCase):

    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_itens(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid(), msg="Form is valid for blank input")
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'do me'})

        new_item = form.save_for_list(list_)

        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)
