import pytest

from structures.time import Time


def test_times_are_equal():
    assert Time(1, 2) == Time(1, 2)


def test_first_time_is_bigger():
    assert Time(15, 10) > Time(10, 15)


def test_first_time_is_less():
    assert Time(4, 8) < Time(5, 10)


def test_time_addition():
    assert Time(12, 5) + Time(8, 4) == Time(20, 9)


def test_time_addition_with_minutes_overflow():
    assert Time(15, 35) + Time(2, 130) == Time(19, 45)
