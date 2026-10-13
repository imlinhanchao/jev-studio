import asyncio
import base64
import importlib.util
import io
import logging
import os
import subprocess
import sys
import time
from typing import Any, Optional

import torch

from app.core.config import settings
from app.schemas.decision import QuestionDefinition

logger = logging.getLogger("jev.model_engine")

# Each supported model is served by a dedicated backend:
#   liquid  -> Hugging Face transformers AutoModel + native `system_one` (trust_remote_code)
#   minicpm -> ytbai/MiniCPM5-2B-Jev checkpoint (LoRA + LetterReadoutHead), loaded through its shipped model.py
#   edgejev -> pip package `edgejev` (ONNX + INT8 runtime, no torch at inference)
SUPPORTED_MODELS = [
    {
        "id": "LiquidAI/d1-omni-600M",
        "backend": "liquid",
        "name": "Liquid AI d1-omni-600M",
        "provider": "Liquid AI",
        "architecture": "LFM2.5-Encoder-350M (d1-omni-600M)",
        "parameters": "600M",
        "description": "原生多模态支持（文本+图像视觉），专为结构化决策优化，零生成延迟，超高吞吐单步前向推理",
        "tags": ["多模态视觉", "极速推理", "零生成延迟", "600M 参数"],
        "recommended_for": "图文审核、票据识别路由、实时工单流转、毫秒级业务决策",
        "typical_latency_ms": "15 ~ 35 ms",
        "supports_vision": True,
    },
    {
        "id": "ytbai/MiniCPM5-2B-Jev",
        "backend": "minicpm",
        "name": "MiniCPM5-2B-Jev",
        "provider": "ytbai / OpenBMB (MiniCPM5-2B 微调)",
        "architecture": "MiniCPM5-2B + LoRA + LetterReadoutHead",
        "parameters": "2.0B",
        "description": "面壁智能 MiniCPM5-2B 上的决策增强微调模型（LoRA + 原生 lm_head 字母读出），深度泛化与长文本语义决策",
        "tags": ["长文本理解", "复杂泛化", "2.0B 参数", "PEFT"],
        "recommended_for": "复杂行业风控、深层用户意图洞察、多条件交叉判定",
        "typical_latency_ms": "30 ~ 65 ms",
        "supports_vision": False,
    },
    {
        "id": "EdgeJev",
        "backend": "edgejev",
        "name": "EdgeJev",
        "provider": "EdgeJev (PyPI: edgejev)",
        "architecture": "EdgeJev-ONNX-INT8 (laya/mmBERT 后端)",
        "parameters": "322M",
        "description": "离线可用的边端类型化决策模型，ONNX + INT8 量化，运行时无需 torch，超低显存与极低延迟",
        "tags": ["端侧边缘计算", "ONNX INT8", "离线推理", "无 torch 运行时"],
        "recommended_for": "IoT网关流式过滤、移动端轻量判定、内网/断网环境边界决策",
        "typical_latency_ms": "5 ~ 15 ms",
        "supports_vision": False,
    },
]


class ModelNotReadyError(RuntimeError):
    """Raised when the active decision model cannot serve inference (not loaded or load failed)."""


def parse_image_to_pil(image_data: str) -> Optional[Any]:
    if not image_data or not isinstance(image_data, str):
        return None
    try:
        from PIL import Image
        if image_data.startswith("data:"):
            header, base64_str = image_data.split(",", 1)
            raw_bytes = base64.b64decode(base64_str)
            return Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        elif image_data.startswith("http://") or image_data.startswith("https://"):
            from transformers.image_utils import load_image
            return load_image(image_data)
        elif os.path.exists(image_data):
            return Image.open(image_data).convert("RGB")
        else:
            raw_bytes = base64.b64decode(image_data)
            return Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except Exception as e:
        logger.warning(f"Could not load image into PIL: {e}")
        return None


class DecisionModelEngine:
    def __init__(self):
        self.model_id = settings.MODEL_ID
        # Validate configured model
        if not any(m["id"] == self.model_id for m in SUPPORTED_MODELS):
            self.model_id = SUPPORTED_MODELS[0]["id"]

        self.device = self._detect_device()
        self.model = None
        self.is_loaded = False
        self.is_loading = False
        self.load_error: str | None = None
        self.mode = "unloaded"  # "real", "unloaded" or "error"
        # Simple cache: keep previously loaded models resident instead of unloading on switch.
        self.cache_enabled = settings.MODEL_CACHE_ENABLED
        self.loaded_models: dict[str, Any] = {}
        self.progress: dict[str, Any] = {
            "model_id": self.model_id,
            "state": "idle",
            "percent": 0.0,
            "message": "",
            "updated_at": time.time(),
        }
        # Serializes concurrent load/switch requests so an in-flight load can never
        # be assigned to a different active model.
        self._load_lock = asyncio.Lock()

    def _detect_device(self) -> str:
        if settings.MODEL_DEVICE != "auto":
            return settings.MODEL_DEVICE
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    @staticmethod
    def _cache_dir() -> Optional[str]:
        return settings.MODEL_CACHE_DIR if os.path.exists(settings.MODEL_CACHE_DIR) else None

    def get_model_meta(self, model_id: str) -> dict[str, Any]:
        for m in SUPPORTED_MODELS:
            if m["id"] == model_id:
                return m
        return SUPPORTED_MODELS[0]

    def get_available_models(self) -> list[dict[str, Any]]:
        models = []
        for m in SUPPORTED_MODELS:
            item = dict(m)
            item["is_active"] = (m["id"] == self.model_id)
            item["is_loaded"] = (m["id"] in self.loaded_models)
            models.append(item)
        return models

    def get_progress(self) -> dict[str, Any]:
        return dict(self.progress)

    def _set_progress(self, state: str, percent: Optional[float] = None, message: str = "",
                      model_id: Optional[str] = None) -> None:
        self.progress = {
            "model_id": model_id or self.model_id,
            "state": state,
            "percent": round(float(percent), 1) if percent is not None else float(self.progress.get("percent", 0.0)),
            "message": message,
            "updated_at": time.time(),
        }

    def _active_backend(self) -> str:
        return self.get_model_meta(self.model_id).get("backend", "liquid")

    def _drop_model(self, model_id: str) -> bool:
        """Releases one model's weights. Returns True if it was resident."""
        handle = self.loaded_models.pop(model_id, None)
        if handle is None:
            return False
        if model_id == self.model_id and self.model is handle:
            self.model = None
            self.is_loaded = False
            if self.mode == "real":
                self.mode = "unloaded"
        self._release_device_cache()
        logger.info(f"Unloaded model {model_id} from memory.")
        return True

    def _set_active_model(self, model_id: str) -> None:
        """Sets the active model id. Unloads the previous model unless simple cache is on."""
        valid_ids = [m["id"] for m in SUPPORTED_MODELS]
        if model_id not in valid_ids:
            raise ValueError(f"Unsupported model '{model_id}'. Supported: {valid_ids}")

        if self.model_id != model_id:
            previous = self.model_id
            if not self.cache_enabled:
                self._drop_model(previous)
            self.model_id = model_id
            self.load_error = None
            self.model = self.loaded_models.get(model_id)
            self.is_loaded = self.model is not None
            self.mode = "real" if self.is_loaded else "unloaded"
            logger.info(f"Switched active decision model to: {model_id}")

    async def set_cache_mode(self, enabled: bool) -> dict[str, Any]:
        """Toggles simple caching; disabling it unloads every non-active cached model."""
        async with self._load_lock:
            self.cache_enabled = bool(enabled)
            if not self.cache_enabled:
                for mid in list(self.loaded_models):
                    if mid != self.model_id:
                        self._drop_model(mid)
        return self.get_status()

    async def switch_model(self, model_id: str) -> dict[str, Any]:
        """Switches the default active model and loads its weights at switch time."""
        self._set_active_model(model_id)
        await self._ensure_active_loaded()
        return self.get_status()

    async def load_real_model(self, force: bool = False, model_id: Optional[str] = None) -> dict[str, Any]:
        """
        Loads the active model's weights on a worker thread so the event loop stays responsive.
        The loading strategy is selected per model backend.
        """
        if model_id and model_id != self.model_id:
            self._set_active_model(model_id)

        async with self._load_lock:
            if force:
                self._drop_model(self.model_id)
            if self.loaded_models.get(self.model_id) is not None:
                self.model = self.loaded_models[self.model_id]
                self.is_loaded = True
                self.mode = "real"
                return {"status": "already_loaded", "mode": self.mode, "device": self.device, "model_id": self.model_id}
            await self._load_active(self.model_id)
        return {
            "status": "success" if self.is_loaded else "failed",
            "mode": self.mode,
            "device": self.device,
            "model_id": self.model_id,
            "error": self.load_error,
        }

    async def _ensure_active_loaded(self) -> None:
        """Loads whatever model is active, retrying if the active model changed mid-load."""
        async with self._load_lock:
            while self.loaded_models.get(self.model_id) is None and not self.load_error:
                target = self.model_id
                logger.info(f"Loading weights for model: {target}...")
                await self._load_active(target)
                if self.model_id != target:
                    # Active model changed while loading; discard and load the new one.
                    continue
            self.model = self.loaded_models.get(self.model_id)
            self.is_loaded = self.model is not None
            if self.is_loaded:
                self.mode = "real"

    async def _load_active(self, target_id: str) -> None:
        """Loads `target_id`; discards the handle if the active model changes meanwhile."""
        backend = self.get_model_meta(target_id).get("backend", "liquid")
        self.is_loading = True
        self.load_error = None
        self._set_progress("preparing", 3.0, f"准备加载 {target_id} ...", target_id)
        try:
            loop = asyncio.get_running_loop()
            handle = await loop.run_in_executor(None, self._load_sync, backend, target_id)
        except Exception as exc:
            self.is_loading = False
            if self.model_id == target_id:
                self.load_error = str(exc)
                self.is_loaded = False
                self.model = None
                self.mode = "error"
                self._set_progress("error", None, str(exc), target_id)
            logger.error(f"Could not load {target_id} ({backend}): {exc}")
            return
        finally:
            self.is_loading = False

        if self.model_id != target_id:
            logger.info(f"Discarding stale load for {target_id} (active is now {self.model_id}).")
            handle = None
            self._release_device_cache()
            self._set_progress("idle", 0.0, "", target_id)
            return

        self.loaded_models[target_id] = handle
        self.model = handle
        self.is_loaded = True
        self.mode = "real"
        self.load_error = None
        self._set_progress("ready", 100.0, f"{target_id} 已就绪", target_id)
        logger.info(f"Successfully loaded {target_id} ({backend}) on {self.device}.")

    @staticmethod
    def _release_device_cache() -> None:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()

    def _load_sync(self, backend: str, target_id: str) -> Any:
        if backend == "liquid":
            return self._load_liquid(target_id)
        if backend == "minicpm":
            return self._load_minicpm(target_id)
        if backend == "edgejev":
            return self._load_edgejev(target_id)
        raise ModelNotReadyError(f"未知的模型后端: {backend}")

    # ------------------------------------------------------------------ liquid
    def _load_liquid(self, target_id: str) -> Any:
        from transformers import AutoModel

        cache_dir = self._cache_dir()

        def _from_pretrained(dev: str, dtype: torch.dtype):
            model = AutoModel.from_pretrained(
                target_id,
                trust_remote_code=True,
                dtype=dtype,
                cache_dir=cache_dir,
            )
            self._set_progress("loading", 80.0, f"加载 {target_id} 到 {dev} ...", target_id)
            model.to(dev)
            model.eval()
            return model

        target_device = self.device
        dtype = torch.float16 if target_device in ("cuda", "mps") else torch.float32
        logger.info(f"Loading {target_id} on {target_device} with dtype {dtype}...")
        self._set_progress("downloading", 10.0, f"下载 Hugging Face 权重：{target_id}", target_id)
        try:
            return _from_pretrained(target_device, dtype)
        except Exception as e:
            logger.warning(f"Failed to load on {target_device} ({e}), falling back to cpu...")
            self.device = "cpu"
            return _from_pretrained("cpu", torch.float32)

    # ----------------------------------------------------------------- minicpm
    @staticmethod
    def _import_minicpm_module(ckpt_dir: str):
        model_py = os.path.join(ckpt_dir, "model.py")
        if not os.path.exists(model_py):
            raise ModelNotReadyError(
                "MiniCPM5-2B-Jev 权重目录中缺少 model.py，无法载入决策读出层。"
            )
        module_name = "jev_minicpm_model"
        spec = importlib.util.spec_from_file_location(module_name, model_py)
        if spec is None or spec.loader is None:
            raise ModelNotReadyError("MiniCPM5-2B-Jev 的 model.py 无法导入。")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _load_minicpm(self, target_id: str) -> dict[str, Any]:
        from huggingface_hub import snapshot_download

        logger.info(f"Downloading MiniCPM5-2B-Jev checkpoint {target_id} ...")
        self._set_progress("downloading", 8.0, f"下载 MiniCPM5-2B-Jev checkpoint（含 base 权重，首次较久）", target_id)
        ckpt_dir = snapshot_download(target_id, cache_dir=self._cache_dir())
        module = self._import_minicpm_module(ckpt_dir)

        target_device = self.device
        dtype = torch.bfloat16 if target_device in ("cuda", "mps") else torch.float32
        logger.info(f"Loading {target_id} on {target_device} with dtype {dtype}...")
        self._set_progress("loading", 65.0, f"加载 MiniCPM5-2B 到 {target_device} ...", target_id)
        try:
            model, tokenizer = module.MiniCPMSystemOne.load_checkpoint(
                ckpt_dir, device=target_device, dtype=dtype
            )
        except Exception as e:
            logger.warning(f"Failed to load MiniCPM on {target_device} ({e}), falling back to cpu...")
            self.device = "cpu"
            model, tokenizer = module.MiniCPMSystemOne.load_checkpoint(
                ckpt_dir, device="cpu", dtype=torch.float32
            )
        return {"kind": "minicpm", "module": module, "model": model, "tokenizer": tokenizer}

    # ----------------------------------------------------------------- edgejev
    def _ensure_edgejev_model_dir(self) -> str:
        model_dir = settings.EDGEJEV_MODEL_DIR
        cfg_path = os.path.join(model_dir, "edgejev.json")
        if os.path.exists(cfg_path):
            return model_dir

        build_cmd = (
            f"edgejev build --backend {settings.EDGEJEV_BACKEND} --out {model_dir}"
        )
        if not settings.EDGEJEV_AUTO_BUILD:
            raise ModelNotReadyError(
                f"EdgeJev 模型尚未构建（缺少 {cfg_path}）。请先运行：{build_cmd}"
            )

        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"Building EdgeJev model into {model_dir} (first run downloads weights)...")
        self._set_progress("downloading", 10.0, f"构建 EdgeJev 模型（首次需下载权重）：{model_dir}")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "edgejev.cli", "build",
                 "--backend", settings.EDGEJEV_BACKEND, "--out", model_dir],
                capture_output=True, text=True,
            )
        except Exception as e:
            raise ModelNotReadyError(f"EdgeJev 构建命令执行失败：{e}") from e
        if proc.returncode != 0 or not os.path.exists(cfg_path):
            detail = (proc.stderr or proc.stdout or "").strip()[-500:]
            raise ModelNotReadyError(
                f"EdgeJev 模型构建失败（exit {proc.returncode}）。请确认已安装构建依赖："
                f"pip install 'edgejev[build]'。\n{detail}"
            )
        return model_dir

    def _load_edgejev(self, target_id: str) -> dict[str, Any]:
        try:
            from edgejev import Agent
        except ImportError as e:
            raise ModelNotReadyError(
                "未安装 edgejev 包，无法载入 EdgeJev。请执行：pip install 'edgejev[build]'"
            ) from e

        model_dir = self._ensure_edgejev_model_dir()
        logger.info(f"Loading EdgeJev ONNX model from {model_dir} ...")
        self._set_progress("loading", 70.0, f"加载 EdgeJev ONNX 模型：{model_dir}", target_id)
        return {"kind": "edgejev", "agent": Agent(model_dir)}

    # ----------------------------------------------------------------- unload
    def unload_model(self, model_id: Optional[str] = None) -> None:
        """Frees weights. With `model_id`, unloads just that cached model; otherwise unloads everything."""
        if model_id:
            self._drop_model(model_id)
            if model_id == self.model_id:
                self.load_error = None
                self.mode = "unloaded"
            return
        for mid in list(self.loaded_models):
            self._drop_model(mid)
        self.model = None
        self.is_loaded = False
        self.load_error = None
        self.mode = "unloaded"
        self._release_device_cache()

    async def unload_cached_model(self, model_id: str) -> dict[str, Any]:
        """Unloads one cached model (any model, not just the active one)."""
        async with self._load_lock:
            self.unload_model(model_id)
        return self.get_status()

    def get_status(self) -> dict[str, Any]:
        memory_mb = 0.0
        if torch.cuda.is_available():
            memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)

        meta = self.get_model_meta(self.model_id)
        return {
            "model_id": self.model_id,
            "name": meta["name"],
            "architecture": meta["architecture"],
            "mode": self.mode,
            "is_loaded": self.is_loaded,
            "is_loading": self.is_loading,
            "device": self.device,
            "memory_mb": round(memory_mb, 2),
            "load_error": self.load_error,
            "cache_enabled": self.cache_enabled,
            "loaded_models": list(self.loaded_models.keys()),
            "progress": self.get_progress(),
            "supports_modalities": ["text", "structured_json", "audio_tokens", "vision_tokens"],
            "decision_primitives": ["choice", "noul", "score"],
            "available_models": self.get_available_models(),
        }

    def _ensure_ready(self, target_model_id: str) -> None:
        """Raises ModelNotReadyError when the target model cannot serve inference."""
        meta = self.get_model_meta(target_model_id)

        if target_model_id != self.model_id:
            raise ModelNotReadyError(
                f"模型 {meta['name']} 并非当前活跃模型，请先在模型管理中切换后再进行推理。"
            )
        if self.is_loading:
            raise ModelNotReadyError(f"模型 {meta['name']} 正在载入中，请稍后重试。")
        if self.load_error:
            raise ModelNotReadyError(f"模型 {meta['name']} 载入失败：{self.load_error}")
        if not self.is_loaded or self.model is None:
            raise ModelNotReadyError(
                f"模型 {meta['name']} 尚未载入，请先在模型管理中加载权重后再进行推理。"
            )

    async def predict(
        self,
        input_text: str,
        questions: dict[str, QuestionDefinition],
        model_id: Optional[str] = None,
        image: Optional[str] = None,
    ) -> tuple[dict[str, Any], float, str]:
        """
        Executes decision inference using the loaded model weights.
        Raises ModelNotReadyError if the active model is not loaded or failed to load.
        Returns:
            (answers_dict, latency_ms, engine_name)
        """
        target_model_id = model_id if model_id in [m["id"] for m in SUPPORTED_MODELS] else self.model_id
        meta = self.get_model_meta(target_model_id)

        self._ensure_ready(target_model_id)

        start_time = time.perf_counter()
        loop = asyncio.get_running_loop()

        q_payload = {}
        for k, q in questions.items():
            if q.type == "choice":
                crit = q.criteria if isinstance(q.criteria, dict) else {}
                q_payload[k] = {
                    "type": "choice",
                    "instructions": q.instructions,
                    "criteria": crit,
                }
            elif q.type == "noul":
                crit = None
                if isinstance(q.criteria, dict):
                    crit = q.criteria
                q_payload[k] = {
                    "type": "noul",
                    "instructions": q.instructions,
                    "criteria": crit,
                }
            elif q.type == "score":
                scale = q.scale or 5
                if isinstance(q.criteria, (list, tuple)) and 2 <= len(q.criteria) <= 10:
                    crit = list(q.criteria)
                else:
                    if any(w in q.instructions for w in ["危害", "危险", "harm", "risk", "紧急", "优先"]):
                        crit = [
                            "1级：温顺无害家庭伴侣/极低危险",
                            "2级：较小危害/低度自卫防范",
                            "3级：中度危害/警惕性高",
                            "4级：较高攻击性威胁/严重危害",
                            "5级：极度凶猛致命危险"
                        ][:scale]
                    else:
                        crit = [f"等级 {i+1}（满分 {scale}）" for i in range(scale)]
                q_payload[k] = {
                    "type": "score",
                    "instructions": q.instructions,
                    "criteria": crit,
                }

        backend = self._active_backend()
        handle = self.model
        try:
            raw_answers = await loop.run_in_executor(
                None, self._infer_raw, backend, handle, input_text, q_payload, image
            )
        except ModelNotReadyError:
            raise
        except Exception as e:
            logger.error(f"Error during model inference: {e}", exc_info=True)
            raise ModelNotReadyError(f"模型 {meta['name']} 推理执行失败：{e}") from e

        answers = {}
        for k, q in questions.items():
            ans = raw_answers.get(k, {})
            if q.type == "choice":
                answers[k] = {
                    "choice": ans.get("choice", ""),
                    "probabilities": ans.get("probabilities", {}),
                    "confidence": round(float(ans.get("confidence", 0.0)), 4),
                }
            elif q.type == "noul":
                p_true = float(ans.get("noul", ans.get("probability", 0.5)))
                answers[k] = {
                    "decision": p_true >= 0.5,
                    "probability": round(p_true, 4),
                }
            elif q.type == "score":
                scale = q.scale or 5
                raw_score = float(ans.get("score", 0.0))
                score_int = max(1, min(scale, int(round(raw_score + 1.0))))
                answers[k] = {
                    "score": score_int,
                    "scale": scale,
                    "confidence": round(float(ans.get("confidence", 0.85)), 2),
                }

        latency_ms = (time.perf_counter() - start_time) * 1000
        engine_title = f"{meta['name']} (Native Vision)" if image else f"{meta['name']} (Native Engine)"
        return answers, round(latency_ms, 2), engine_title

    def _infer_raw(
        self,
        backend: str,
        handle: Any,
        input_text: str,
        q_payload: dict[str, Any],
        image: Optional[str],
    ) -> dict[str, Any]:
        """Dispatches a single inference to the loaded backend, returning a `{question: answer}` dict."""
        if handle is None:
            raise ModelNotReadyError("模型尚未载入，无法推理。")

        if backend == "liquid":
            pil_image = parse_image_to_pil(image) if image else None
            with torch.no_grad():
                state_val = input_text.strip() if input_text and input_text.strip() else None
                images_arg = [pil_image] if pil_image is not None else None
                result = handle.system_one(state_val, q_payload, images=images_arg)
            return result.get("answers", result) if isinstance(result, dict) else {}

        if backend == "minicpm":
            return self._infer_minicpm(handle, input_text, q_payload)

        if backend == "edgejev":
            result = handle["agent"].system_one(input_text, q_payload)
            return result.get("answers", result) if isinstance(result, dict) else {}

        raise ModelNotReadyError(f"未知的模型后端: {backend}")

    def _infer_minicpm(self, handle: dict[str, Any], input_text: str, q_payload: dict[str, Any]) -> dict[str, Any]:
        module = handle["module"]
        model = handle["model"]

        record = {"state": input_text or "", "questions": q_payload}
        internal = module.to_internal_record(record, add_date_facts=True)
        results = model.predict_record(internal, use_pride=False)

        answers: dict[str, Any] = {}
        for q_internal, (_logits, probs) in zip(internal["questions"], results):
            keys = q_internal["keys"]
            probs_list = probs.tolist() if hasattr(probs, "tolist") else list(probs)
            total = float(sum(probs_list)) or 1.0
            probs_list = [float(v) / total for v in probs_list]
            q_type = q_internal["type"]

            if q_type == "choice":
                best = max(range(len(probs_list)), key=probs_list.__getitem__)
                answers[q_internal["name"]] = {
                    "choice": keys[best],
                    "probabilities": {k: round(v, 4) for k, v in zip(keys, probs_list)},
                    "confidence": round(probs_list[best], 4),
                }
            elif q_type == "noul":
                answers[q_internal["name"]] = {
                    "noul": round(probs_list[1], 4),
                    "confidence": round(max(probs_list), 4),
                }
            elif q_type == "score":
                expected = sum(i * v for i, v in enumerate(probs_list))
                answers[q_internal["name"]] = {
                    "score": round(expected, 4),
                    "confidence": round(max(probs_list), 4),
                }
        return answers


model_engine = DecisionModelEngine()
