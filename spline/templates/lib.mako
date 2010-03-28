<%def name="cache_content()"><%
    # This is set in spline.lib.base
    c._cache_me(context, caller)
%></%def>

<%def name="field(name, **render_args)">
    <dt>${c.form[name].label() | n}</dt>
    <dd>${c.form[name](**render_args) | n}</dd>
    % for error in c.form[name].errors:
    <dd class="error">${error}</dd>
    % endfor
</%def>

<%def name="escape_html()" filter="h">${caller.body()}</%def>
