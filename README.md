# 侧线软测量

前后端在这一个目录里。五个底座在 `core_bases`，网页和实时缓存在 `application`，页面在 `frontend`。

## 依赖方向

- `dataset` 不导入其他底座包。
- `mechanism` 只从 `dataset.config` 读系数。
- `predict` 使用 `dataset` 和 `mechanism`。
- `evaluate` 使用 `dataset` 和 `predict`。
- `mining` 只给离线脚本。`application` 不导入它。

## 运行

```bash
python -m venv .venv
.venv/bin/pip install -e . pytest 
.venv/bin/python -m application.ingest
.venv/bin/python -m uvicorn application.main:app --host 127.0.0.1 --port 8780
```

前端：

```bash
cd frontend
npm install
npm run dev
```

验收窗 2026-09-05 至 2026-09-14，2878 点。绿线决定系数 0.29，均方根 0.69。锁温式系数在 `config/product.json`。

工厂原始文件在 `AI揭榜/资料`。`application.ingest` 把能读成表的 csv、xlsx 和文本写入 `data/factory.db`。pdf、压缩包只登记路径。实时点写入 `data/realtime_cache.pkl`，不进入离线快照。

人工复核：机理公式、验收指标、实时数据是否写进快照。
