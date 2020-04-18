import unittest
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpRequest
from django.urls import reverse
from django.test import TestCase
from django.utils.html import escape
from django.contrib.auth import get_user_model

from lists.views import new_list, share_list
from lists.forms import ItemForm, ExistingListItemForm,EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
from lists.models import Item, List

User = get_user_model()


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1, "Item was not saved into database via POST request")
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item", "Item saved into database with wrong text")

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertRedirects(response, '/lists/1/')

    def test_can_save_a_POST_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1, "Item was not saved into database via POST request")
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new item for an existing list", "Item saved into database with wrong text")
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new list item'}
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0, msg="to-do item was saved to db with invalid input")

    def test_for_invalid_input_renders_lists_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')

        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


class NewListTest(TestCase):
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertEqual(response.context['list'], correct_list)

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0, "New list was created when blank input was typed")
        self.assertEqual(Item.objects.count(), 0, "Item with blank input was saved into database")

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


# redirect was complaining about mocks
def mocked_new_list_form():
    mock = MagicMock()
    mock_form = mock.return_value
    mock_list = mock_form.save.return_value     # Saving should return a list
    mock_list.get_absolute_url = lambda: reverse('view_list', args=[1])
    return mock


@patch('lists.views.NewListForm', new_callable=mocked_new_list_form)
class NewListViewFormTest(unittest.TestCase):

    def setUp(self) -> None:
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mock_new_list_form):
        new_list(self.request)
        mock_new_list_form.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mock_new_list_form):
        mock_form = mock_new_list_form.return_value
        mock_form.is_valid.return_value = True

        new_list(self.request)

        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(self, mock_redirect, mock_new_list_form):
        mock_form = mock_new_list_form.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(self, mock_render, mock_new_list_form):
        mock_form = mock_new_list_form.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, mock_new_list_form):
        mock_form = mock_new_list_form.return_value
        mock_form.is_valid.return_value = False

        new_list(self.request)

        self.assertFalse(mock_form.save.called)


class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_list.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)


class ShareListTest(TestCase):

    def setUp(self) -> None:
        self.owner = User.objects.create(email='a@b.com')
        self.sharee = User.objects.create(email='noreply@share.com')

    def test_post_redirects_to_list_page(self):
        list_ = List.objects.create()

        response = self.client.post(f'/lists/{list_.id}/share', data={
            'sharee': self.sharee.email
        })

        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_sharing_adds_user_to_shared_with_list(self):
        list_ = List.objects.create()
        email = self.sharee.email

        self.client.post(f'/lists/{list_.id}/share', data={
            'sharee': email
        })

        self.assertEqual(list(list_.shared_with.all()), [self.sharee])
