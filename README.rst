About
-----
*offlinetb* is a small utility module for serializing python tracebacks for later examination. Its simple premise is::

  >>> from offlinetb import distill
  >>> try:
  ...    some_code()
  ... except:
  ...    offline_tb = distill()

**distill** returns a Pythonic data structure describing the exception caught. It holds, among else:

* The exception object caught, its type, value representation, and data members
* The traceback itself, frame by frame
* Each frame contains its filename, function name, line number, sample lines before and after, the faulty line itself, and the locals. Each local has its data members, value representation and name distilled.

Distilled tracebacks use only simple datatypes (numbers, strings, lists, dictionaries), guaranteeing their ability to be serialized to other formats (e.g. JSON).

The original purpose of offlinetb was to display tracebacks caught via a web app, and an example for this usage is included; under the **rendering/** directory you can find a sample Javascript, CSS and HTML that displays a given JSON traceback in a *<div>*. 
