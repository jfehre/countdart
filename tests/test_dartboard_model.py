import numpy as np
import pytest

from countdart.utils.dartboard_model import DartboardModel


@pytest.fixture
def model() -> DartboardModel:
    return DartboardModel()


def test_get_translation_vector(model):
    """Test translation vector. This vector is hardcoded"""
    model_vector = model.get_translation_vector()
    assert model_vector is not None
    assert model_vector.shape == (3, 3)
    test_vector = np.array([[1, 0, 350], [0, 1, 350], [0, 0, 1]])
    np.testing.assert_array_equal(model_vector, test_vector)


def test_get_score(model):
    """Test score function of the model"""
    test_dict = {
        "dbull": ((0, 0), "D BULL", 50),
        "bull": ((0, 10), "BULL", 25),
        "s20": ((0, 30), "S 20", 20),
        "d20": ((0, 165), "D 20", 40),
        "t20": ((0, 100), "T 20", 60),
        "m20": ((0, 170.1), "M 20", 0),
        "s6": ((30, 0), "S 6", 6),
        "s3": ((0, -130), "S 3", 3),
        "s11": ((-130, 0), "S 11", 11),
    }
    for value in test_dict.values():
        label, score = model.get_score(value[0])
        assert label == value[1]
        assert score == value[2]


def test_get_outer_points_errors(model):
    """Tests outer points errors"""
    with pytest.raises(ValueError, match=r"Wrong format"):
        model.get_outer_point("20 1")
    with pytest.raises(ValueError, match=r"Wrong format"):
        model.get_outer_point("t | y")
    with pytest.raises(ValueError, match=r"Wrong format"):
        model.get_outer_point("20 + 1")
    with pytest.raises(ValueError, match=r"Out of range"):
        model.get_outer_point("21 | 2")
    with pytest.raises(ValueError, match=r"Out of range"):
        model.get_outer_point("0 | 2")
    with pytest.raises(ValueError, match=r"Invalid label"):
        model.get_outer_point("20 | 20")
    with pytest.raises(ValueError, match=r"Invalid label"):
        model.get_outer_point("20 | 17")


def test_get_outer_points(model):
    """Tests outer points"""
    point = model.get_outer_point("20 | 1")
    assert point == (26.593859056839246, 167.90701790117342)
    point = model.get_outer_point("1 | 20")
    assert point == (26.593859056839246, 167.90701790117342)
    point = model.get_outer_point("5 | 20")
    assert point == (-26.59385905683929, 167.9070179011734)
    point = model.get_outer_point("20 | 5")
    assert point == (-26.59385905683929, 167.9070179011734)
