/*
Name: Filters: C Discharge Rate
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:46.265Z
*/

select distinct crate_d as a, count(*) from test_metadata group by a order by a