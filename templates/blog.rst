<%!
    import calendar
%>
% for year, months in blogtree.items():
${year}
${''.join('#' for _ in range(len(str(year))))}

% for month, postmetas in months.items():
${calendar.month_name[month]}
${''.join('=' for _ in range(len(calendar.month_name[month])))}

% for postmeta in postmetas:
    - `${postmeta['title']}`_
% endfor

% for postmeta in postmetas:
.. _`${postmeta['title']}`: ${postmeta['buildpath'].replace('_build', '')}
% endfor

% endfor

% endfor
