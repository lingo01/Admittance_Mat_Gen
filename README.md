# Admittance_Mat_Gen

## 简介 | Introduction

`Admittance_Mat_Gen` 是一个用于从 CloudPSS 平台潮流计算结果中生成系统导纳矩阵 `Ybus` 的 Python 工具。该工具会调用 CloudPSS 模型中的潮流计算任务，解析计算结果中导出的 IEEE Common Data Format（CDF）文件及其映射关系文件，将 CDF 数据转换为 MATPOWER MPC 格式，再通过 pandapower 计算系统导纳矩阵。

`Admittance_Mat_Gen` is a Python tool for generating the system admittance matrix `Ybus` from CloudPSS power-flow results. It runs a power-flow job on a CloudPSS model, extracts IEEE Common Data Format (CDF) files and mapping data from the result messages, converts the CDF content into a MATPOWER MPC-style case, and computes `Ybus` through pandapower.

The main callable interface is:

```python
from func_generate_admittance_matrix import func_generate_admittance_matrix

Ybus, cdf_map = func_generate_admittance_matrix(
    project_name="IEEE39",
    area_name="area1",
)
```

The command line interface is only an additional wrapper around the same function.

<br />

## 免责声明 | Disclaimer

本代码及相关文档仅供学术研究与技术交流使用。使用者应自行确认 CloudPSS 模型、潮流计算任务、导出数据、网络环境及本地依赖版本是否满足要求。因使用本代码所引发的任何直接或间接损失、故障、数据泄露、法律责任或其他后果，作者概不负责。

This code and its related documentation are provided solely for academic research and technical exchange. Users are responsible for verifying the CloudPSS model, power-flow job, exported data, network environment, and local dependency versions. The author assumes no responsibility for any direct or indirect loss, malfunction, data leakage, legal liability, or other consequences arising from the use of this code.

<br />

## 许可协议 | License

本项目建议按照研究交流用途发布。若在 GitHub 上公开发布，请在发布前确认仓库中不包含真实 API Token、私有服务器地址、个人账号或其他敏感信息。

This project is intended for research and technical exchange. Before publishing it on GitHub, please make sure that no real API token, private server address, personal account, or other sensitive information remains in the repository.

<br />

## 联系方式 | Contact

与本代码相关的问题可联系作者彭啸宇（[pengxy19@tsinghua.org.cn](mailto:pengxy19@tsinghua.org.cn)）或课题组负责人刘锋（[lfeng@mail.tsinghua.edu.cn](mailto:lfeng@mail.tsinghua.edu.cn)）进行咨询。

For any questions or uses of the source codes, please feel free to contact the author, Xiaoyu Peng ([pengxy19@tsinghua.org.cn](mailto:pengxy19@tsinghua.org.cn)), and the corresponding author, Feng Liu ([lfeng@mail.tsinghua.edu.cn](mailto:lfeng@mail.tsinghua.edu.cn)).

<br />

## 主要功能 | Main Features

- 自动调用 CloudPSS 模型中的潮流计算任务。
- 自动从 CloudPSS 运行结果消息中提取选定区域的潮流结果及其映射关系文件 `area_name.cf` 与 `area_name.cf.map`。
- 支持对 CDF 文本进行基础归一化处理。
- 将 IEEE CDF 数据转换为 MATPOWER MPC 格式。
- 基于 pandapower 计算系统导纳矩阵 `Ybus`。
- 返回 `Ybus` 与 CloudPSS 元件到 CDF/Ybus 节点顺序的映射关系 `cdf_map`。
- 同时支持 Python 函数调用和命令行调用。

- Automatically runs the power-flow job in a CloudPSS model.
- Extracts `area_name.cf` and `area_name.cf.map` from CloudPSS result messages.
- Performs basic normalization for CDF text.
- Converts IEEE CDF data into a MATPOWER MPC-style case.
- Computes the system admittance matrix `Ybus` with pandapower.
- Returns both `Ybus` and the CloudPSS-to-CDF/Ybus mapping `cdf_map`.
- Supports both Python function calls and command line usage.

<br />

## 实现思路 | Implementation Approach

1. 通过 `func_cloudpss_config.py` 注入 CloudPSS 服务器地址、API Token 和用户名。
2. 根据 `project_name` 和 `user_name` 拉取 CloudPSS 模型：

   ```python
   model = cloudpss.Model.fetch(f"model/{user_name}/{project_name}")
   ```

3. 获取或创建名为 `Power Flow Job: Admittance Mat Generation` 的潮流任务，并将潮流导出格式设置为 `common_format`。
4. 运行潮流计算，等待 CloudPSS runner 完成。
5. 从 runner 消息中查找 `cf.zip` 的 data URI，并在内存中读取指定分区的 `.cf` 与 `.cf.map` 文件。
6. 对 CDF 内容做归一化处理。
7. 将 CDF 数据转换为 MATPOWER MPC 格式。
8. 使用 pandapower 将 MPC/PYPOWER case 转换为 pandapower net，运行潮流并读取：

   ```python
   Ybus = net["_ppc"]["internal"]["Ybus"]
   ```

9. 返回：

   ```python
   return Ybus, cdf_map
   ```

<br />

## 文件结构 | File Structure

- `main.py`：命令行入口，只调用 `func_generate_admittance_matrix_cli()`。
- `func_cloudpss_config.py`：CloudPSS 配置信息注入函数，用户需要先配置该文件。
- `func_generate_admittance_matrix.py`：主流程函数与 CLI 包装函数。
- `func_process_messages_for_cdf.py`：解析 CloudPSS runner 消息，提取 CDF 与映射文件。
- `func_cdf_normalization.py`：CDF 文本归一化处理。
- `func_cdf2mpc.py`：将 IEEE CDF 数据转换为 MATPOWER MPC 格式。

<br />

## 依赖环境 | Dependencies

本项目当前已在以下关键版本上验证：

- Python：建议使用 Python 3.10 或更高版本。
- `cloudpss==5.0.0`：已验证可正常调用。
- `pandapower==3.4.0`：已验证可正常调用。

关键依赖与相关链接：

- CloudPSS manuals: <https://kb.cloudpss.net>
- pandapower GitHub: <https://github.com/e2nIEE/pandapower>
- pandapower PYPOWER converter documentation: <https://pandapower.readthedocs.io/en/latest/converter/pypower.html>
- MATPOWER: <https://matpower.org/>

<br />

## 配置方法 | Configuration

在调用任何主流程前，用户必须先配置 `func_cloudpss_config.py` 中的 CloudPSS 连接信息：

```python
def func_inject_cloudpss_config():
    server_name = "your_cloudpss_server_url"
    token = "your_cloudpss_api_token"
    user_name = "your_cloudpss_user_name"

    cloudpss.setToken(f'{token}')
    os.environ['CLOUDPSS_API_URL'] = f'{server_name}'
    return server_name, token, user_name
```

其中：

- `server_name`：CloudPSS 服务器地址，例如 `https://cloudpss.net/` 或用户所在机构部署的服务器地址。
- `token`：用户自己的 CloudPSS API Token。
- `user_name`：CloudPSS 用户名，用于拼接模型路径。

模型拉取路径为：

```python
model = cloudpss.Model.fetch(f'model/{user_name}/{project_name}')
```

发布到 GitHub 前，请务必删除真实 `token`、私人服务器地址和个人账号信息，或改为占位内容。

<br />

## 使用方法 | Usage

### 方式一：Python 函数调用 | Python Function Call

推荐在其他 Python 程序中直接调用主函数：

```python
from func_generate_admittance_matrix import func_generate_admittance_matrix

project_name = "IEEE39"
area_name = "area1"

Ybus, cdf_map = func_generate_admittance_matrix(project_name, area_name)

print(Ybus)
print(cdf_map)
```

这是本项目的核心调用方式。`func_generate_admittance_matrix_cli()` 不是唯一调用入口，它只是为了命令行使用而提供的包装函数。

### 方式二：命令行调用 | Command Line Usage

也可以通过命令行调用：

```powershell
python main.py --project-name IEEE39 --area-name area1
```

或直接调用主流程文件：

```powershell
python func_generate_admittance_matrix.py --project-name IEEE39 --area-name area1
```

参数说明：

- `--project-name`：CloudPSS 项目名称，不包含 `model/{user_name}/` 前缀。
- `--area-name`：CDF 分区名称，例如 `area1`。程序会读取 `area1.cf` 与 `area1.cf.map`。

<br />

## 关键数据格式 | Key Data Formats

### IEEE Common Data Format (CDF)

本项目从 CloudPSS 潮流结果中读取 IEEE Common Data Format（CDF）格式的潮流文件。当前流程默认从 `cf.zip` 中读取：

- `{area_name}.cf`
- `{area_name}.cf.map`

CDF 格式说明参考：

- IEEE Common Data Format example/specification: <https://labs.ece.uw.edu/pstca/formats/cdf.txt>

### MATPOWER MPC Format

`func_cdf2mpc.py` 会将 CDF 内容转换为 MATPOWER case struct，即本项目中所称的 `mpc`。该结构包含 `baseMVA`、`bus`、`branch`、`gen`、`gencost` 等字段，并用于后续 pandapower 转换。

MATPOWER 相关链接：

- MATPOWER official website: <https://matpower.org/>
- MATPOWER case format documentation: <https://matpower.org/documentation/>

### Ybus 与 cdf_map

主函数返回：

```python
Ybus, cdf_map = func_generate_admittance_matrix(project_name, area_name)
```

- `Ybus`：pandapower 内部 PPC 结果中的系统导纳矩阵，通常为稀疏矩阵。
- `cdf_map`：由 `{area_name}.cf.map` 解析出的映射关系，用于说明 CDF/Ybus 节点顺序与 CloudPSS 实际元件之间的对应关系。

<br />

## pandapower 兼容性说明 | pandapower Compatibility

不同 pandapower 版本中，`from_ppc` 的暴露路径可能不同。

在较新的 `pandapower==3.4.0` 中，推荐使用：

```python
from pandapower.converter.pypower.from_ppc import from_ppc
```

部分旧版本中，可能仍可通过如下路径调用：

```python
pandapower.converter.from_ppc
```

因此本项目在 `func_generate_admittance_matrix.py` 中提供了兼容逻辑：

1. 优先尝试 `pandapower.converter.pypower.from_ppc`。
2. 若该路径不可用，再回退到 `pandapower.converter.from_ppc`。
3. 如果两个路径都不可用，则抛出明确错误，提示检查 pandapower 版本。

该逻辑避免了仅依赖版本号判断，提高了对不同 pandapower 版本的适配能力。

<br />

## 注意事项 | Notes

- 使用前必须先正确配置 `func_cloudpss_config.py`。
- 使用前必须确认 CloudPSS 项目中存在可运行的潮流计算任务，或允许程序自动创建 `Power Flow Job: Admittance Mat Generation`。
- 当前流程依赖 CloudPSS runner 消息中存在 `cf.zip` 的 data URI 下载链接。
- `area_name` 必须与 `cf.zip` 内部的 `.cf` 和 `.cf.map` 文件名前缀一致。
- 本项目会触发 CloudPSS 远端潮流计算，请确认服务器地址、Token 权限和模型权限正确。
- 发布公开仓库前，请删除真实配置、Token、服务器地址、个人账号和运行结果中的敏感信息。

<br />

## 参考 | References

[1] Y. Song, Y. Chen, Z. Yu, S. Huang, and C. Shen, "CloudPSS: A high-performance power system simulator based on cloud computing," *Energy Reports*, vol. 6, pp. 1611-1618, Dec. 2020, doi: [10.1016/j.egyr.2020.12.028](https://doi.org/10.1016/j.egyr.2020.12.028).

[2] pandapower: <https://github.com/e2nIEE/pandapower>

[3] MATPOWER: <https://matpower.org/>
