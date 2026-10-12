# 离线试验

本目录不放可被在线服务导入的代码。

原先 `phase3_delta_2h` 下的训练脚本、以及仓库根的 gnn、path_a、path_b、multi_horizon，仍留在 `single_tower_slot`。新服务的启动路径不把那个仓库加进在线导入，也不读取那些脚本。

三个实验预报文件只读：`xgb_lock_feature_pred.pkl`、`xgb_resid_on_lock_pred.pkl`、`xgb_resid_sim_pid_pred.pkl`。验收预报 `regime_daily_pred.pkl` 不在这里重写。
