from operator import itemgetter
from plone import api  
     

def unparse_images(images):
    try:
        data_string = ''
        for image in images:
            data_string += image['image_path'] + '|'
            data_string += image['restriction_path'] + '|'
            data_string += image['index'] + '\n'
        return data_string
    except Exception as e:
        return data_string    
        
        
def parse_images(data):
    try:
        images = filter(lambda x: x, data.show_images.replace('\r','').replace(' ','').split('\n'))
        content = []
        for image in images:
            sections = image.split('|')
            content.append({
                'image_path':sections[0],
                'restriction_path':sections[1],
                'index':sections[2],
            })
        return content
    except Exception as e:
        return []
        

def get_restricted_images(portal, context, data):
    slider_images = api.content.get(path='/' + portal.id + '/' + data.folder_id)
    default_page = '$missing$'
    if context.getDefaultPage():
        default_page = context.getDefaultPage()
    path = context.absolute_url_path()
    if default_page:
        path = context.absolute_url_path().replace('/' + default_page, '')

    path_restriction = ''
    images = sorted(parse_images(data), key=itemgetter('restriction_path'), reverse=True)
    for image in images:
        if path.startswith(image['restriction_path']): 
            path_restriction = image['restriction_path']
            break
            
    image_paths = filter(lambda x: x['restriction_path'] == path_restriction, images)

    restricted_images = []
    for image_path in sorted(image_paths, key=itemgetter('index')):
        restricted_images = restricted_images + [ i for i in api.content.find(context=slider_images, portal_type='linkable_image', path={'query':image_path['image_path']})]
    
    return restricted_images
    
    
    
    
    