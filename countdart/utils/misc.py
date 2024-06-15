""" Miscellaneous helper functions"""
import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from countdart.database.schemas.config import AllConfigModel


def encode_numpy(array: np.ndarray) -> bytes:
    """Encodes numpy array to bytes. Will save shape of array in bytes string.
    The decode function assumes the array is in uint8.
    See: https://stackoverflow.com/a/60457732


    Args:
        array (np.ndarray): an uint8 array to encode

    Returns:
        bytes: encoded array
    """

    if len(array.shape) == 2:
        h, w = array.shape
        c = 1
    elif len(array.shape) == 3:
        h, w, c = array.shape
    else:
        raise ValueError(
            f"Shape {array.shape} is not supported. Please use (h, w, c) or (h, w)"
        )
    shape = struct.pack(">III", h, w, c)
    encoded = shape + array.tobytes()
    return encoded


def decode_numpy(bytes: bytes) -> np.ndarray:
    """decode bytes to numpy array. Assumes the original array had uin8 format

    Args:
        bytes (bytes): the bytes

    Returns:
        np.ndarray: the resulting array
    """
    h, w, c = struct.unpack(">III", bytes[:12])
    # Add slicing here, or else the array would differ from the original
    array = np.frombuffer(bytes[12:], dtype=np.uint8).reshape(h, w, c)
    return array


def remove(lst: List, attr: str, value: str) -> Tuple[List, Any]:
    """Removes item from list, where attribute of item matches
    given value.
    Returns updated list and removed item.

    Args:
        lst (List): List of item
        attr (str): attribute, wich should match value
        value (str): value of the given attribute to match

    Returns:
        Tuple[List, Any]: Updated List and removed item
    """
    updated = lst.copy()
    deleted = None
    for i, model in enumerate(lst):
        if getattr(model, attr) == value:
            deleted = updated.pop(i)
    return updated, deleted


def find(lst: List, attr: str, value: str) -> int:
    """Return index of item where given attribute matches value.
    Returns -1 if no item with given attribute exists in list.

    Args:
        lst (List): list
        attr (str): attribute of config which should match.
        value (str): value of given attribute to match

    Returns:
        int: index of config model in list. Returns -1 if it was not found
    """
    for i, dic in enumerate(lst):
        if getattr(dic, attr) == value:
            return i
    return -1


def update_config_list(old: List[AllConfigModel], new: List[AllConfigModel]) -> List:
    """Update old list of config models with list of new config models

    Args:
        old_list List: old list
        new_list List: new list

    Returns:
        List: updated List
    """
    for item in new:
        idx = find(old, "name", item.name)
        if idx != -1:
            old_item = old[idx]
            data = item.model_dump(exclude_unset=True)
            updated_item = old_item.model_copy(update=data)
            old[idx] = updated_item
        else:
            old.append(item)
    return old


def update_config_dict(
    old: Dict[str, List[AllConfigModel]], new: Dict[str, List[AllConfigModel]]
) -> Dict:
    """Update old dict of config models with new dict of config models

    Args:
        old (Dict[str, List[AllConfigModel]]): old dict with configs
        new (Dict[str, List[AllConfigModel]]): new dict with configs

    Returns:
        Dict: updated dict
    """
    for key, new_list in new.items():
        old_list = old[key]
        updated_list = update_config_list(old_list, new_list)
        old[key] = updated_list
    return old


@dataclass
class BBox:
    """Dataclass to represent a bounding box in percentages.
    This helps to draw a bounding box on the same image in different scalings.
    """

    x: float
    y: float
    w: float
    h: float

    def to_pixel(self, img_h: int, img_w: int) -> Tuple[int, int, int, int]:
        """Calculates actual pixel of the bounding box based on the given image
        size.

        Args:
            img_h (int): image width
            img_w (int): image height

        Returns:
            Tuple[int, int, int, int]: (x, y, w, h) in pixel of the given image size
        """
        return (
            int(self.x * img_w),
            int(self.y * img_h),
            int(self.w * img_w),
            int(self.h * img_h),
        )

    @classmethod
    def from_pixel(self, bbox: Tuple[int, int, int, int], img_h: int, img_w: int):
        """Creates a new bounding box representation in percentage of the given
        image width and height.

        Args:
            bbox (Tuple[int, int, int, int]): bounding box with (x, y, w, h) in pixels
            img_h (int): image width
            img_w (int): image height

        Returns:
            _type_: _bounding box in percentages of the given image widht and height.
        """
        return BBox(bbox[0] / img_w, bbox[1] / img_h, bbox[2] / img_w, bbox[3] / img_h)


@dataclass
class Line:
    """Dataclass to represent a line in percentages inside an image.
    This helps to draw a line on the same image in different scalings.
    """

    x1: float
    y1: float
    x2: float
    y2: float

    def to_pixel(self, img_h: int, img_w: int) -> Tuple[int, int, int, int]:
        """Calculates actual pixel of the line based on the given image
        size.

        Args:
            img_h (int): image width
            img_w (int): image height

        Returns:
            Tuple[int, int, int, int]: (x2, y2, x2, y2) in pixel of the given image size
        """
        return (
            int(self.x1 * img_w),
            int(self.y1 * img_h),
            int(self.x2 * img_w),
            int(self.y2 * img_h),
        )

    @classmethod
    def from_pixel(self, line: Tuple[int, int, int, int], img_h: int, img_w: int):
        """Creates a new line representation in percentage of the given
        image width and height.

        Args:
            line (Tuple[int, int, int, int]): line with (x1, y1, x2, y2) in pixels
            img_h (int): image width
            img_w (int): image height

        Returns:
            _type_: _bounding box in percentages of the given image widht and height.
        """
        return Line(line[0] / img_w, line[1] / img_h, line[2] / img_w, line[3] / img_h)
