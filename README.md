### Convalidacao_Espanha

Com a crescente demanda de pedidos provenientes da Espanha para verificação de restrições dos condutores, surgiu a ideia de automatizar o processo. Diego Patrick foi o responsável pelo projeto e Lucas Fontoura o auxiliou na sua elaboração.

### Resumo do Projeto

O Convalidacao_Espanha é um script Python que executa uma série de tarefas automatizadas. O código começa executando a função "main()", que imprime a data e hora atuais e inicia o script. Em seguida, a função "carregarMunicipios()" é chamada.

O programa, então, tenta abrir o programa "HOD" e executá-lo. Se houver algum problema com a execução, uma exceção será lançada. Em seguida, o código lê os arquivos TXT da pasta especificada e executa uma série de ações para cada arquivo.

Cada arquivo é lido e seus registros são processados. Para cada registro, o código consulta informações sobre o condutor usando o número de registro do RENACH. Em seguida, o código procura a pasta do usuário correspondente ao registro e extrai informações básicas do usuário. Se ocorrer algum erro durante a extração de informações do usuário, uma exceção será lançada.

Por fim, as informações coletadas são formatadas e escritas em um arquivo de saída. O código exclui os arquivos de entrada após o processamento e fecha o programa "HOD" e o painel de controle associado.

### Conclusão

O Convalidacao_Espanha é um projeto útil e eficiente que automatiza o processo de verificação de restrições dos condutores na Espanha. Graças ao trabalho de Diego Patrick e Lucas Fontoura, agora é possível lidar com uma grande demanda de pedidos de forma rápida e eficiente.
