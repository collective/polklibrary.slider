

var PolkSlider = function(id) {

    $(id).attr('data-loaded','1');
    
    var obj = {

        _first_starting: true,
        _portlet : null,
        _container : null,
        _dots : null,
        _speed : 5,
        _transition : 'fade',
        _random_start : false,
        _show_title : false,
        _show_description : false,
        _show_dots : false,
        _show_arrows : false,
        _INDEX_MAX : 0,
        _index : 0,
        _thread : null,

        init : function() {
            this._portlet = $(id);
            this._container = this._portlet.find('.pl-slider-container');
            this.load_resources(); // Prep targets _portlet and _container first
            this._dots = this._container.find('.dots');
            this._speed = parseInt(this._container.attr('data-speed'));
            this._random_start = Boolean(parseInt(this._container.attr('data-randomstart')));
            this._show_title = Boolean(parseInt(this._container.attr('data-showtitle')));
            this._show_description = Boolean(parseInt(this._container.attr('data-showdescription')));
            this._show_dots = Boolean(parseInt(this._container.attr('data-showdots')));
            this._show_arrows = Boolean(parseInt(this._container.attr('data-showarrows')));
            this.set_transition(parseInt(this._container.attr('data-transitions')));
            this._INDEX_MAX = this._container.find('img').length;
            
            if (this._random_start)
                this._index = Math.floor((Math.random() * this._INDEX_MAX)); 
            
            if (this._INDEX_MAX > 1 && this._transition != 'nothing') {
                if (this._show_dots)
                    this.build_dots();
                if (this._show_arrows)
                    this.build_arrows();
                this.rotate_process();
            }
            else {
                this.show_image();
            }
            
            this.build_links();
            this.build_editor();
        },
        
        root_url : function() {
            var url = $('body').attr('data-portal-url');
            
            if (url == '' || url == null) {
                proto = 'http://';
                if(document.location.protocal == 'https:')
                    proto = 'https://';
                url = proto + document.location.host + document.location.pathname;
            }
            return url;
            
        },
        
        build_links : function() {
            this._container.find('img.pl-slide-image').mouseup(function(e){
                var url = $(this).attr('data-href');
                if (typeof url !== 'undefined')
                    if(e.which === 1) 
                        document.location.href = url;
                    else if(e.which === 2) 
                        window.open(url, '_blank');
            });
        },
        
        build_editor : function() {
            var self = this;
            self._container.find('span.pl-slide-load').click(function(){
                $('.pl-slide-load-zone .pl-slide-content').empty();
                $('.pl-slide-load-zone').hide();
                var option = this;
                self._container.find('.pl-slide-load-zone .pl-slide-content').load( $(option).attr('data-src') + ' #content-core form' , function(){
                
                    self._container.find('.pl-slide-load-zone .pl-slide-label').html($(option).attr('title'));
                    self._container.find('.pl-slide-load-zone').slideDown();
                    
                    // Setup referer
                    if(self._container.find('.pl-slide-load-zone form input[name="referer"]').val() == '') 
                        self._container.find('.pl-slide-load-zone form input[name="referer"]').remove();
                    var referer = $('<input>').attr({'name':'referer','type':'hidden'}).val(document.location.href);
                    self._container.find('.pl-slide-load-zone form').append(referer);
                    
                    // Handle the Save
                    self._container.find('#pl-slide-load-zone form').submit(function(e){
                        e.preventDefault(); //prevent submit
                        var referer = $(this).find('input[name="referer"]').val();
                        var data = $(this).serializeArray();
                        data.push({'name': self._container.find('input[value="Save"]').attr('name'), 'value': self._container.find('input[value="Save"]').val() })
                        data.push({'name': self._container.find('input[value="Cancel"]').attr('name'), 'value': self._container.find('input[value="Cancel"]').val() })
                        $.post($(this).attr('action'), data, function() {
                            window.location = referer;
                        });
                        
                        $.ajax({
                            url: $(this).attr('action'),
                            data: data,
                            cache: false,
                            contentType: false,
                            processData: false,
                            type: 'POST',
                            success: function(data){
                                alert(data);
                            }
                        });
                    });
                    
                    // Handle the Cancel
                    self._container.find('#form-buttons-cancel_add, #form-buttons-cancel').click(function(e){
                        e.preventDefault();
                        self._container.find('.pl-slide-load-zone .pl-slide-content').empty();
                        self._container.find('.pl-slide-load-zone').hide();
                    });
                    
                    // file upload handler
                    self._container.find('.pl-slide-fileUpload input').change(function(){
                        if ($(this).val() != '') {
                            $('.pl-slide-fileUpload').addClass('has-file');
                            $('.pl-slide-fileUpload > div').html('Ready to upload files');
                        }
                    });
                    
                    // sortable handler
                    self._container.find('.pl-slide-sortable').sortable({'stop':function(){
                        $(this).find('li').each(function(i,t){
                            $(t).find('input[type="hidden"]').val(i);
                        });
                    }});    
                    self._container.find('.pl-slide-sortable').disableSelection();
                        
                    // show or not
                    self._container.find('ul li input[type="checkbox"]').change(function(){
                        if ($(this).is(':checked')) {
                            $(this).parents('li').detach().appendTo(self._container.find('ul.pl-slide-sortable'));
                        }    
                        else {
                            $(this).parents('li').detach().appendTo(self._container.find('ul.pl-slide-static'));
                        }
                        self._container.find('.pl-slide-static li input[type="checkbox"]').prop('checked',false).removeAttr('checked', false);
                        self._container.find('.pl-slide-sortable').sortable('refresh');
                        self._container.find('.pl-slide-sortable').find('li').each(function(i,t){
                            $(t).find('input[type="hidden"]').val(i);
                        });
                    });
                    
                    // show more images
                    self._container.find('.pl-slide-static-open').click(function(){
                        self._container.find('.pl-slide-static').slideToggle();
                    });
                    
                    // Rebind in case other links exist from the load
                    self._container.find('.pl-slide-edit span.pl-slide-load').unbind('click');
                    self.build_editor();
                });
            });
        },
        
        build_arrows : function() {
            var self = this;
            self._container.hover(
                function(){
                    self._container.find('.pl-slide-left, .pl-slide-right').show();
                },
                function(){
                    self._container.find('.pl-slide-left, .pl-slide-right').hide();
                }
            );
            
            self._container.find('.pl-slide-left').click(function(){
                self._index = (self._index + self._INDEX_MAX - 1) % self._INDEX_MAX;
                self.rotate_process();
            });
            self._container.find('.pl-slide-right').click(function(){
                self._index =(self._index + 1) % self._INDEX_MAX;
                self.rotate_process();
            });
        },
        
        build_dots : function() {
            var self = this;
            for (var i = 0; i < this._INDEX_MAX; i++) {
                var span = $('<span>').attr('data-index', i).html('&#x2022').click(function() {
                    var index_clicked = parseInt($(this).attr('data-index'));
                    if (index_clicked != self._index){
                        self._index = index_clicked;
                        self.rotate_process();
                    }
                });
                this._dots.append(span);
            }
        },
        
        show_image : function() {
            var self = this;
            var img = this._container.find('img.pl-slide-image').get(this._index);
            this._dots.find('span').removeClass('active');
            $(this._dots.find('span').get(this._index)).addClass('active');
             
            // Handle Transition Out's
            this._container.find('img.pl-slide-image').css('position','absolute').stop(true,true).fadeOut(1000);
            this._container.find('.pl-slide-text').hide();
            
            if(this._first_starting) {
                $(img).stop(true,true).show(); // show now at startup
                this._first_starting = false;
            }
            
            // Supply Title and Description Info
            if (this._show_title)
                this._container.find('.pl-slide-title').html($(img).attr('alt'));
            if (this._show_description)
                this._container.find('.pl-slide-description').html($(img).attr('title'));
            
            // Handle Transition In's
            if (this._transition == 'fade') {
                $(img).css('position','relative').fadeIn(500).css("display","block");;
                if (this._show_title || this._show_description)
                    this._container.find('.pl-slide-text').fadeIn(500).css("display","block");;
            }
            else if (this._transition == 'nothing') {
                $(img).css({'position':'relative','display':'block'}).show();
            }
            else if (this._transition == 'slide') {
                $(img).css({
                    'display':'block',
                    'position':'relative',
                    'opacity':'0',
                    'left':'-200px',
                }).stop(true,true).animate({
                    opacity: 1,
                    left: '+=200px'
                }, 500);
                if (this._show_title || this._show_description)
                    this._container.find('.pl-slide-text').fadeIn(500);
            }
            
            // Set Height Off Container When Image Loads
            // $(img).on('load', function(){
                // console.log('loaded: ' + $(img).height() );
                // $(self._container).css('height', $(img).height());
            // }).on('error', function() { 
                // console.log('error: ' + $(img).height() );
                // $(self._container).css('height', '150px');
            // });
                   
        },
        
        rotate_process : function() {
            var self = this;
            clearInterval(this._thread);
            this._thread = null;
            this.show_image();
            this._thread = setInterval(function(){
                self._index++;
                if (self._index >= self._INDEX_MAX)
                    self._index = 0;
                self.show_image();
            },
            this._speed*1000);
        },
        
        load_resources : function() {
            // Load Files
            if (typeof $.fn.sortable === 'undefined') {
                $('head').append($('<script>').attr({'name': 'text/javascript', 'src': this.root_url() + '/++resource++polklibraryslider/jquery-ui-1.9.2.custom.min.js'}));
            }
            
            // Load Images
            var self = this;
            self._container.find("img.pl-slide-image").one("load", function() {
                self._container.removeClass('pl-loading');
            }).each(function() {
              if(this.complete) $(this).load();
            });
            
            // Add 
            this._container.find('.pl-loading').css('background-url', 'url(' + this.root_url() + '/++resource++polklibraryslider/loading.gif)');
        },
        
        set_transition : function(i) {
            if (i == 0)
                this._transition = 'fade';
            else if (i == 1)
                this._transition = 'slide';
            else if (i == 2)
                this._transition = 'nothing';
        }
        
    }
    
    obj.init();
    return obj;
}

var PolkSliderLoad = function() {
    // Not the hottest function, but can trigger it immediately once the html is ready on the slider.
    $('.portletSlider').each(function(i,t){
        if($(t).attr('data-loaded') == '0')
            window['PolkSlider' + i] = PolkSlider(t);
    });
}

