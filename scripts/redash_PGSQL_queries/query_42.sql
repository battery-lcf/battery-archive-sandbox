/*
Name: Filters: Max State of Charge
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:30.461Z
*/

select distinct soc_max as a, count(*) from test_metadata group by a order by a