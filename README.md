### Convalidacao_Espanha

Com a crescente demanda de pedidos provenientes da Espanha para verificação de restrições dos condutores, surgiu a ideia de automatizar o processo. Diego Patrick foi o responsável pelo projeto e Lucas Fontoura o auxiliou na sua elaboração.

- Resumo:

  Este código é um script Python que realiza um conjunto de tarefas automatizadas.
  
  A primeira função a ser executada é a "main()", que inicia o script e imprime a data e hora atuais. 
  
  Em seguida, a função "carregarMunicipios()" é chamada.
  
  O código, então, tenta abrir um programa chamado "HOD" e executá-lo. 
  
  Se ocorrer algum erro, uma exceção será lançada.
  
  Em seguida, o código lê os arquivos TXT na pasta especificada e executa uma série de ações para cada arquivo. 
  
  Cada arquivo é lido e seus registros são processados. 
  
  Para cada registro, o código consulta informações sobre o condutor usando o número de registro do RENACH.
  
  Em seguida, o código procura a pasta do usuário correspondente ao registro e extrai informações básicas do usuário. 
  
  Se ocorrer algum erro durante a extração de informações do usuário, uma exceção será lançada.
  
  Por fim, as informações coletadas são formatadas e escritas em um arquivo de saída. 
  
  O código exclui os arquivos de entrada após o processamento e fecha o programa "HOD" e o painel de controle associado.
