# 数据管线（维护者）

这组脚本把游戏资源提取工作区的产物加工成站点数据。**普通贡献者不需要运行它们**——
`site/public/data/*.json` 已入库，直接改 JSON 即可。

## 前置条件

脚本按以下目录布局解析输入（即游戏资源提取工作区）：

```
<工作区>/
  cache/gfwiki/Gun_info_data_*.lua     # gfwiki MediaWiki Lua 数据模块
  cache/texttable_all/*.txt            # assettexttable.ab 导出的 177 张配置表
  manifests/skins.csv                  # 皮肤表
  manifests/portraits_by_name.csv      # 立绘清单（源 PNG 路径）
  extracted/portraits_by_name/         # 立绘 PNG
```

脚本内 `ROOT` 指向上两级目录，因此本目录应放置在工作区的 `scripts/site/` 位置运行，
或自行调整 `ROOT`。

## 用法

```bash
python build_data.py     # join 六源 → site/public/data/*.json（秒级）
python build_images.py   # PNG → WebP（4150 张，约 47 分钟；支持断点续跑）
```

数据源要点（详见上游工作区 docs/findings.md）：

- 技能文本表键格式 `<字段前缀><技能ID><等级2位>`（1=名 2=描述 3=详情）
- gfwiki Lua 的 `mod` 模块（key=20000+id）为 MOD3 满级差量字段，合并后即最终值
- MOD 立绘挂同一 wiki_id、codename 以 `mod` 结尾
