INSERT INTO oxy_con.jobs (target, url, query, domain, parse, geo_location) VALUES
    ('google_search', null, 'nearest pub', 'lt', 0, 'Vilnius, Lithuania'),
    ('google_search', null, 'nearest pub', 'lt', 1, 'Vilnius, Lithuania'),
    ('google_search', null, 'nearest pub', 'co.uk', 0, 'London,United Kingdom'),
    ('google_search', null, 'nearest pub', 'co.uk', 1, 'London,United Kingdom'),
    ('google', 'https://www.google.lt/search?q=what+is+42', null, null, 0, null),
    ('universal', 'https://en.wikipedia.org/wiki/42_(number)', null, null, 0, null),
    ('universal', 'https://en.wikipedia.org/wiki/42_(number)', null, null, 0, null);
