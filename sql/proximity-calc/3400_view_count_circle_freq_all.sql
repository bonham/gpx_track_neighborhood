drop view if exists count_circle_freq_all;
create view count_circle_freq_all as
SELECT
  circle_id,
  count(num) as num
from (
  select *
  from count_ls
  UNION ALL
  select *
  from count_ml_consecutive
) as unioncount
group by circle_id