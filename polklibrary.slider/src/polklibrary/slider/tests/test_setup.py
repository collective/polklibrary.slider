# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from polklibrary.slider.testing import POLKLIBRARY_SLIDER_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that polklibrary.slider is properly installed."""

    layer = POLKLIBRARY_SLIDER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if polklibrary.slider is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('polklibrary.slider'))

    def test_browserlayer(self):
        """Test that IPolklibrarySliderLayer is registered."""
        from polklibrary.slider.interfaces import IPolklibrarySliderLayer
        from plone.browserlayer import utils
        self.assertIn(IPolklibrarySliderLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = POLKLIBRARY_SLIDER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['polklibrary.slider'])

    def test_product_uninstalled(self):
        """Test if polklibrary.slider is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('polklibrary.slider'))
