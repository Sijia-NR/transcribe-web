"""WhisperX 本地 GPU 转写管线

使用 faster-whisper (large-v3) + pyannote/speaker-diarization-community-1
通过 HF_ENDPOINT=https://hf-mirror.com 下载模型（国内镜像）
模型缓存在全局变量中，避免每次请求重新加载。
"""

import os
import gc

# ── 全局模型缓存（只加载一次，常驻 GPU 显存） ──
_asr_model = None
_asr_device = None
_align_cache = {}       # language -> (align_model, metadata)
_diarize_model = None


def _get_device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def _get_asr_model(device):
    global _asr_model, _asr_device
    if _asr_model is None:
        import whisperx
        _asr_model = whisperx.load_model(
            "large-v3", device=device, compute_type="int8", language=None,
        )
        _asr_device = device
    return _asr_model


def _get_align_model(language, device):
    if language in _align_cache:
        return _align_cache[language]
    import whisperx
    align_model, metadata = whisperx.load_align_model(
        language_code=language, device=device,
    )
    _align_cache[language] = (align_model, metadata)
    return align_model, metadata


def _get_diarize_model(device, hf_token):
    global _diarize_model
    if _diarize_model is None:
        from whisperx.diarize import DiarizationPipeline
        _diarize_model = DiarizationPipeline(token=hf_token, device=device)
    return _diarize_model


def process_audio(filepath, tasks_dict, task_id, hf_token=None):
    """处理音频文件，输出兼容 result.html 的 segments 格式

    Args:
        filepath: 音频文件路径
        tasks_dict: 全局 tasks 字典（用于更新进度）
        task_id: 任务 ID
        hf_token: HuggingFace token（用于 pyannote 模型）

    Returns:
        list[(speaker, text), ...] — 与讯飞 parse_result 格式一致
    """
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    import torch
    import whisperx

    device = _get_device()

    # ── 阶段 1：ASR ──
    if _asr_model is None:
        _update_status(tasks_dict, task_id, "正在加载 Whisper 模型（首次较慢）...")
    else:
        _update_status(tasks_dict, task_id, "正在转写音频...")

    model = _get_asr_model(device)
    audio = whisperx.load_audio(filepath)
    result = model.transcribe(audio, batch_size=8)

    language = result.get("language", "zh")
    segments_raw = result.get("segments", [])

    if not segments_raw:
        return []

    # ── 阶段 2：对齐 ──
    if language not in _align_cache:
        _update_status(tasks_dict, task_id, "正在加载对齐模型...")
    else:
        _update_status(tasks_dict, task_id, "正在对齐时间戳...")

    align_model, metadata = _get_align_model(language, device)
    result = whisperx.align(segments_raw, align_model, metadata, audio, device)

    # ── 阶段 3：说话人识别 ──
    if _diarize_model is None:
        _update_status(tasks_dict, task_id, "正在加载说话人识别模型...")
    else:
        _update_status(tasks_dict, task_id, "正在进行说话人识别...")

    diarize_model = _get_diarize_model(device, hf_token)
    diarize_segments = diarize_model(audio)

    result = whisperx.assign_word_speakers(diarize_segments, result)

    # ── 格式转换：兼容讯飞 segments 格式 ──
    segments = []
    for seg in result.get("segments", []):
        speaker = seg.get("speaker", "SPEAKER_00")
        speaker_num = str(int(speaker.replace("SPEAKER_", "")) + 1)
        text = seg.get("text", "").strip()
        if text:
            segments.append((speaker_num, text))

    # 合并同一说话人连续段落
    merged = []
    for rl, text in segments:
        if merged and merged[-1][0] == rl:
            merged[-1] = (rl, merged[-1][1] + " " + text)
        else:
            merged.append((rl, text))

    return merged


def _update_status(tasks_dict, task_id, text):
    """更新任务状态文字"""
    if task_id in tasks_dict:
        tasks_dict[task_id]["status_text"] = text
