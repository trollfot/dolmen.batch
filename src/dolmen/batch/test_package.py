# -*- coding: utf-8 -*-

from cromlech.browser.testing import XMLDiff, TestHTTPResponse, TestHTTPRequest
from cromlech.io.interfaces import IPublicationRoot
from dolmen.batch import Batcher
from zope.interface import implements
from zope.location import Location


NO_BATCH = '''
<div class="batch">
  <ul>
    <li class="current">1</li>
  </ul>
</div>
'''

BATCHED = '''
<div class="batch">
  <ul>
    <li class="current">1</li>
    <li class="next">
      <a href="http://localhost?batch.start=2&amp;batch.size=2">2</a>
    </li>
    <li class="next">
      <a href="http://localhost?batch.start=4&amp;batch.size=2">3</a>
    </li>
    <li class="next">
      <a href="http://localhost?batch.start=6&amp;batch.size=2">4</a>
    </li>
  </ul>
</div>
'''

BATCHED_ADV = '''
<div class="batch">
  <ul>
    <li class="previous">
      <a href="http://localhost?batch.start=0&amp;batch.size=2">1</a>
    </li>
    <li class="previous">
      <a href="http://localhost?batch.start=2&amp;batch.size=2">2</a>
    </li>
    <li class="current">3</li>
    <li class="next">
      <a href="http://localhost?batch.start=6&amp;batch.size=2">4</a>
    </li>
  </ul>
</div>
'''


def test_batch():

    sequence = [1, 3, 5, 7, 9, 11, 13, 15]

    class Publishable(Location):
        implements(IPublicationRoot)

    root = Publishable()
    request = TestHTTPRequest()
    batcher = Batcher(root, request)
    batcher.update(sequence)
    assert not XMLDiff(batcher.render(), NO_BATCH)

    request = TestHTTPRequest(form={'batch.size': 2})
    batcher = Batcher(root, request)
    batcher.update(sequence)
    assert not XMLDiff(batcher.render(), BATCHED)

    request = TestHTTPRequest(form={'batch.size': 2, 'batch.start': 4})
    batcher = Batcher(root, request)
    batcher.update(sequence)
    assert not XMLDiff(batcher.render(), BATCHED_ADV)
