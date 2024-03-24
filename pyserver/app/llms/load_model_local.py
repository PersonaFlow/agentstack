import logging
from torch import cuda
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def load_model_local(callback_manager, streaming: bool = False):
    device_type = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
    model_path = "./models/llama-2-7b-chat.ggmlv3.q4_K_M.bin"
    logging.info(f"Loading Model: {model_path}, on: {device_type}")
    logging.info("Using Llamacpp for GGML quantized models")
    max_ctx_size = 4096
    # f16_kv = True
    verbose=True
    kwargs = {
        "model_path": model_path,
        "n_ctx": max_ctx_size,
        "max_tokens": max_ctx_size,
        # "f16_kv": f16_kv,
        "verbose": verbose,
    }
    if device_type.lower() == "mps":
        kwargs["n_gpu_layers"] = 1000
    if device_type.lower() == "cuda":
        kwargs["n_gpu_layers"] = 1000
        kwargs["n_batch"] = max_ctx_size
    if streaming:
        return LlamaCpp(**kwargs, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])) 
    else:
        return LlamaCpp(**kwargs, callback_manager=callback_manager)   