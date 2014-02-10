COMIDA-Minutes-Indexer
======================

County of Monroe Industrial Development Agency Meeting Minutes Indexer

What is this?
=============

This tool was created to index meeting minutes (notes) for the County of Monroe Industrial Development Agency (COMIDA).
The tool has two parts: 1) a web scraper that pulls down the pdf documents, converts them, and then indexes them, 
and 2) a small web application that allows for simple searching of these indexed documents.

You can see a live demo of this code [here](http://comida.mycodespace.net/)

Hacking Instructions
====================

First, if you don't already, install virtualenv

    > sudo pip install virtualenv virtualenvwrapper
    > source /usr/bin/virtualenvwrapper.sh

Pull down the repo (and sub repos)

    > git clone https://github.com/hhroc/COMIDA-Minutes-Indexer
    > cd BarkingOwl
    > git clone https://github.com/thequbit/BarkingOwl
    > cd ../unpdfer
    > git clone https://github.com/thequbit/unpdfer
    > cd ../dler
    > git clone https://github.com/thequbit/dler
    > cd ..

Next, create a virtual enviornment to install packages to.

    > mkvirtualenv comida

To run the scraper, you will need to install these python dependancies:

    > pip install pdfminer==20110515
    > pip install BeautifulSoup4
    > pip install elasticsearch
    > pip install python-magic
    
To run the web app, you will need to install these python dependancies:

    > pip install pymongo
    > pip install flask
    
You will finally need to install the following applications to run the scraper and web app:

    Ubuntu:
    > sudo apt-get install elasticsearch
    > sudo apt-get install mongodb
    
    Fedora:
    > sudo yum install elasticsearch
    > sudo yum install mongodb

