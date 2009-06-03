<%page args="widget, kwargs"/>
% for priority in [1, 2, 3, 4, 5]:
%    for path in config['spline.plugins.widgets'].get(widget, {}).get(priority, []):
<%include file="${path}" args="kwargs=kwargs"/>
%     endfor
% endfor
