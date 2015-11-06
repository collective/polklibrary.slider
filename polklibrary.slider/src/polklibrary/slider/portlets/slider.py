from AccessControl import getSecurityManager
from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from polklibrary.slider.browser.utility import get_restricted_images
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.security import checkPermission


yesno = SimpleVocabulary([
    SimpleVocabulary.createTerm(0, '0', u'No'),
    SimpleVocabulary.createTerm(1, '1', u'Yes'),
])

transitions = SimpleVocabulary([
    SimpleVocabulary.createTerm(0, '0', u'Fade'),
    SimpleVocabulary.createTerm(1, '1', u'Slide'),
    SimpleVocabulary.createTerm(2, '2', u'No Transition'),
])

class ISlider(IPortletDataProvider):

    show_transitions = schema.Choice(title=u"Image Transitions?",
                                   vocabulary=transitions,
                                   required=True,
                                   default=0)
                                   
    random_start = schema.Choice(title=u"Pick random image to start with?",
                                   vocabulary=yesno,
                                   required=True,
                                   default=0)
                                   
    show_title = schema.Choice(title=u"Show Image Title?",
                                   vocabulary=yesno,
                                   required=True,
                                   default=0)
                                   
    show_description = schema.Choice(title=u"Show Image Description?",
                                   vocabulary=yesno,
                                   required=True,
                                   default=0)
                
    show_dots = schema.Choice(title=u"Show Image Dots?",
                                   vocabulary=yesno,
                                   required=True,
                                   default=1)
                
    show_arrows = schema.Choice(title=u"Show Image Arrows?",
                                   vocabulary=yesno,
                                   required=True,
                                   default=0)
                
    transition_time = schema.Int(title=u"Seconds between transitions?",
                               description=u"Please specify an integer.", 
                               required=True, 
                               default=30)
    
    folder_id = schema.TextLine(title=u"ADVANCED: Folder Storage ID",
                                         description=u"Do not change unless the main folder is moved or renamed",
                                         required=True,
                                         default=u"slider-images")

    show_images = schema.Text(title=u"ADVANCED: List of images to show",
                                         description=u"Do not change",
                                         required=False,
                                         default=u"")

class Assignment(base.Assignment):
    """ Portlet assignment. This is what is actually managed through the portlets UI and associated with columns. """

    implements(ISlider)

    def __init__(self,**kwargs):
        self.show_transitions = kwargs.get('show_transitions',0)
        self.random_start = kwargs.get('random_start',0)
        self.show_title = kwargs.get('show_title',0)
        self.show_description = kwargs.get('show_description',0)
        self.show_dots = kwargs.get('show_dots',1)
        self.show_arrows = kwargs.get('show_arrows',0)
        self.transition_time = kwargs.get('transition_time', 30)
        self.folder_id = kwargs.get('folder_id', 'slider-images')
        self.show_images = kwargs.get('show_images', '')
        
    @property
    def title(self):
        return u'Banner Slider'


class Renderer(base.Renderer):
    """ View class """

    _template = ViewPageTemplateFile('slider.pt')
   
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        
    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())        

    def slider_editor_permission(self):
        membership = api.portal.get_tool('portal_membership')
        return bool(membership.checkPermission('Portlets: Manage portlets', self.context))
        
    def get_images(self):
        return get_restricted_images(self.portal, self.context, self.data)

    def portlet_manager(self):
        return self.__portlet_metadata__["manager"]
        
    def portlet_name(self):
        return self.__portlet_metadata__["name"]
        
    def portlet_key(self):
        return self.__portlet_metadata__["key"]
        
    def get_cssclass_no_images(self):
        if self.data.show_images:
            if self.data.show_images.replace(' ','') != '':
                return ''
        return 'pl-slider-empty'
        
    @property
    def _data(self):
        return self.data

    @property
    @memoize
    def portal(self):
        return api.portal.get()

class AddForm(base.AddForm):
    """ Portlet add form. """
    schema = ISlider
    form_fields = form.Fields(ISlider) #backwards to plone 4
    label = u'Add Slider'
    description = u'Add Slider Desc'

    def create(self, data):
        return Assignment(
            show_transitions=data.get('show_transitions', 0),
            random_start=data.get('random_start', 0),
            show_title=data.get('show_title', 0),
            show_description=data.get('show_description', 0),
            show_dots=data.get('show_dots', 1),
            show_arrows=data.get('show_arrows', 0),
            transition_time=data.get('transition_time', 30),
            folder_id=data.get('folder_id', '/slider-images'),
            show_images=data.get('show_images', ''),
            )


class EditForm(base.EditForm):
    """ Portlet edit form. """
    schema = ISlider
    form_fields = form.Fields(ISlider) #backwards to plone 4
    label = u'Edit Slider'
    description = u'Edit Slider Desc'
    
    