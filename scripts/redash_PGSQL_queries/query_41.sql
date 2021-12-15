/*
Name: Filters: Cathode
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:37.931Z
*/

select distinct cathode as a, count(*) from cell_metadata group by a order by a