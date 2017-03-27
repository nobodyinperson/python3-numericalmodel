
What is :mod:`numericalmodel`?
==============================

The Python package :mod:`numericalmodel` is an attempt to **make prototyping
simple numerical models** in Python an **easy and painless** task.

Why should I prototype a numerical model in Python?
+++++++++++++++++++++++++++++++++++++++++++++++++++

During development phase of a model, it is very handy to be able to flexibly
change crucial model parts. One might want to quickly:

- add more **variables**/**parameters**/**forcings**
- add another **model equation**
- have specific **forcings be time-dependent**
- test another **numerical scheme**
- use **different numerical schemes for each equation**
- **combine numerical schemes** to solve different equation parts 
- etc.

Quickly achieving this in a compiled, inflexible language like **Fortran** or
**C** may not be that easy. Also, debugging or unit testing such a language is
way more inconvenient than it is in Python. With Python, one can take advantage
of the extreme flexibility that object orientation and object introspection
provides. 

While it is obvious, that such a prototyped model written in an interpreted
language like Python will never come up to the speed and efficiency of a
compiled language, it may seem very appealing in terms of flexibility. Once it's
clear how the model should look like and fundamental changes are unlikely to
occur anymore, it can be translated into another, faster language.

Can I implement any numerical model with :mod:`numericalmodel`?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

No, at least for now ``:-)``. Currently, there are a couple of restrictions:

- **only zero-dimensional models** are supported for now. Support for more
  dimensions is on the TODO-list.
- :mod:`numericalmodel` is focused on **physical models**

But that doesn't mean that you can't create new subclasses from
:mod:`numericalmodel` to fit your needs.

Is setting up a numerical model with :mod:`numericalmodel` really that easy?
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Have a look at the :doc:`basics`, :doc:`model-setup` and the :doc:`examples` and
see for yourself.

