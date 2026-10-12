# dataset

公共数据集底座。读取冻结快照 `official_fru2h_dataset.pkl`，切分来自只读的 xinbao 配置。在线四个标记在 `marks/`。实时缓存不写进快照。

不导入 mechanism、predict、evaluate、mining。
