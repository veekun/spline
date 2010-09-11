<%def name="cache_content()"><%
    # This is set in spline.lib.base
    c._cache_me(context, caller)
%></%def>

<%def name="field(name, form=None, **render_args)">
<% form = form or c.form %>\
    <dt>${form[name].label() | n}</dt>
    <dd>${form[name](id=u'', **render_args) | n}</dd>
    % for error in form[name].errors:
    <dd class="error">${error}</dd>
    % endfor
</%def>

<%def name="bare_field(name, form=None, **render_args)">
<% form = form or c.form %>\
    ${form[name](id=u'', **render_args) | n}
    % for error in form[name].errors:
    <p class="error">${error}</p>
    % endfor
</%def>

<%def name="escape_html()" filter="h">${caller.body()}</%def>
