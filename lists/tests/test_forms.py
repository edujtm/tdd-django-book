import unittest
from unittest.mock import patch, Mock
from django.test import TestCase

from lists.models import List, Item
from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR, ExistingListItemForm, ItemForm, NewListForm


class ItemFormTest(TestCase):

    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_itens(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid(), msg="Form is valid for blank input")
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])


class ExistingListItemFormTest(TestCase):
    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()

        form = ExistingListItemForm(for_list=list_, data={'text': ''})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='no twins!')

        form = ExistingListItemForm(for_list=list_, data={'text': 'no twins!'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

    def test_form_save(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'hi'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])


class NewListFormTest(unittest.TestCase):

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_post_data_if_not_user_authenticated(
            self, mock_list_create_new
    ):
        user = Mock(is_authenticated=False)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_list_create_new.assert_called_once_with(
            first_item_text='new item text'
        )

    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_with_owner_if_user_authenticated(
            self, mock_list_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_list_create_new.assert_called_once_with(
            first_item_text='new item text', owner=user
        )

    @patch('lists.forms.List.create_new')
    def test_when_commit_is_false_should_not_create_list(self, mock_list_create_new):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user, commit=False)
        self.assertFalse(mock_list_create_new.called)

    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(self, mock_list_create_new):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        response = form.save(owner=user)
        self.assertEqual(response, mock_list_create_new.return_value)
