<%!
    import calendar
%>
% for year, months in blogtree.items():
${year}
${''.join('#' for _ in range(len(str(year))))}

% for month, posts in months.items():
${calendar.month_name[month]}
${''.join('=' for _ in range(len(calendar.month_name[month])))}

% for post in posts:
    - `${post['title']}`_
% endfor

% for post in posts:
.. _`${post['title']}`: ${post['path']}
% endfor

% endfor

% endfor
