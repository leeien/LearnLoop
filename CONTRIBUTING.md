# 贡献指南

感谢你关注 LearnLoop。提交前请先阅读以下边界，避免破坏学习闭环、数据隔离或可审计性。

## 提交问题

请说明预期行为、实际行为、复现步骤、运行环境和相关截图或日志。不要在问题单中粘贴 API Key、访问令牌、完整 Memory 内容或未脱敏的学习数据。

## 提交改动

1. 保持 React 前端、FastAPI API、领域服务与 Agent 层的职责边界。
2. 涉及 API、数据模型、Agent 行为或 Memory MCP 工具时，补充对应测试和 README 说明。
3. 不要将接口密钥、数据库、向量数据、构建产物或用户学习资料提交到仓库。
4. 提交前运行以下检查：

```powershell
cd backend
python -m unittest discover -s tests -v

cd ../frontend
npm run build
```

## 许可证与行为准则

当前仓库尚未声明开源许可证。提交代码前，请确保你拥有贡献内容的权利；在正式添加 `LICENSE` 前，不要假设代码可被再分发或商用。
