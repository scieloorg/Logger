Logger
======

Tool responsible to read Apache log fiels and register each access into Ratchet
(Access Statisitics Tool).

.. image:: https://travis-ci.org/scieloorg/Logger.svg?branch=master
    :target: https://travis-ci.org/scieloorg/Logger


Instalação
==========

Para iniciar o processo de instalação é necessario ter uma cópia do Logger no
computador onde se deseja fazer a instalação.

Essa cópia pode ser feita através do comando "git clone" ou através de download
da versao desejada.


Pré-requisitos
--------------

1. Copia do Logger no servidor onde a aplicação será instalada
2. Uma instancia de MongoDB acessível
3. ArticleMeta acessível
4. Verificar arquivo requirements.txt para lista de dependencias python

Passos para instalação
----------------------

1. Acessar o diretório da aplicação
2. Instalar dependencias python

#> pip install -r requirements.txt

3. Instalar aplicação

#> python setup.py install


Passos para Configurações de Websites da Metodologia SPF
--------------------------------------------------------
Crie ou edite o arquivo `new_websites.json` (baseado no `new_websites.json.template`).


```json
[
  {
    "new": "nbr",
    "old: "scl"
  },
  {
    "new": "acron_novo",
    "old: "acron_antigo"
  }
]
```


Passos para Configurações
-------------------------

Copiar o arquivo de template de configuração.

#> cp config.ini.template config.ini

Criar uma variável de ambiente com o path para o arquivo de configuração

#> export LOGGER_SETTINGS_FILE=config.ini

Os parâmetros a serem configurados sao:

**mongo_uri**

Caminho para a base de dados MongoDB.

**rabbitmq**

Caminho para o rabbimq. O RabbitMQ só será necessário se o inspetor de diretório
de logs (inspector.py) for utilizado.

**logs_source**

Local onde serao depositados os arquivos de log do apache para processamento.

**robots_file**

Caminho para arquivo com lista de robos. Esta lista de robos é utilizada para
ignorar a contagem de acessos originados por user_agent compatível com os nomes
disponíveis nesta lista.

**counter_compliant**

Indicar se o processamento de logs irá considerar as regras do Counter Code
of Practice 4 para a contagem de acessos.

**log_format**

Indicar o formato do log do apache. O Logger utiliza a biblioteca **apachelog**
para fazer o parsing de cada linha de log. Verificar a documentação desta 
biblioteca para mais informações sobre como mapear uma linha de log.

**articlemeta**

Path para a API Thrift do ArticleMeta, ex: 127.0.0.1:11621.

Também é possível indicar a URL da API Resftul.

Executando a processamento
==========================

Existem duas maneiras de processar os logs do Apache utilizando o Logger (
logger_inspector, logger_loadlogs_scielo). Após a instalação do Logger, três
console scripts serao habilitados no terminal.

**logger_inspector**

Este comando inspeciona um diretório a espera de arquivos de logs. Uma vez que
um arquivo de log é depositado no diretório indicado, um processamento de log
será enviado para uma fila de processamento de logs gerida através do **celery**.

Para tanto, é necessário ter uma fila iniciada antes da execução do comando.

Para mais informação, Executar:

#> logger_inspector --help 

**logger_loadlogs_scielo**

Este comando processa os logs disponíveis em um diretório. 

Para mais informação, Executar:

#> logger_loadlogs_scielo --help 


**logger_loadlogs_readcube**

Este comando processa os logs disponíveis em um diretório. O formato dos aquivos
de log devem seguir o formato de arquivos fornecidos pelo ReadCube. 

Para mais informação, Executar:

#> logger_loadlogs_readcube --help 


Iniciando Task Celery
=====================

Iniciar uma Celery task é pré-requisito caso o logger_inspector seja utilizado.

Para iniciar a task o seguinte comando deve ser executado, e uma instância de 
rabbibmq deve estar disponível e devidamente configurada no arquivo de configuração.

#> celery -A logger.tasks worker -l DEBUG
