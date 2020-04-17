from django.conf import settings
from django.contrib.auth import get_user_model

from .server_tools import create_session_on_server
from .base import FunctionalTest
from .management.commands.create_session import create_pre_authenticated_session

User = get_user_model()


class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_pre_authenticated_session(email)

        # Para definir um cookie, precisamos antes acessar o domínio.
        # as páginas 404 são as que carregam mais rapidamente
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith é uma usuária logada
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)

    def test_logged_in_users_are_saved_as_my_lists(self):
        # Edith é uma usuaria logada
        self.create_pre_authenticated_session('edith@example.com')

        # Edith acessa a página inicial e começa uma lista
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # Ela percebe o link para "My lists" pela primeira vez
        self.browser.find_element_by_link_text('My lists').click()

        # Ela vê que sua lista está lá, nomeada de acordo com
        # o primeiro item da lista
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Reticulate splines')
        )
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # Ela decide iniciar outra lista, somente para conferir
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        second_list_url = self.browser.current_url

        # Em "my lists", sua nova lista aparece
        self.browser.find_element_by_link_text('My lists').click()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Click cows')
        )
        self.browser.find_element_by_link_text('Click cows').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # Ela faz logout A opção "My lists" desaparece
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_link_text('My lists'),
            []
        ))
