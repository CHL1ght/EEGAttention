"""
【教学注释版】

对应正式文件：
    scripts/eeg_pipeline_utils.py

用途：
    帮助项目所有者理解 EEGAttention 两个正式入口共同使用的工具函数。

重要：
    1. 本文件是教学副本，不是正式实验代码。
    2. 不要运行本文件，也不要从本文件生成模型、artifact 或指标。
    3. 正式实验请使用 scripts/legacy_baseline_v0.py 或
       scripts/evaluate_locked_test.py。
    4. 如果正式源文件以后改变，本文件可能需要同步更新。
"""

from __future__ import annotations

# hashlib：计算 SHA-256 文件指纹。
# json：读写配置和指标等结构化文本。
# pathlib.Path：跨平台地表示文件路径，比手写字符串拼接更安全。
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

# mne 专门用于 EEG/MEG 等神经信号。
# numpy 负责数组和数值运算。
import mne
import numpy as np

# welch 把“电压随时间变化”的信号转换为“不同频率上的功率”。
from scipy.signal import welch


def save_json(path: Path, value: Any) -> None:
    """保存稳定、易读的 JSON 文件。"""
    # value 可以是 dict、list 或包含嵌套结构的普通 Python 对象。
    # ensure_ascii=False 让中文保持可读，而不是变成 \uXXXX。
    # indent=2 方便人打开查看；sort_keys=True 让同样内容的文件顺序稳定。
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def save_dataframe(path: Path, dataframe: Any) -> None:
    """把 pandas DataFrame 保存为 CSV，并提前创建父目录。"""
    # output_dir 可能还不存在，所以先 mkdir。
    # parents=True 表示必要时连上级目录一起创建。
    # exist_ok=True 表示目录已经存在时不报错。
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


def sha256_file(path: Path) -> str:
    """返回文件内容的 SHA-256 数字指纹。"""
    # hash 不是文件的副本，而是由内容计算出的短指纹。
    # 项目用它确认：当前测试使用的 pipeline/config 是否仍是冻结版本。
    # 每次只读取 1 MiB，避免把大文件一次性放入内存。
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_locked_path(path: Path) -> bool:
    """判断路径是否位于受保护的 data/locked 目录。"""
    # resolve() 把相对路径转换成绝对路径。
    # 统一斜杠并转小写，是为了减少 Windows 路径写法差异带来的漏检。
    normalized = str(path.resolve()).replace("\\", "/").lower()
    return "/data/locked/" in normalized or normalized.endswith("/data/locked")


def assert_not_locked(path: Path, description: str) -> None:
    """训练入口使用的安全闸门：禁止它读取 locked 数据。"""
    # 这里用 assert-like 的显式异常，而不是静默跳过。
    # 如果训练脚本误指向 locked，应该立刻停止，不能让实验边界变得模糊。
    if is_locked_path(path):
        raise RuntimeError(f"Refusing to access locked data ({description}): {path}")


def print_banner(title: str) -> None:
    """打印两个正式入口共同使用的简洁标题。"""
    print("\n" + "=" * 60)
    print(f" EEGAttention — {title}")
    print("=" * 60)


def print_metric(name: str, value: Any) -> None:
    """把一个指标按固定宽度打印，便于终端快速扫描。"""
    print(f"  {name:<20}: {value}")


def load_eeg_recording(
    edf_path: Path,
    *,
    target_fs: float = 128.0,
    allow_locked: bool = False,
) -> tuple[np.ndarray, float, list[str]]:
    """
    读取一个 EDF，并统一 EEG 通道和采样率。

    输入
    ----
    edf_path:
        EDF 文件路径。EDF 是 EEG 常见的存储格式，里面有通道名称、
        采样率和连续信号样本。
    target_fs:
        目标采样率。当前项目固定为 128 Hz。
    allow_locked:
        训练脚本保持 False；只有已经验证路径位于 locked 日期目录的
        独立 inference 入口才会显式传 True。

    输出
    ----
    data:
        numpy 数组，形状是 ``(n_channels, n_time_samples)``。
    sfreq:
        实际输出采样率。
    channels:
        输出数组每一行对应的通道名称列表。

    关键概念
    --------
    ``24 channels, 300 Hz, 10 seconds`` 大致对应 ``(24, 3000)``。
    第一维是通道，第二维是时间采样点，不要和机器学习常见的
    ``(n_samples, n_features)`` 混淆。
    """
    if not allow_locked:
        # baseline 默认走这里，防止训练入口误读最终测试集。
        assert_not_locked(edf_path, "EDF")

    # Raw 是 MNE 对连续神经信号的对象封装。
    # preload=True 表示把数据加载到内存，后面才能直接 get_data() 和 resample。
    # infer_types=True 尝试从 EDF 的通道信息推断 EEG 类型。
    raw = mne.io.read_raw_edf(
        str(edf_path),
        preload=True,
        infer_types=True,
        verbose=False,
    )

    # 一个 EDF 可能还包含 trigger、misc 或其他辅助通道。
    # 当前特征定义只针对 EEG，所以保留 MNE 标记为 eeg 的通道。
    # try/except 是为了兼容不同 MNE 版本的 verbose 参数差异。
    try:
        raw.pick_types(eeg=True, stim=False, misc=False, verbose=False)
    except TypeError:
        raw.pick_types(eeg=True, stim=False, misc=False)
    if len(raw.ch_names) == 0:
        raise ValueError(f"{edf_path} has no MNE-recognized EEG channels")

    source_fs = float(raw.info["sfreq"])
    # 例如 300 Hz 表示每秒记录 300 个时间点。
    # 当前实现要求源采样率是整数，避免 sample index 计算不明确。
    if not np.isclose(source_fs, float(round(source_fs)), atol=1e-6):
        raise ValueError(f"Non-integral source sampling rate is unsupported: {source_fs}")

    # 为了让 Legacy 和 LOCKED_TEST 进入完全相同的 feature space，
    # 如果源数据不是 128 Hz，就统一重采样。
    # 300 Hz → 128 Hz 后，每秒从 300 个点变成 128 个点，计算量也下降。
    if not np.isclose(source_fs, target_fs):
        raw.resample(target_fs, npad="auto", verbose=False)

    # MNE 的 get_data() 返回 shape=(通道数, 时间点数)。
    data = raw.get_data()
    return data, float(raw.info["sfreq"]), list(raw.ch_names)


def preprocess_eeg(
    segment_data: np.ndarray,
    sfreq: float,
    *,
    l_freq: float = 0.5,
    h_freq: float = 43.0,
) -> np.ndarray:
    """
    对一个逻辑 segment 做冻结的 FIR 带通预处理。

    例如输入可以是 ``(24, 76800)``：24 个通道、600 秒 × 128 Hz。

    ``0.5–43 Hz`` 的含义是：

    - 低于 0.5 Hz 的超慢变化通常包括 baseline drift 等慢漂移；
    - 高于 43 Hz 的部分不是当前任务的目标频段，也可能包含较多高频噪声；
    - FIR 是有限脉冲响应滤波器，``firwin`` 是设计这种滤波器的一种方法。
    """
    # Nyquist 频率是采样率的一半。128 Hz 的 Nyquist 是 64 Hz，
    # 因此 43 Hz 上限仍低于理论可表示的最高频率。
    # 这里调用 MNE 的统一实现，避免训练和测试各写一套滤波细节。
    return mne.filter.filter_data(
        segment_data,
        sfreq=sfreq,
        l_freq=l_freq,
        h_freq=h_freq,
        method="fir",
        fir_design="firwin",
        verbose=False,
    )


def make_windows(
    segment_data: np.ndarray,
    sfreq: float,
    *,
    window_sec: float = 4.0,
    step_sec: float = 2.0,
) -> Iterator[tuple[np.ndarray, float]]:
    """
    把一个 segment 切成固定长度、固定步长的窗口。

    4 秒窗口、2 秒 step 的前几个窗口是：

    ```text
    Window 1: 0–4 s
    Window 2: 2–6 s
    Window 3: 4–8 s
    Window 4: 6–10 s
    ```

    所以相邻窗口重叠 2 秒。窗口数也不等于总时长除以 4，
    因为窗口之间有重叠，最后不足 4 秒的尾部会被舍弃。

    返回的第二项是窗口在当前 segment 内的起始秒数。
    """
    # 连续信号在数组中由 sample index 表示，因此秒数必须乘 sfreq。
    window_size = int(round(window_sec * sfreq))
    step_size = int(round(step_sec * sfreq))
    if segment_data.shape[1] < window_size:
        raise ValueError("Segment is shorter than one frozen 4-second window")

    # range(start, stop, step) 依次产生 0、step_size、2*step_size ...。
    # 只有完整窗口才进入循环，避免访问 segment 边界外的样本。
    for start in range(0, segment_data.shape[1] - window_size + 1, step_size):
        window = segment_data[:, start : start + window_size]
        yield window, start / sfreq


def extract_bandpower_features(
    window_data: np.ndarray,
    sfreq: float,
    bands: dict[str, tuple[float, float]],
    *,
    welch_nperseg_sec: float = 2.0,
) -> np.ndarray:
    """
    从一个 EEG window 生成一维 band-power feature vector。

    原始 EEG 是“电压随时间变化”。Welch PSD 后，可以得到类似：

    ```text
    1 Hz  → power
    5 Hz  → power
    10 Hz → power
    20 Hz → power
    ```

    再把频率合并到 delta/theta/alpha/beta/gamma 五个频段。
    每个通道、每个频段保存两种数字：

    1. log absolute power：该频段绝对功率取自然对数；
    2. relative power：该频段功率除以 1–43 Hz 总功率。

    例如一个通道的特征可以理解为：

    ```text
    delta_log, theta_log, alpha_log, beta_log, gamma_log,
    delta_relative, theta_relative, alpha_relative, beta_relative, gamma_relative
    ```

    多个通道的这些特征按通道顺序拼接成一个 window 的向量。
    """
    features: list[float] = []
    for channel_data in window_data:
        # Welch 会把一段时间信号分成重叠小段，分别估计 PSD，
        # 再平均以降低单次频谱估计的波动。
        freqs, psd = welch(
            channel_data,
            fs=sfreq,
            nperseg=min(len(channel_data), int(sfreq * welch_nperseg_sec)),
        )

        # total_power 是 1–43 Hz 的积分近似。
        # +1e-12 防止全零或极小信号导致除零和 log(0)。
        total_idx = (freqs >= 1.0) & (freqs <= 43.0)
        total_power = float(np.trapezoid(psd[total_idx], freqs[total_idx])) + 1e-12

        for low, high in bands.values():
            # boolean mask 选出当前频段对应的频率 bin。
            # 下界包含、上界不包含，和正式实现保持一致。
            band_idx = (freqs >= low) & (freqs < high)
            power = float(np.trapezoid(psd[band_idx], freqs[band_idx])) + 1e-12

            # log power 的主要作用是压缩尺度：
            # alpha=1000 和 beta=10 的差距，取 log 后不会仍保持 100 倍。
            # 它不是概率，也不是把数值归一化到 0–1。
            log_absolute_power = float(np.log(power))

            # relative power 回答“这个频段占总频谱多大比例”。
            # 例如总功率 100、alpha 功率 30，则 relative power=0.30。
            relative_power = float(power / total_power)
            features.extend((log_absolute_power, relative_power))

    # np.asarray 把 Python list 转为 numpy 数组，便于之后堆叠为 X。
    # 一个 window 的输出 shape 是 (n_features,)，例如 24*5*2=240。
    return np.asarray(features, dtype=np.float64)


def extract_segment_features(
    data: np.ndarray,
    sfreq: float,
    start_sec: float,
    end_sec: float,
    bands: dict[str, tuple[float, float]],
    *,
    window_sec: float = 4.0,
    step_sec: float = 2.0,
    l_freq: float = 0.5,
    h_freq: float = 43.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    完成一个逻辑 segment 的完整特征流程。

    输入
    ----
    data:
        shape=(通道数, 全部时间点) 的 EDF 数据。
    start_sec, end_sec:
        来自 manifest 的 segment 边界，而不是从文件名猜标签。
    bands/window/filter 参数:
        从正式 baseline 的冻结配置传入。

    输出
    ----
    X_segment:
        shape=(n_windows, n_features)，例如 ``(299, 240)``。
    window_starts:
        每个窗口相对于原 EDF 的起始秒数，shape=(n_windows,)。

    流程
    ----
    ```text
    EDF data
      → 按 manifest 截取 segment
      → FIR preprocessing
      → 4 s / 2 s windows
      → Welch PSD
      → 五频段 log + relative power
      → X_segment
    ```
    """
    # 秒数必须先变成数组索引。例如 600 s * 128 Hz = 76800。
    start = int(round(start_sec * sfreq))
    stop = int(round(end_sec * sfreq))
    if start < 0 or stop > data.shape[1] or stop <= start:
        raise ValueError(
            f"Manifest interval [{start_sec}, {end_sec}) is outside EDF "
            f"({data.shape[1] / sfreq:.3f} s)"
        )

    # 先切 segment，再滤波，确保 mixed EDF 的两个逻辑 segment 不跨边界混用。
    filtered = preprocess_eeg(
        data[:, start:stop],
        sfreq,
        l_freq=l_freq,
        h_freq=h_freq,
    )

    features: list[np.ndarray] = []
    starts: list[float] = []
    for window, offset_sec in make_windows(
        filtered,
        sfreq,
        window_sec=window_sec,
        step_sec=step_sec,
    ):
        features.append(extract_bandpower_features(window, sfreq, bands))
        # offset_sec 是 segment 内偏移；加 start_sec 才回到 EDF 全局时间。
        starts.append(start_sec + offset_sec)

    # np.asarray(features) 将很多个 shape=(n_features,) 的向量组成矩阵。
    # 机器学习要求 X 的第一维是样本数，第二维是特征数。
    return np.asarray(features), np.asarray(starts, dtype=np.float64)
