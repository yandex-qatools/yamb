yamb
====

.. image:: https://travis-ci.org/yandex-qatools/yamb.svg?branch=master 
        :alt: Build Status
        :target: https://travis-ci.org/yandex-qatools/yamb/

YAml Meta Binding microframework

Define schema for YAML documents a-la SQLAlchemy to read, write and manipulate data like a python object.


Basic example
=============

.. code:: python

 from yamb import Literal, Nested, Collection, YAMBObject


 class Address(YAMBObject):
     city = Literal(default='New York')
     street = Literal()

 class Person(YAMBObject):
     name = Literal()
     phone = Literal()
     address = Nested(Address)

     def lives_close_to(self, another_person):
         return self.address.city == another_person.address.city

 class Phonebook(YAMBObject):
     title = Literal()
     people = Collection(Person)


 friends = Phonebook(title='Friends', people=[])

 friends.people.append(Person(name='Sue', phone='+12345', address=Address(street='Some blvd')))
 sam = Person(name='Sam', phone='+123456', address=Address(city='London', street='Picadilly'))
 friends.people += [sam]

 with open('friends.yml', 'w') as f:
     f.write(friends._dump())

 parsed = Phonebook._load(open('friends.yml'))

 assert parsed.title == 'Friends'
 assert parsed.people[0].address.city == 'New York'
 assert parsed.people[1].name == 'Sam'


