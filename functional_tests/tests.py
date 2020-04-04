from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import unittest

MAX_WAIT = 10

class NewVisitorTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Firefox()

  def tearDown(self):
    self.browser.quit()

  def wait_for_row_in_list_table(self, row_text):
    start_time = time.time()
    while True:
      try:
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])
        return
      except (AssertionError, WebDriverException) as e:
        if time.time() - start_time > MAX_WAIT:
          raise e
        time.sleep(0.5)

  def test_can_start_a_list_and_retrieve_it_later(self):
    # Edith ouviu falar de uma nova aplicação online interessante para
    # listas de tarefa. Ela decide verificar sua homepage
    self.browser.get(self.live_server_url)

    # Ela percebe que o título da página e o cabeçalho mencionam listas de tarefas (To-Do)
    self.assertIn("To-Do", self.browser.title)
    header_text = self.browser.find_element_by_tag_name('h1').text
    self.assertIn("To-Do", header_text)

    # Ela é convidada a inserir um item de tarefa imediatamente
    inputbox = self.browser.find_element_by_id('id_new_item')
    self.assertEqual(
      inputbox.get_attribute('placeholder'),
      'Enter a to-do item'
    )

    # Ela digita "Comprar penas de pavão" em uma caixa de texto 
    # (O hobby de Edith é fazer iscas para pesca com fly)
    inputbox.send_keys('Buy peacock feathers')
    inputbox.send_keys(Keys.ENTER)
    time.sleep(1)

    # Ainda continua havendo uma caixa de texto convidando-a a acrescentar outro
    # item. Ela insere "Usar penas de pavão para fazer uma isca" 
    self.wait_for_row_in_list_table('1: Buy peacock feathers')
    
    inputbox = self.browser.find_element_by_id('id_new_item')
    inputbox.send_keys('Use peacock feathers to make a fly')
    inputbox.send_keys(Keys.ENTER)
    time.sleep(1)

    # A página é atualizada novamente e agora mostra os dois itens em sua lista
    self.wait_for_row_in_list_table('1: Buy peacock feathers')
    self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')

  def test_multiple_users_can_start_lists_in_different_urls(self):
    # Edith inicia uma nova lista de tarefas
    self.browser.get(self.live_server_url)

    inputbox = self.browser.find_element_by_id('id_new_item')
    inputbox.send_keys('Buy peacock feathers')
    inputbox.send_keys(Keys.ENTER)
    self.wait_for_row_in_list_table('1: Buy peacock feathers')

    # Ela percebe que sua lista possui um url unico
    edith_list_url = self.browser.current_url
    self.assertRegex(edith_list_url, '/lists/.+')

    # Outro usuário, chamado Francis, chega ao site

    # Usamos uma nova sessão de navegador para garantir que nenhuma informação
    # de Edith esta vindo de cookies, etc
    self.browser.quit()
    self.browser = webdriver.Firefox()

    # Francis acessa a página inicial, não há nenhum sinal da lista de Edith
    self.browser.get(self.live_server_url)
    page_text = self.browser.get_element_by_tag_name('body').text
    self.assertNotIn('Buy peacock feathers', page_text)
    self.assertNotIn('make a fly', page_text)

    # Francis inicia uma nova lista inserind um item novo. Ele é menos interessante
    # que edith
    inputbox = self.browser.get_element_by_id('id_new_item')
    inputbox.send_keys('Buy milk')
    inputbox.send_keys(Keys.ENTER)
    self.wait_for_row_in_list_table('1: Buy milk')

    # Francis tambem possui um url exclusivo
    francis_list_url = self.browser.current_url
    self.assertRegex(francis_list_url, '/lists/.+')
    self.assertNotEqual(francis_list_url, edith_list_url, "Different users have the same list url")

    # Novamente não há nenhum sinal da lista de Edith
    page_text = self.browser.get_element_by_tag_name('body').text
    self.assertNotIn('Buy peacock feathers', page_text)
    self.assertNotIn('make a fly', page_text)

    # Satisfeitos, ambos voltam a dormir