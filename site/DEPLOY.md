# 发布指南 / Deployment

本站为纯静态站点（`dist/` 目录），无后端依赖，可部署到任何静态托管。

## 构建

```bash
# 工具链：Node 20+（本工作区已带便携版 tools/node）
cd site
npm install --registry=https://registry.npmmirror.com
npm run build        # 产物在 site/dist/
```

构建前置：`site/public/data/*.json`（由 `python scripts/site/build_data.py` 生成）与
`site/public/images/`（由 `python scripts/site/build_images.py` 生成）。

## 方案 A：Cloudflare Pages（推荐，图多量大）

全站约 4700 个文件 / ~500MB，Cloudflare Pages 免费额度完全覆盖（单文件 25MB、无总容量限制）。

1. 注册/登录 https://dash.cloudflare.com → Workers & Pages → Create → Pages → **Upload assets**
2. 把 `site/dist` 整个目录拖进去 → Deploy
3. 得到 `https://<项目名>.pages.dev` 公网地址（可绑定自定义域名）

## 方案 B：GitHub Pages

全站 ~500MB，低于 GitHub Pages 1GB 建议上限，可用但 push 较慢。

```bash
# 1. 在 GitHub 上新建一个公开空仓库（如 yourname/gfl-db），不要勾选 README
# 2. 本地已配置好 GitHub 凭据（git credential manager / ssh key）后：
bash scripts/site/deploy_ghpages.sh https://github.com/yourname/gfl-db.git
# 3. 仓库 Settings → Pages → Source 选 gh-pages 分支 → / (root)
#    稍等几分钟即上线 https://yourname.github.io/gfl-db/
```

`deploy_ghpages.sh` 会把 `site/dist` 作为 orphan `gh-pages` 分支强推。

## 方案 C：Vercel / Netlify

CLI 一行（需账号登录）：

```bash
npx vercel deploy --prod site/dist
npx netlify deploy --prod --dir site/dist
```

注意：这两个平台免费档对总容量/文件数有限制，500MB 图量建议拆分或选方案 A。

## 本机/局域网预览

```bash
cd site && npx vite preview --port 8823 --host   # 手机同 WiFi 可访问 http://<本机IP>:8823
```

## 注意事项

- 路由使用 hash 模式（`#/dolls/...`），任何静态托管都无需配置回退规则。
- 站点含游戏美术资产，版权属散爆网络 / MICA Team；页面底部已声明非官方与联系方式，请保留。
