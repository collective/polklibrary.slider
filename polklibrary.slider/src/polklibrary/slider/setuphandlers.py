# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.dexterity.behaviors import constrains
from Products.CMFCore.utils import getToolByName

def post_install(context):
    """Post install script"""
    #if context.readDataFile('polklibraryslider_default.txt') is None:
    #    return

    print "Running Post Install"
    
    # Add Group plone.app.portlets.ManagePortlets
    # plone.api.group.create(groupname='slider_image_editor', title='Slider Image Editor', description='Can edit and manage slider content')
    
    
    # Add Slider Folder
    site = api.portal.get()
    obj = api.content.create(
                type='Folder',
                title='Slider Images',
                description='This folder contains all the banner sliding images of your site. DO NOT DELETE, MOVE OR RENAME!',
                container=site)
    api.content.transition(obj, 'publish')
    obj.exclude_from_nav = True
  
    
    behavior = ISelectableConstrainTypes(obj)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setLocallyAllowedTypes(('linkable_image',))
    behavior.setImmediatelyAddableTypes(('linkable_image',))
    obj.reindexObject()
    