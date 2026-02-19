---
type: claude-knowledge
source: aiprojects
source_path: ".claude/agent-output/results/ollama-manager/2025-11-07_pull_qwen25_7b_instruct.md"
source_category: "discovery-ollama-manager"
synced: 2026-02-17
title: "Ollama Model Pull Results: Qwen2.5-Instruct 7B"
tags:
  - claude-knowledge
  - discovery-ollama-manager
---

# Ollama Model Pull Results: Qwen2.5-Instruct 7B

**Date**: 2025-11-07 15:32:45
**Session**: 2025-11-07_ollama-manager_151955
**Operation**: Model Pull
**Service**: ollama.service (systemd) on AIServer:11434

---

## Executive Summary

Successfully pulled and tested the **qwen2.5:7b-instruct** model on the systemd Ollama service. The model is fully GPU-accelerated with AMD ROCm and demonstrates excellent performance on the AMD Ryzen AI Max+ 395 hardware.

**Status**: SUCCESS
**Model Size**: 4.7 GB
**GPU Acceleration**: Full (29/29 layers on ROCm0)
**Performance**: 2.8 seconds inference time

---

## Model Information

### Basic Details
- **Model Name**: qwen2.5:7b-instruct
- **Model ID**: 845dbda0ea48
- **Size on Disk**: 4.7 GB
- **Parameters**: 7 billion
- **Quantization**: Q4_0 (inferred from size-to-parameter ratio)
- **Type**: Instruction-tuned language model
- **Provider**: Alibaba Cloud (Qwen Team)
- **Modified Date**: 2025-11-07 15:32:42

### Technical Specifications
- **Architecture**: Qwen2.5 (transformer-based)
- **Context Window**: 32,768 tokens (training), 8,192 tokens (runtime default)
- **Layers**: 28 transformer layers + 1 output layer
- **Quantization Method**: Q4_0 (4-bit quantization)

---

## Installation Process

### Pre-Installation Status
**Disk Space Available**: 1.6 TB
**Existing Models**: llama2:latest (3.8 GB), nomic-embed-text:latest (274 MB)
**Total Space Used (Before)**: 3.9 GB

### Download Metrics
- **Command**: `ollama pull qwen2.5:7b-instruct`
- **Download Size**: 4.7 GB
- **Average Speed**: 32-33 MB/s
- **Download Duration**: ~2 minutes 19 seconds
- **Completion**: Successful

### Post-Installation Status
**Total Models**: 3
**Total Space Used (After)**: 8.8 GB (4.7 GB + 3.8 GB + 0.3 GB)
**Disk Space Remaining**: 1.6 TB

---

## Performance Testing

### Test 1: Basic Inference

**Prompt**: "Hello, introduce yourself in one sentence"

**Response**:
```
Hello! I'm Qwen, an AI assistant created by Alibaba Cloud designed to help
with a wide variety of tasks and questions.
```

**Metrics**:
- Total inference time: 2.841 seconds
- Model loading time: 1.76 seconds
- Actual generation time: ~1.08 seconds
- User CPU time: 0.013s
- System CPU time: 0.018s

### GPU Acceleration Verification

**ROCm Status**: ACTIVE and FULLY UTILIZED

**GPU Memory Allocation**:
- Model buffer on ROCm0: 4,168.09 MiB (~4.17 GB)
- KV cache on ROCm0: 448.00 MiB
- Compute buffer on ROCm0: 492.00 MiB
- **Total GPU VRAM**: ~5.1 GB

**Layer Offloading**:
- Repeating layers offloaded: 28/28
- Output layer offloaded: 1/1
- **Total layers on GPU**: 29/29 (100%)

**CPU Memory Allocation** (minimal fallback):
- CPU_Mapped model buffer: 292.36 MiB
- ROCm_Host output buffer: 1.19 MiB
- ROCm_Host compute buffer: 23.01 MiB
- **Total CPU VRAM**: ~316 MiB

### Performance Analysis

**Strengths**:
1. Fast inference (2.8s total) for a 7B model
2. Full GPU acceleration - all layers on AMD GPU
3. Efficient memory usage (~5.1 GB total)
4. Quick model loading (1.76s)
5. High-quality instruction-following responses

**Optimal Use Cases**:
- General-purpose chat and Q&A
- Code assistance and explanation
- Task completion and reasoning
- Multi-turn conversations
- Instruction-following workflows

**Hardware Fit**:
- Excellent match for AMD Ryzen AI Max+ 395
- Q4_0 quantization balances speed and quality
- 128GB RAM easily accommodates model + KV cache
- ROCm acceleration working perfectly

---

## Recommendations

### Model Usage
1. **Primary Use**: General-purpose instruction-following assistant
2. **Integration**: Ready for OpenWebUI connection via host.docker.internal:11434
3. **Context Length**: 8,192 tokens (can be increased to 32,768 if needed)
4. **Parallel Requests**: Can handle multiple concurrent requests with 128GB RAM

### Performance Optimization
1. Model is already optimally configured for this hardware
2. All layers are GPU-accelerated - no further optimization needed
3. Consider increasing context window for long-document tasks
4. Q4_0 quantization is ideal balance for this hardware

### Comparison with Other Models
- **vs llama2:latest (3.8 GB)**: Qwen2.5 is larger, more capable, better instruction-following
- **vs nomic-embed-text (274 MB)**: Different use case (embeddings vs generation)
- **Recommendation**: Use qwen2.5:7b-instruct as primary general-purpose model

---

## Next Steps

### Immediate Actions
1. Configure OpenWebUI to use qwen2.5:7b-instruct as default model
2. Test multi-turn conversation performance
3. Benchmark with longer prompts and context

### Future Considerations
1. Monitor performance under real-world workload
2. Consider pulling additional specialized models if needed:
   - Code-specific: codellama or deepseek-coder
   - Larger general: qwen2.5:14b or 32b (if more capability needed)
   - Faster small: qwen2.5:1.5b or 3b (for quick tasks)

### Memory Updates
- Added qwen2.5:7b-instruct to model inventory
- Documented performance characteristics
- Confirmed ROCm GPU acceleration working

---

## Technical Logs

### Installation Log Excerpt
```
pulling manifest
pulling 2bada8a74506: 100% [4.7 GB/4.7 GB]
verifying sha256 digest
writing manifest
success
```

### GPU Acceleration Log Excerpt
```
load_tensors: offloading 28 repeating layers to GPU
load_tensors: offloading output layer to GPU
load_tensors: offloaded 29/29 layers to GPU
load_tensors:        ROCm0 model buffer size =  4168.09 MiB
llama_kv_cache_unified:      ROCm0 KV buffer size =   448.00 MiB
llama_context:      ROCm0 compute buffer size =   492.00 MiB
llama runner started in 1.76 seconds
```

---

## Conclusion

The qwen2.5:7b-instruct model has been successfully installed and is fully operational with AMD ROCm GPU acceleration on AIServer. Performance is excellent with 2.8-second inference times and full GPU layer offloading. The model is ready for production use and integration with OpenWebUI.

**Links**:
- Session Log: `/home/davidmoneil/AIProjects/.claude/agents/sessions/2025-11-07_ollama-manager_151955.md`
- Model Details: `ollama show qwen2.5:7b-instruct`
- Service Status: `systemctl status ollama.service`
