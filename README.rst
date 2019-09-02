Logger
======

Tool responsible to read Apache log fiels and register each access into Ratchet
(Access Statisitics Tool).

.. image:: https://travis-ci.org/scieloorg/Logger.svg?branch=master
    :target: https://travis-ci.org/scieloorg/Logger


Instalaçao
==========

Para iniciar o processo de instalaçao é necessario ter uma cópia do Logger no
computador onde se deseja fazer a instalaçao.

Essa cópia pode ser feita através do comando "git clone" ou através de donwload
da versao desejada.


Pré-requisitos
--------------

1. Copia do Logger no servidor onde a aplicaçao será instalada
2. Uma instancia de MongoDB acessível
3. ArticleMeta acessível
4. Verificar arquivo requirements.txt para lista de dependencias python

Passos para instalaçao
----------------------

1. Acessar o diretório da aplicaçao
2. Instalar dependencias python

#> pip install -r requirements.txt

3. Instalar aplicaçao

#> python setup.py install

4. Configuraçao de variáveis de ambiente


