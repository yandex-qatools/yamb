"""
Holds tests for ``verba.utils``

"""
import yaml
import pytest

from hamcrest import assert_that, has_properties, has_property, is_, contains, has_string, contains_string, all_of

from yamb import YAMLY, Attr, Another, Many


class Foo(YAMLY):
    __tag__ = 'Foo'

    bar = Attr()
    baz = Attr()


def test_yamly_load():
    foo = Foo._load('''
bar: 1
baz: 'ololo'
    ''')

    assert_that(foo, has_properties(bar=1, baz='ololo'))


def test_yamly_save():
    foo = Foo(bar=2, baz='pewpew')

    assert_that(yaml.load(foo._dump()), is_(dict(bar=2, baz='pewpew')))


@pytest.mark.parametrize('value', [5, 'a', []])
def test_default_load(value):
    class Simple(YAMLY):
        a = Attr(default=value)

    assert_that(Simple._load('{}'), has_properties(a=value))


def test_roundabout_save():
    foo = Foo(bar=2, baz=3)

    foo.bar = 5

    assert_that(foo, has_property('bar', 5))
    assert_that(Foo._load(foo._dump()), has_property('bar', 5))


class Bar(YAMLY):
    foo = Another(Foo)
    thing = Attr()


def test_another_load():
    doc = '''
foo:
   bar: 1
   baz: 2
    '''

    assert_that(Bar._load(doc), has_property('foo', has_properties(bar=1, baz=2)))


def test_another_save():
    bar = Bar()
    bar.foo = Foo(bar='test', baz='values')

    assert_that(yaml.load(bar._dump()), is_(dict(foo=dict(bar='test', baz='values'))))


def test_another_update():
    bar = Bar()
    bar.foo = Foo(bar='test', baz='values')
    bar.foo.baz = 'ololo'

    assert_that(yaml.load(bar._dump()), is_(dict(foo=dict(bar='test', baz='ololo'))))


def test_another_as_argument():
    bar = Bar(foo=Foo(bar='test', baz='values'))

    assert_that(yaml.load(bar._dump()), is_(dict(foo=dict(bar='test', baz='values'))))


class Thing(YAMLY):
    value = Attr()


class Lots(YAMLY):
    things = Many(Thing)


def test_many_load():
    doc = '''
things:
   - value: 2
   - value: 3
   - value: 4
    '''

    assert_that(Lots._load(doc), has_property('things', contains(*[has_property('value', x) for x in [2, 3, 4]])))


def test_many_save():
    l = Lots()

    l.things = [Thing(value=2), Thing(value=3)]

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': 2}, {'value': 3}]}))


def plusequals(l, t):
    l.things += [t]


@pytest.mark.parametrize('appender', [lambda l, t: l.things.append(t),
                                      plusequals])
def test_many_append(appender):
    l = Lots()
    l.things = [Thing(value='a')]
    appender(l, Thing(value='b'))

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': 'a'}, {'value': 'b'}]}))


def test_many_del():
    l = Lots()
    l.things = [Thing(value='1')]

    del l.things[0]

    assert_that(yaml.load(l._dump()), is_({'things': []}))


def test_many_set():
    l = Lots(things=[Thing(value='1')])

    l.things[0] = Thing(value='foo')

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': 'foo'}]}))


def test_many_set_item_field():
    l = Lots(things=[Thing(value='1')])

    l.things[0].value = 'foo'

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': 'foo'}]}))


def test_many_set_item_field_from():
    l = Lots(things=[])

    l.things.append(Thing(value='1'))

    l.things[0].value = 'foo'

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': 'foo'}]}))


def test_many_as_arg():
    l = Lots(things=[Thing(value='1')])

    assert_that(yaml.load(l._dump()), is_({'things': [{'value': '1'}]}))


@pytest.mark.parametrize('operator', [lambda t: setattr(t, 'not_there', 123),
                                      lambda t: getattr(t, 'not_there')],
                         ids=['set', 'get'])
def test_nondeclared_attributes(operator):
    """
    Check that non-declared attributes cannot be accessed
    """
    with pytest.raises(AttributeError):
        operator(Thing(value=5))


def test_nondeclared_attributes_at_constructor():
    """
    Check that non-declared attributes cannot be accessed
    """
    with pytest.raises(AttributeError) as e:
        Thing(not_there=5)

    assert_that(e.value, has_string(all_of(contains_string('Thing'),
                                           contains_string('unknown'),
                                           contains_string('not_there'),
                                           )))


def test_fields_settable():
    class Test(YAMLY):
        a = Attr()
        b = None

    x = Test()

    x.b = 5
    assert x.b == 5
