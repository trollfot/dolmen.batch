# -*- coding: utf-8 -*-

from os import path
from urllib import urlencode

from cromlech.browser import IRenderer
from cromlech.i18n import ILanguage
from dolmen.location import absolute_url
from dolmen.template import TALTemplate
from z3c.batching.batch import Batch
from zope.interface import implements


TEMPLATES_DIR = path.join(path.dirname(__file__), 'templates')


def template_path(filename):
    return path.join(TEMPLATES_DIR, filename)


class Batcher(object):
    implements(IRenderer)

    template = TALTemplate(template_path('batch.pt'))

    def __init__(self, context, request, prefix='batch', size=10):
        self.context = context
        self.request = request
        self.url = absolute_url(self.context, self.request)
        self.prefix = prefix
        self.size = size
        self.batch = None

    @property
    def available(self):
        return bool(self.batch is not None and len(self.batch.batches))

    def previous(self):
        batch = self.batch.batches[0]
        while batch is not self.batch:
            yield batch
            batch = batch.next

    def next(self):
        batch = self.batch.next
        while batch:
            yield batch
            batch = batch.next

    def batch_info(self, start=0):
        start = int(self.request.form.get(self.prefix + '.start', start))
        size = int(self.request.form.get(self.prefix + '.size', self.size))
        return start, size

    def update(self, sequence, *args, **kw):
        start, size = self.batch_info()
        self.batch = Batch(sequence, start=start, size=size)

    def batch_url(self, batch):
        start_param = self.prefix + ".start"
        size_param = self.prefix + ".size"
        params = [(k,v) for k, v in self.request.form.items()
                  if k not in (start_param, size_param)]
        params.append((start_param, batch.start))
        params.append((size_param, batch.size))
        return self.url + '?' + urlencode(params)

    def namespace(self):
        namespace = {}
        namespace['batch'] = self.batch
        namespace['batcher'] = self
        namespace['context'] = self.context
        return namespace

    @property
    def target_language(self):
        return ILanguage(self.request, None)

    def render(self, *args, **kwargs):
        if not self.available:
            return u''
        return self.template.render(self, target_language=self.target_language)
