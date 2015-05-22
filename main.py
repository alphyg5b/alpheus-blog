#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created  = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class MainHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * from Post order by created DESC limit 10")
        self.render("post.html",posts = posts)

class Permalink(Handler):
    def get(self,post_id):
        s = Post.get_by_id(int(post_id))
        self.render("post.html",posts = [s])

class New(Handler):
    def render_form(self,error="",valtitle="",valpost=""):
        self.render("form.html" , error=error , valtitle=valtitle, valpost=valpost)

    def get(self):
        self.render_form()

    def post(self):
        title = self.request.get("subject")
        post = self.request.get("content")
        if title and post:
            p = Post(title = title , post = post)
            post_key = p.put()
            self.redirect('/%d' % post_key.id())
        else:
            self.render_form("Both title and post, Please!",title,post)

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/newpost',New),
                               ('/(\d+)',Permalink)
                                ], debug=True)
