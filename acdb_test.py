import os.path
import tempfile

import pytest

import acdb


def driver_easy_case(driver):
    driver.set('name', b'acdb')
    assert driver.get('name') == b'acdb'
    assert driver.all() == ['name']
    driver.rm('name')
    with pytest.raises(Exception):
        driver.get('name')


def emerge_easy_test(emerge):
    emerge.set('name', 'acdb')
    assert emerge.get('name') == 'acdb'
    assert emerge.all() == ['name']
    emerge.rm('name')
    emerge.set('n', 0)
    for _ in range(64):
        emerge.incr('n')
    assert emerge.get('n') == 64
    emerge.rm('n')

    assert emerge.none('name')
    emerge.set_none('name', 'acdb')
    assert emerge.some('name')
    emerge.set_some('name', 'bcad')
    assert emerge.get('name') == 'bcad'
    emerge.set_none('name', 'acdb')
    assert emerge.get('name') == 'bcad'


def test_mem_driver():
    driver = acdb.MemDriver()
    driver_easy_case(driver)


def test_doc_driver():
    driver = acdb.DocDriver(os.path.join(tempfile.gettempdir(), 'acdb'))
    driver_easy_case(driver)


def test_lru_driver():
    driver = acdb.LruDriver()
    driver_easy_case(driver)


def test_lru_dirver_full():
    driver = acdb.LruDriver(1024)
    for i in range(1024):
        driver.set(i, str(i))
    assert len(driver.dict) == 1024
    assert list(driver.dict.keys())[-1] == 1023
    driver.set(1024, '1024')
    assert len(driver.dict) == 769
    assert driver.get(512) == '512'
    with pytest.raises(KeyError):
        driver.get(0)


def test_map_driver():
    driver = acdb.MapDriver(os.path.join(tempfile.gettempdir(), 'acdb'))
    driver_easy_case(driver)


def test_json_emerge():
    emerge = acdb.mem()
    emerge_easy_test(emerge)
