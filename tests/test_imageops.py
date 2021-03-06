"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from unittest import TestCase
from parsing import imageops
from PIL import Image
from utils.directories import get_assets_directory
from os import path


class TestImageOps(TestCase):
    def setUp(self):
        self.image = Image.open(path.join(get_assets_directory(), "vision", "test.png"))

    def test_image_similarity(self):
        result = imageops.get_similarity(self.image, self.image)
        self.assertEqual(result, 100.0)

    def test_pixel_similarity(self):
        pixels = [
            (100, (255, 255, 255), (255, 255, 255)),
            (67, (255, 0, 0), (0, 0, 0)),
            (93, (255, 255, 200), (255, 255, 255))
        ]
        for expected, pixel1, pixel2 in pixels:
            result = imageops.get_similarity_pixels(pixel1, pixel2)
            self.assertAlmostEqual(round(result, 0), expected)

    def test_brightest_pixel(self):
        result = imageops.get_brightest_pixel(self.image)
        self.assertIsInstance(result, tuple)

    def test_brightest_pixel_loc(self):
        result = imageops.get_brightest_pixel_loc(self.image)
        self.assertIsInstance(result, tuple)

    def test_brightest_pixel_cl(self):
        result = imageops.get_brightest_pixel_cl(self.image)
        self.assertIsInstance(result, tuple)

    def test_image_similarity_transparent(self):
        template = Image.open(path.join(get_assets_directory(), "vision", "pointer.png"))
        to_match = Image.open(path.join(get_assets_directory(), "vision", "test_pointer.png"))
        r = imageops.get_similarity_transparent(template, to_match)
        print("[TestImageOps] Result: {}".format(r))
