#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Generate the SQLite database for Golly docset '''

# Libraries
import os
import sys
import sqlite3
from tabulate import tabulate
from bs4 import BeautifulSoup


def main() -> None:
    ''' Main function '''
    if len(sys.argv) > 2:
        print(f'Usage: {sys.argv[0]} [path-to-Golly.docset]')
        sys.exit(1)
    elif len(sys.argv) == 1 and not os.path.exists('Golly.docset'):
        print('No Golly.docset found in current directory.')
        sys.exit(1)
    elif len(sys.argv) == 2 and not os.path.exists(sys.argv[1]):
        print(f'Invalid path: {sys.argv[1]}')
        sys.exit(1)

    golly_path = sys.argv[1] if len(sys.argv) == 2 else os.path.abspath('Golly.docset')

    # Prepare SQLite database
    db_path = os.path.join(golly_path, 'Contents/Resources/docSet.dsidx')
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)')

    # Read index.html
    soup = BeautifulSoup(open(
        os.path.join(golly_path, 'Contents/Resources/Documents/index.html'),
        'r'), 'lxml')
    for link in soup.find_all('a'):
        name, path = link.string, link.get('href')
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)',
                    (name, 'Guide', path))
        print(f'{name} -> {path} [Guide]')

    # Add algorithms as parameters
    soup = BeautifulSoup(open(
        os.path.join(golly_path, 'Contents/Resources/Documents/algos.html'),
        'r'), 'lxml')
    for link in soup.find_all('a'):
        name, path = link.string, link.get('href')
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)',
                    (name, 'Parameter', path))
        print(f'{name} -> {path} [Parameter]')

    # Add lexicons as defines
    soup = BeautifulSoup(open(
        os.path.join(golly_path, 'Contents/Resources/Documents/Lexicon/lex.htm'),
        'r'), 'lxml')
    for link in soup.find_all('center')[1].find_all('a'):
        name, path = link.string, link.get('href')
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)',
                    ('Life Lexicon - ' + name, 'Define', 'Lexicon/' + path))
        print(f'{name} -> {path} [Define]')

    # print the current state of things
    print('\n\nCurrent Values:')
    print(tabulate(cur.execute('SELECT name, type, path FROM searchIndex').fetchall(), headers=[
        'name', 'type', 'path'
    ], tablefmt='github'))

    # commit & close
    con.commit()
    con.close()

# Call main
if __name__ == '__main__':
    main()
