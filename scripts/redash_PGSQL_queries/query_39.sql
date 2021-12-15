/*
Name: Filters: C charge Rate
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:55.071Z
*/

select distinct crate_c as a, count(*) from test_metadata group by a order by a