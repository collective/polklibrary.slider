
from plone import api
from plone.namedfile.file import NamedBlobImage
from polklibrary.slider.browser.utility import parse_images, unparse_images, get_restricted_images, get_restricted_path
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, getMultiAdapter
import random


from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignable
from polklibrary.slider.portlets.slider import ISlider
from plone.portlets.interfaces import IPortletRetriever

class Slider(BrowserView):

    template = ViewPageTemplateFile("slider.pt")
    SAFE_EXTENSIONS = ['.jpg','.png','.gif','.jpeg']
    default_page = '$missing$'
    
    def __call__(self):
        self.id = self.request.form.get('id','')
        self.portlet_manager = self.request.form.get('manager','')
        self.portlet_name = self.request.form.get('name','')
        self.portlet_key = self.request.form.get('key','')
        
        if self.context.getDefaultPage():
            self.default_page = self.context.getDefaultPage()
        self.raw_absolute_url = self.context.absolute_url().replace('/' + self.default_page, '')
        
        #context_path = self.context.absolute_url_path().replace('/' + self.default_page, '')
        
        
        if 'form.buttons.apply' in self.request.form:
            # Ordering
            images = [ {} for i in self.request.form]
            for arg in sorted(self.request.form):
                if arg.startswith('form.index.'):
                    i = int(arg.split('.').pop())
                    images[i]['index'] = self.request.form.get(arg)
                if arg.startswith('form.active.'):
                    i = int(arg.split('.').pop())
                    images[i]['image_path'] = self.request.form.get(arg)
                    images[i]['restriction_path'] = get_restricted_path(self.context, self.request)
            images = filter(lambda x: x, images)
            images = filter(lambda x: 'restriction_path' in x, images)
            
            # Upload Files
            files = self.request.form.get('files', [])
            if not isinstance(files, list) and files:
                files = [files]
            for file in files:
                filename = safe_unicode(file.filename)
                data = file.read()
                img_obj = api.content.create(type='linkable_image',
                                             title=filename,
                                             container=self.slider_folder)
                wrapped_data = NamedBlobImage(data=data, filename=filename)
                img_obj.image = wrapped_data
                api.content.transition(img_obj, 'publish')
                img_obj.reindexObject()
            
                # Add to existing images
                images.append({})
                i = len(images)-1
                images[i]['index'] = str(i)
                images[i]['image_path'] = img_obj.absolute_url_path()
                images[i]['restriction_path'] = get_restricted_path(self.context, self.request)
                
            self.save_content(images)
            
            
        if 'referer' in self.request.form:
            self.request.response.redirect(self.request.form.get('referer'))
            
        return self.template()

        
    def save_content(self, incoming_image_data):
        #context_path = self.context.absolute_url_path().replace('/' + self.default_page, '')
        all_image_data = parse_images(self.portlet.data)
        keep_image_data = filter(lambda x: x['restriction_path'] != get_restricted_path(self.context, self.request), all_image_data)
        self.portlet.data.show_images = unparse_images(keep_image_data + incoming_image_data)
        
    @property
    def slider_folder(self):
        return api.content.get(path='/' + self.portal.id + '/' + self.id)
    
    def get_images(self):
        return get_restricted_images(self.portal, self.context, self.portlet.data)
        
    def get_organized_images(self):
        restricted_images = self.get_images()
        all_images = api.content.find(context=self.slider_folder, portal_type='linkable_image')
        for restricted in restricted_images:
            all_images = filter(lambda x: x.getPath() != restricted.getPath(), all_images)
        return {
            'restricted': restricted_images,
            'others': all_images,
        }
        
    @property
    def portlet(self):
        manager = getUtility(IPortletManager, name=self.portlet_manager)
        retriever = getMultiAdapter((self.context, manager), IPortletRetriever)
        for assignment in retriever.getPortlets():
            if assignment["name"] == self.portlet_name and assignment["key"] == self.portlet_key:
                return assignment["assignment"]
        return None
        
    @property
    def portal(self):
        return api.portal.get()
