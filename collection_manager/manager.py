#!/usr/bin/env python
from flask import Flask, render_template, redirect, url_for
from elixir import *
from flask.ext.wtf import Form, TextField, Required, SelectField
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import ColumnProperty

app = Flask(__name__)
app.secret_key = '\xcb\xb9|\xf5\xfb<]{\xf2\x94\x98\xab-0n\xf9kT\x98\xf8\x00\xa5\x98M'

app.config.QRCODE_URL = True
# app.config.QRCODE_IDS = True

app.config.STATES = ['unopened', 'opened', 'assembled', 'based', 'primed',
                     'blackwashed', 'partially basecoated', 'basecoated',
                     'partially washed', 'washed', 'partially drybrushed',
                     'drybrushed', 'clearcoated', 'bulletcoated']


def make_form(entity):
    col_prop_names = [p for p in entity.mapper.iterate_properties
                            if isinstance(p, ColumnProperty)]
    attrs = {}
    for prop in col_prop_names:
        name = str(prop.key)
        validators = [Required()]

        coltype = None
        if hasattr(prop.columns[0], 'type'):
            coltype = prop.columns[0].type

        if isinstance(coltype, sqlalchemy.types.Enum):
            attrs[name] = SelectField(name.capitalize(),
                                      choices=[(k, k.title()) for i, k in enumerate(coltype.enums)],
                                      default=getattr(entity, name),
                                      )
        else:
            attrs[name] = TextField(name.capitalize(),
                                    default=getattr(entity, name),
                                    validators=validators)


    new_class = type(entity.__class__.__name__+"Form",
                     (Form,),
                     attrs)
    return new_class()


def form_to_elixir(form, entity):
    '''Copy all the form data to the entity and return it.'''
    for field in form._fields:
        setattr(entity, field, getattr(form, field).data)
    return entity


class Item(Entity):
    name = Field(Unicode)
    location = Field(Unicode)
    category = Field(Unicode)
    state = Field(Enum(*app.config.STATES))
    photos = OneToMany('Photo')


class Photo(Entity):
    name = Field(Unicode)
    data = Field(Binary, deferred=True)
    item = ManyToOne('Item')


def init_database():
    metadata.bind = "sqlite:///collection.sqlite"
    metadata.bind.echo = True
    setup_all()
    create_all()


@app.route('/update/', methods=("GET", "POST"))
@app.route('/update/<id>', methods=("GET", "POST"))
def update(id=None):
    '''Show a form to update an entry in the database.
    If the ID doesn't exist, create it.'''
    if not id:
        id = (session.query(func.max(Item.id)).scalar() or 0) + 1
    thisitem = Item.get(id) or Item(id=id)

    form = make_form(thisitem)

    if form.validate_on_submit():
        form_to_elixir(form, thisitem)
        session.commit()
        return redirect(url_for('items'))
    else:
        # Remove it from the session until we're ready to really insert it
        session.expunge(thisitem)
        return render_template("update.html",
                               form=form,
                               id=id)


@app.route('/items/')
def items():
    '''Show a listing of items.'''
    return render_template("items.html",
                           items=Item.query.all(),
                           getattr=getattr)


@app.route('/items/<id>')
def item(id=None):
    '''Show a single item's data.'''
    return "Hello item."


@app.route('/')
def index():
    return redirect(url_for('items'))

def main():
    init_database()
    app.run('0.0.0.0', debug=True)

if __name__ == '__main__':
    main()
