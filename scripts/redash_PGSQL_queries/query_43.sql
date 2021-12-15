/*
Name: Filters: Min State of Charge
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:23.217Z
*/

select distinct soc_min as a, count(*) from test_metadata group by a order by a