# 少女前线资料库 GFL DB

![GFL DB](https://yelikour.github.io/gfl-db/images/103_mod_normal.webp)

> 玩家自制、非官方的《少女前线》资料数据库：451 位人形的图鉴、立绘、数值与技能。

**🌐 线上地址：<https://yelikour.github.io/gfl-db/>**

## 功能

- **人形图鉴**：451 位人形，支持枪种（HG / SMG / AR / RF / MG / SG）、稀有度、可否改造、势力筛选，名称 / 代号 / 英文名搜索，多种排序
- **人形详情**：立绘查看（基础 / 破损 / 改造 / 皮肤切换，点击全屏查看）、Lv.100 与 MOD3 满级数值对比、技能 Lv.1 / Lv.10 文本、光环效果、获取途径、画师 / CV / 制造时间、原型枪械资料（英文）
- 纯静态站点：Vue 3 + Vite + TypeScript + naive-ui，hash 路由，可部署到任何静态托管

## 快速开始（本地开发）

```bash
git clone https://github.com/yelikour/gfl-db.git
cd gfl-db

# 立绘图片（约 450MB / 4150 张 WebP）存放在 gh-pages 分支，取回到本地：
git fetch origin gh-pages --depth=1
git archive origin/gh-pages images | tar -x -C site/public

cd site
npm install
npm run dev        # http://localhost:5173
```

> 没有图片也能开发：页面布局与数据全部可用，只是立绘位置显示占位。

## 目录结构

```
site/                     前端（Vue 3 + Vite）
  src/                    页面与路由：Home / DollList / DollDetail / About
  public/data/*.json      站点数据（451 人形，由 pipeline 生成，可直接修改）
  public/images/          立绘 WebP（不入库，从 gh-pages 分支取回）
pipeline/                 数据管线（Python，维护者使用）
  build_data.py           数据源 join → site/public/data/*.json
  build_images.py         立绘 PNG → WebP（缩略图 360w / 全图 1280w）
  lua_table.py            gfwiki Lua 数据模块解析器
  deploy_ghpages.sh       手动部署脚本（增量推送）
.github/workflows/        推送 main 分支自动构建并部署
```

## 数据文件说明

`site/public/data/` 下三个 JSON 是所有页面数据的唯一来源，直接改它们就能生效：

| 文件 | 内容 |
|---|---|
| `index.json` | 图鉴列表（名称、枪种、稀有度、缩略图路径、皮肤数、是否可改造） |
| `dolls.json` | 详情页全量数据（数值、MOD3 数值、技能、皮肤、立绘路径、获取途径等） |
| `meta.json` | 站点统计（数量、覆盖度、数据版本日期） |

## 如何贡献

欢迎 issue 与 PR！可以直接上手的方向：

- **数据勘误**：技能文本、数值、皮肤名对照游戏内实际有出入的，改 `public/data/*.json` 提 PR 即可
- **补全缺失**：约 25 名人形的技能文本不在本地配置表中（详见 About 页），欢迎补录；少数新皮肤暂无立绘
- **前端功能**：编队模拟 / 阵型光环可视化 / 装备数据 / 妖精图鉴 / 收藏夹 / 多语言……有想法就提 issue 讨论
- **样式与体验**：移动端适配、暗色以外的主题、加载性能

**PR 流程**：fork → 新建分支 → 修改 → PR 到 `main`。合并后 GitHub Actions 会自动构建并部署到 GitHub Pages（约 2 分钟生效）。改动只涉及 `public/data/*.json` 或 `src/` 时无需本地构建，CI 会处理。

## 数据管线（维护者）

数值与文本来自两条链路，在游戏资源提取工作区中运行（游戏目录只读）：

1. `gfwiki` MediaWiki Lua 模块（Gun_info_data_*）→ 枪种/稀有度/六维/实装日期/皮肤清单
2. 游戏本地配置表（`assettexttable.ab` 导出的 177 张 txt）→ 中文名/画师 CV/技能文本/原型枪资料
3. 立绘自 Steam 客户端标准 UnityFS bundle 只读提取（UnityPy），皮肤名与立绘目录做 join

```bash
# 在提取工作区（含 cache/ 与 manifests/）中：
python pipeline/build_data.py      # → site/public/data/*.json
python pipeline/build_images.py    # → site/public/images/*.webp（约 47 分钟）
cd site && npm run build
bash pipeline/deploy_ghpages.sh git@github.com:yelikour/gfl-db.git
```

## 部署

- **自动**：推送到 `main` → GitHub Actions 构建（含从 gh-pages 分支取回图片）→ 强推 `gh-pages` 分支 → Pages 生效
- **手动**：`bash pipeline/deploy_ghpages.sh <remote>`（持久 git 目录增量推送，图片未变时秒级完成）

## 版权与致谢

- Girls' Frontline《少女前线》及其全部角色立绘、名称与设定版权归 **散爆网络 / MICA Team** 所有。本站为非官方、非营利的玩家资料站，如版权方认为内容不适宜展示，请联系 [仓库所有者](https://github.com/yelikour) 处理下架。
- 数值与文本数据来源：游戏客户端本地配置表、[gfwiki（少女前线中文维基）](https://gfwiki.org) 公开图鉴数据模块。
- 页面形态参考了 [nikke-db](https://github.com/Nikke-db/nikke-db-vue) 项目（NIKKE 数据库）。
- 站点代码以 [WTFPL](./LICENSE) 发布，可自由使用；游戏资产不在代码许可范围内。
