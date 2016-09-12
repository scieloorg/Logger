# coding: utf-8
import os
import thriftpy
import json
import logging

from thriftpy.rpc import make_client
from xylose.scielodocument import Article, Journal

LIMIT = 1000

logger = logging.getLogger(__name__)

articlemeta_thrift = thriftpy.load(
    os.path.join(os.path.dirname(__file__))+'/articlemeta.thrift')


class ServerError(Exception):
    def __init__(self, message=None):
        self.message = message or 'thirftclient: ServerError'

    def __str__(self):
        return repr(self.message)


def articlemeta(host):

    address, port = host.split(':')

    return ArticleMeta(address, port)


class ArticleMeta(object):

    def __init__(self, address, port):
        """
        Cliente thrift para o Articlemeta.
        """
        self._address = address
        self._port = port

    @property
    def client(self):

        client = make_client(
            articlemeta_thrift.ArticleMeta,
            self._address,
            int(self._port)
        )
        return client

    def journal(self, code, collection=None):

        kwargs = {
            'code': code,
        }

        if collection:
            kwargs['collection'] = collection

        journal = self.client.get_journal(**kwargs)

        if not journal:
            return None

        jjournal = json.loads(journal)
        xjournal = Journal(jjournal)

        return xjournal

    def journals(self, collection=None, issn=None):
        offset = 0
        while True:
            identifiers = self.client.get_journal_identifiers(
                collection=collection, issn=issn, limit=LIMIT, offset=offset)
            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                yield self.journal(
                    code=identifier.code[0], collection=identifier.collection
                )

            offset += 1000

    def document(self, code, collection, replace_journal_metadata=True, fmt='xylose'):
        try:
            article = self.client.get_article(
                code=code,
                collection=collection,
                replace_journal_metadata=replace_journal_metadata,
                fmt=fmt
            )
        except:
            msg = 'Error retrieving document: %s_%s' % (collection, code)
            raise ServerError(msg)

        jarticle = json.loads(article)

        if not jarticle:
            return None

        if fmt == 'xylose':
            xarticle = Article(jarticle)
            return xarticle
        else:
            return article

    def documents(self, collection=None, issn=None, from_date=None,
                  until_date=None, fmt='xylose'):
        offset = 0
        while True:
            identifiers = self.client.get_article_identifiers(
                collection=collection, issn=issn, from_date=from_date,
                until_date=until_date, limit=LIMIT, offset=offset)

            if len(identifiers) == 0:
                raise StopIteration

            for identifier in identifiers:

                document = self.document(
                    code=identifier.code,
                    collection=identifier.collection,
                    replace_journal_metadata=True,
                    fmt=fmt
                )

                yield document

            offset += 1000

    def collections(self):
        return [i for i in self.client.get_collection_identifiers()]
