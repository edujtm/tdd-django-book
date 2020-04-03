from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):

  def setUp(self):
    self.browser = webdriver.Firefox()

  def tearDown(self):
    self.browser.quit()

  def test_can_start_a_list_and_retrieve_it_later(self):
    # Edith ouviu falar de uma nova aplicação online interessante para
    # listas de tarefa. Ela decide verificar sua homepage
    self.browser.get('http://localhost:8000/')

    # Ela percebe que o título da página e o cabeçalho mencionam listas de tarefas (To-Do)
    self.assertIn("To-Do", self.browser.title)
    self.fail("Finish the test!")

    # Ela é convidada a inserir um item de tarefa imediatamente

    # Ela digita "Comprar penas de pavão" em uma caixa de texto 
    # (O hobby de Edith é fazer iscas para pesca com fly)

    # Ainda continua havendo uma caixa de texto convidando-a a acrescentar outro
    # item. Ela insere "Usar penas de pavão para fazer uma isca" 

    # A página é atualizada novamente e agora mostra os dois itens em sua lista

    # Edith se pergunta se o site se lembrará das suas notas. Então ela percebe
    # que o site gerou um URL único para ela -- há um pequeno texto explicativo 
    # para isso

    # Ela acessa esse URL - sua lista de tarefas continua lá
  
if __name__ == '__main__':
  unittest.main(warnings="ignore")