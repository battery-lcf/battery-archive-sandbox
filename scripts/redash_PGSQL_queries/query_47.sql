/*
Name: Efficiencies
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:18:50.878Z
*/

SELECT
   key || ': ' || r.cell_id as series,
   r.cycle_index,
   value
FROM (SELECT cell_id, trunc(cycle_index,0) as cycle_index, json_build_object('e_eff', TRUNC(e_eff,3), 'ah_eff', TRUNC(ah_eff,3)) AS line 
FROM cycle_data
where cell_id IN ({{cell_id}}) and ah_eff<1.004) as r
JOIN LATERAL json_each_text(r.line) ON (key ~ '[e,ah]_[eff]')
where cast(value as numeric)>0 
GROUP by r.cell_id, r.cycle_index, json_each_text.key, json_each_text.value
order by r.cell_id,r.cycle_index, key    