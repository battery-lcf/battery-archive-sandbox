/*
Name: Cycle Data
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:20:24.273Z
*/

SELECT KEY || ': ' || r.cell_id AS series,
              r.cycle_index,
              r.test_time,
              value
FROM
  (SELECT cell_id,
          trunc(cycle_index,0) AS cycle_index,
          test_time,
          json_build_object('e_d', round(e_d,3), 'ah_d', round(ah_d,3)) AS line
   FROM cycle_data
   WHERE cell_id IN ({{cell_id}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[e,ah]_[d]')
WHERE cast(value AS numeric)!=0
GROUP BY r.cell_id,
         r.cycle_index,
         r.test_time,
         json_each_text.key,
         json_each_text.value
ORDER BY r.cell_id,
         r.cycle_index,
         KEY
