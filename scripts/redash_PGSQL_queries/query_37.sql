/*
Name: Filters: Form Factor
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:20:08.440Z
*/

select distinct form_factor as a, count(*) from cell_metadata group by a order by a