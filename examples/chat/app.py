# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 by Tomasz Wójcik <labs@tomekwojcik.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""BTHEventSource chat demo."""

import tornado.web
import tornado.ioloop
import tornado.escape
import logging
import os
from optparse import OptionParser
import time
from btheventsource import BTHEventStreamHandler

config = {
    'debug': True
}

listeners = set()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
        
    def post(self):
        message = {
            'author': tornado.escape.xhtml_escape(self.get_argument('author')),
            'message': tornado.escape.xhtml_escape(self.get_argument('message'))
        }
        
        for item in listeners:
            try:
                item.emit(message)
            except:
                pass
            
class EventsHandler(BTHEventStreamHandler):
    listeners = set()
    
    @tornado.web.asynchronous
    def get(self):
        listeners.add(self)
        
    def _on_timeout(self, i):
        if self.request.connection.stream.closed():
            return
        
        if i < 15:
            tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 1, lambda: self._on_timeout(i + 1))
        else:
            self.finish()
        
    @tornado.web.asynchronous
    def post(self):
        listeners.add(self)
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 1, lambda: self._on_timeout(1))
            
routes = [
    (r'/', IndexHandler),
    (r'/events', EventsHandler)
]

if __name__ in ('main', '__main__'):
    parser = OptionParser()
    parser.add_option('-p', '--port', dest="port", help="port to bind to. Defaults to 8888.", action="store", type="int", default=8888)
    options, args = parser.parse_args()
    
    logging_config = {
        'format': "%(asctime)s %(name)s <%(levelname)s>: %(message)s",
        'level': logging.INFO
    }
    
    if config['debug'] == True:
        logging_config['level'] = logging.DEBUG
        
    config['static_path'] = os.path.join(os.path.dirname(__file__), 'static')
        
    logging.basicConfig(**logging_config)
    
    app = tornado.web.Application(routes, **config)
    
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()