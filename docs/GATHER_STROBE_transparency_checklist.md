# GATHER/STROBE-Style Transparency Checklist

## Study Design And Data Sources

- [ ] 标题和摘要说明本研究是 GBD 2023 secondary analysis / ecological counterfactual scenario analysis。
- [ ] 报告数据源：GBD 2023 Results Tool / IHME outputs、SDI 数据、Natural Earth basemap、UN WPP 2024 population review data。
- [ ] 说明研究范围：Southeast Asia, East Asia, and Oceania super-region 的 34 个国家/地区，1990-2023，projection to 2050 仅为 scenario analysis。
- [ ] 说明研究对象不是个体队列，不包含 primary patient-level data。
- [ ] 说明伦理审批豁免依据：公开、去标识、聚合数据。

## Case Definition And Outcome Boundaries

- [ ] 明确 outcome 为 GBD NAFLD/MASLD-related cirrhosis and liver cancer burden，不等同于完整现代 MASLD 患病谱。
- [ ] 报告 deaths 和 DALYs 的 measure、metric、age、sex、year、location 筛选。
- [ ] 对 `MASLD` 和 `NAFLD` 命名进行过渡性说明：GBD 2023 数据仍以 NAFLD disease sequelae 为基础，本稿采用 MASLD/NAFLD-related wording。

## Exposure And Counterfactual

- [ ] 明确 high BMI exposure sex gap 的构造来源和年龄范围。
- [ ] 说明 main counterfactual 为 `calibrated exposure-scaling counterfactual`，不是完整 IHME PAF recalculation。
- [ ] 报告 Scenario A：sex-equalized high-BMI exposure。
- [ ] 报告 Scenario B：high BMI at TMREL / theoretical upper bound。
- [ ] 说明 Scenario A 与 Scenario B 是 nested，不可相加。

## Statistical Methods

- [ ] 说明 country-level burden、rates、percentages 的计算公式。
- [ ] 说明 `internal age-standardized rate` 使用内部标准人群，不是 official GBD ASR。
- [ ] 说明 SDI 分析为 descriptive association，不作强因果解释。
- [ ] 说明 high BMI、high FPG、smoking attribution 是 non-additive and non-mutually exclusive。
- [ ] 说明 BAPC projection 的输入、年龄组、人群 proxy、projection period 和主要限制。

## Uncertainty And Sensitivity

- [ ] 分开报告 main proxy interval、summary-UI proxy propagation、RR-PSA、uncapped sensitivity、lean denominator sensitivity。
- [ ] 不使用 `draw-level uncertainty` 或 `statistically significant` 来描述 proxy uncertainty。
- [ ] 报告 Q19 截断规则：excess-risk ratio 大于 1 的 cells 被 capped；uncapped sensitivity 作为边界。
- [ ] 报告 Q20 公式调和和一致性审计。
- [ ] 报告官方 population/future population 复核：2023 内部 proxy 与 WPP 2024 接近；原 2050 internal proxy 明显高于 WPP 中位方案；修订版 Block 5 已用 WPP 2024 population exposure 复跑 2024-2050 future person-years。

## Results Reporting

- [ ] 摘要中给出绝对值和相对值：2023 DALYs 约 2797，占总负担约 0.40%；deaths 约 107，占约 0.41%。
- [ ] 报告 high FPG 在 27/34 国家为主导 risk factor，high BMI 仅 3/34，smoking 4/34。
- [ ] 报告国家异质性时同时给 absolute number 和 rate，避免小岛国绝对数过小导致误读。
- [ ] Figure 1 图注说明颜色为 rate、气泡/条形为 number。
- [ ] Figure 3 图注说明 baseline projection uses UN WPP 2024 population exposure for 2024-2050 future person-years and is not an IHME official forecast。

## Reproducibility

- [ ] 提供数据下载日期、GBD query parameters、UN WPP 2024 文件路径和本地缓存文件名。
- [ ] 提供代码版本、分析脚本、figure manifest、table manifest。
- [ ] 说明所有修订输出存放于 `<active_revision>`，第一版已归档。
