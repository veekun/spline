<%inherit file="base.mako" />

<%def name="title()">Home</%def>

<h1>Updates</h1>
% for update in c.updates:
<%include file="${update.source.template}" args="update=update" />
% endfor
