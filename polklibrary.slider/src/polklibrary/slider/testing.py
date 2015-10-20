# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import polklibrary.slider


class PolklibrarySliderLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=polklibrary.slider)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'polklibrary.slider:default')


POLKLIBRARY_SLIDER_FIXTURE = PolklibrarySliderLayer()


POLKLIBRARY_SLIDER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POLKLIBRARY_SLIDER_FIXTURE,),
    name='PolklibrarySliderLayer:IntegrationTesting'
)


POLKLIBRARY_SLIDER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(POLKLIBRARY_SLIDER_FIXTURE,),
    name='PolklibrarySliderLayer:FunctionalTesting'
)


POLKLIBRARY_SLIDER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        POLKLIBRARY_SLIDER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PolklibrarySliderLayer:AcceptanceTesting'
)
