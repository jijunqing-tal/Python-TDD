from django.test import TestCase
from django.urls import resolve
from django.utils.html import escape
from lists.views import home_page
from lists.models import Item,List
from lists.forms import ItemForm,ExistingListItemForm,EMPTY_ITEM_ERROR,DUPLICATE_ITEM_ERROR
from django.contrib.auth import get_user_model
# Create your tests here.

User=get_user_model()

class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response=self.client.get('/')
        found=resolve('/')
        self.assertEqual(found.func,home_page)
        self.assertTemplateUsed(response,'home.html')
    def test_home_page_uses_item_form(self):
        reponse=self.client.get('/')
        self.assertIsInstance(reponse.context['form'],ItemForm)
class ListViewTest(TestCase):
    def force_log_in(self):
        user=User.objects.create(email='test@b.com')
        self.client.force_login(user)
        return user
    def test_uses_list_template(self):
        user=self.force_log_in()
        list_=List.objects.create(owner=user)
        response=self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response,'list.html')
    def test_passes_correct_list_to_template(self):
        user=self.force_log_in()
        other_list=List.objects.create(owner=user)
        correct_list=List.objects.create(owner=user)
        response=self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'],correct_list)
    def test_can_save_a_Post_request_to_an_existing_list(self):
        user=self.force_log_in()
        other_list=List.objects.create(owner=user)
        correct_list=List.objects.create(owner=user)
        self.client.post(f'/lists/{correct_list.id}/',data={'text':'A new item for an existing list'})
        self.assertEqual(Item.objects.count(),1)
        new_item=Item.objects.first()
        self.assertEqual(new_item.text,'A new item for an existing list')
        self.assertEqual(new_item.list,correct_list)
    def test_POST_redirects_to_list_view(self):
        user=self.force_log_in()
        other_list=List.objects.create(owner=user)
        correct_list=List.objects.create(owner=user)

        reponse=self.client.post(f'/lists/{correct_list.id}/',data={'text':'A new item for an existing list'})
        self.assertRedirects(reponse,f'/lists/{correct_list.id}/')
    def test_displays_item_form(self):
        user=self.force_log_in()
        list_=List.objects.create(owner=user)
        response=self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'],ExistingListItemForm)
        self.assertContains(response,'name="text"')
    def test_displays_only_items_for_that_list(self):
        user=self.force_log_in()
        correct_list = List.objects.create(owner=user)
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create(owner=user)
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)
        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')
    def post_invalid_input(self):
        user=self.force_log_in()
        list_=List.objects.create(owner=user)
        return self.client.post(f'/lists/{list_.id}/',data={'text':''})
    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(),0)
    def test_for_invalid_input_renders_list_template(self):
        response=self.post_invalid_input()
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'list.html')
    def test_for_invalid_input_passes_form_to_template(self):
        response=self.post_invalid_input()
        self.assertIsInstance(response.context['form'],ExistingListItemForm)
    def test_for_invalid_input_shows_error_on_page(self):
        response=self.post_invalid_input()
        self.assertContains(response,escape(EMPTY_ITEM_ERROR))
    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        user=self.force_log_in()
        list1=List.objects.create(owner=user)
        item1=Item.objects.create(list=list1,text='textey')
        response=self.client.post(f'/lists/{list1.id}/',data={'text':'textey'})
        expected_error=escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response,expected_error)
        self.assertTemplateUsed(response,'list.html')
        self.assertEqual(Item.objects.all().count(),1)
    def test_show_error_if_not_log_in(self):
        user=User.objects.create(email='a@b.com')
        list_=List()
        list_.owner=user
        list_.save()
        Item.objects.create(text='item1',list=list_)
        response=self.client.get(f'/lists/{list_.id}/')
        self.assertNotIn('item1',response.content.decode())
        self.assertIn(escape("You can't get item with not log in"),response.content.decode())
class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new',data={'text':'A new list item'})
        self.assertEqual(Item.objects.count(),1)
        new_item=Item.objects.first()
        self.assertEqual(new_item.text,'A new list item',f'{new_item.text}')
    def test_redirect_after_POST(self):
        response=self.client.post('/lists/new',data={'text':'A new list item'})
        new_list=List.objects.first()
        self.assertRedirects(response,f'/lists/{new_list.id}/')
    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response=self.client.post('/lists/new',data={'text':''})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home.html')
        expected_error=escape("You can't have an empty list item")
        self.assertContains(response,expected_error)
    def test_invalid_list_items_are_not_saved(self):
        self.client.post('/lists/new',data={'text':''})
        self.assertEqual(Item.objects.count(),0)
        self.assertEqual(List.objects.count(),0)
    def test_for_invalid_input_renders_home_template(self):
        response=self.client.post('/lists/new',data={'text':''})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home.html')
    def test_validation_errors_are_shown_on_home_page(self):
        response=self.client.post('/lists/new',data={'text':''})
        self.assertContains(response,escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response=self.client.post('/lists/new',data={'text':''})
        self.assertIsInstance(response.context['form'],ItemForm)
    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user=User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new',data={'text':'new item'})
        list_=List.objects.first()
        self.assertEqual(list_.owner,user)
class MyListsTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        user=User.objects.create(email='a@b.com')
        self.client.force_login(user)
        response=self.client.get('/lists/user/a@b.com/')
        self.assertTemplateUsed(response,'my_lists.html')
    def test_passes_correct_owner_to_template(self):
        user=User.objects.create(email='wrong@owner.com')
        self.client.force_login(user)
        correct_user=User.objects.create(email='a@b.com')
        response=self.client.get('/lists/user/a@b.com/')
        self.assertEqual(response.context['owner'],correct_user)
    def test_show_error_if_user_not_logged_in(self):
        email='a@b.com'
        User.objects.create(email=email)
        response=self.client.get('/lists/user/a@b.com/')
        self.assertIn(f'{email} not logged in',response.content.decode())
