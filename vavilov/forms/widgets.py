from os.path import join

from django.conf import settings
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


# from django.utils.encoding import force_unicode
class AutocompleteTextInput(TextInput):
    '''A text input that autocompletes getting a json list'''
    class Media:
        'The css and javascript files required by this widget'
        base_url = settings.STATIC_URL
        # TODO add join url
        css = {'all': (join(base_url, 'style/base/jquery.ui.all.css'),
                       join(base_url, 'style/autocomplete_ui/autocomplete.css'),
                       )}

    def __init__(self, attrs=None, source=None, min_length=3,
                 result_limit=100, force_check=True):
        '''It inits the widget.

        A source url for the json list should be given.
        '''
        super(TextInput, self).__init__(attrs)
        if source is None:
            raise ValueError('A source url should be given')
        self.source = source
        self.min_length = int(min_length)
        self.result_limit = result_limit
        self.force_check = force_check

    def render(self, name, value, attrs=None):
        'It renders the html and the javascript'
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            # final_attrs['value'] = force_unicode(self._format_value(value))
            final_attrs['value'] = self._format_value(value)
        html = u'<input%s />' % flatatt(final_attrs)
        javascript = self.render_js(attrs['id'])
        return mark_safe(html + javascript)

    def render_js(self, field_id):
        'The javascript that does the autocomplete'
# var $j = JQuery.noConflict(true);
        javascript_no_force_check = u'''<script type="text/javascript">

j(function() {
j("#%(field_id)s").autocomplete({
    source:"%(source)s?limit=%(limit)s",
    minLength: %(min_length)i,
    focus: function( event, ui ) {
         event.preventDefault();
        j("#%(field_id)s").val(ui.item.label)
        },
    select: function( event, ui ) {
         event.preventDefault();
        j('#%(field_id)s_result').val(ui.item.value);
        j("#%(field_id)s").val(ui.item.label)
        },
    })
});
</script>
'''
        javascript_force_check = u'''<script type="text/javascript">

j.expr[':'].textEquals = function (a, i, m) {
  return j(a).text().match("^" + m[3] + "j");
};
j(function() {
  j("#%(field_id)s").autocomplete({
    source:"%(source)s?limit=%(limit)s",
    minLength: %(min_length)i,
    focus: function( event, ui ) {
         event.preventDefault();
        j("#%(field_id)s").val(ui.item.label)
        },
    select: function( event, ui ) {
         event.preventDefault();
        j('#%(field_id)s_result').val(ui.item.value);
        j("#%(field_id)s").val(ui.item.label)
        },
    change: function(event, ui) {
      // if the value of the textbox does not match a suggestion, clear the
      // textbox and the pk
      if (j(".ui-autocomplete li:textEquals('" + j(this).val() + "')").size() == 0) {
         j(this).val('');
      }
    },
  })

});
</script>
'''
        if not self.force_check:
            javascript = javascript_no_force_check
        else:
            javascript = javascript_force_check

        javascript %= {'field_id': field_id, 'source': self.source,
                       'min_length': self.min_length,
                       'limit': self.result_limit}
        return javascript


# from django.utils.encoding import force_unicode
class AutocompleteTextMultiInput(TextInput):
    '''A text input that autocompletes getting a json list'''
    class Media:
        'The css and javascript files required by this widget'
        base_url = settings.STATIC_URL
        # TODO add join url
        css = {'all': (join(base_url, 'style/base/jquery.ui.all.css'),
                       join(base_url, 'style/autocomplete_ui/autocomplete.css'),
                       )}

    def __init__(self, attrs=None, source=None, min_length=3,
                 result_limit=100, force_check=True):
        '''It inits the widget.

        A source url for the json list should be given.
        '''
        super(TextInput, self).__init__(attrs)
        if source is None:
            raise ValueError('A source url should be given')
        self.source = source
        self.min_length = int(min_length)
        self.result_limit = result_limit
        self.force_check = force_check

    def render(self, name, value, attrs=None):
        'It renders the html and the javascript'
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            # final_attrs['value'] = force_unicode(self._format_value(value))
            final_attrs['value'] = self._format_value(value)
        html = u'<input%s />' % flatatt(final_attrs)
        javascript = self.render_js(attrs['id'])
        return mark_safe(html + javascript)

    def render_js(self, field_id):
        'The javascript that does the autocomplete'
        javascript = '''<script>
  j( function() {
    function split( val ) {
      return val.split( /,\s*/ );
    }
    function extractLast( term ) {
      return split( term ).pop();
    }

    j( "#%(field_id)s" )
      // don't navigate away from the field on tab when selecting an item
      .on( "keydown", function( event ) {
        if ( event.keyCode === j.ui.keyCode.TAB &&
            $( this ).autocomplete( "instance" ).menu.active ) {
          event.preventDefault();
        }
      })
      .autocomplete({
        minLength: %(min_length)i,
        source: function( request, response ) {
          j.getJSON( "%(source)s?limit=%(limit)s", {
            term: extractLast( request.term )
          }, response );
        },
        search: function() {
          // custom minLength
          var term = extractLast( this.value );
          if ( term.length < 2 ) {
            return false;
          }
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function( event, ui ) {
          var terms = split( this.value );
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push( ui.item.value );
          // add placeholder to get the comma-and-space at the end
          terms.push( "" );
          this.value = terms.join( ", " );
          return false;
        }
      });
  } );
  </script>
      '''
        javascript %= {'field_id': field_id, 'source': self.source,
                       'min_length': self.min_length,
                       'limit': self.result_limit}
        return javascript
