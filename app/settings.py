from dotenv import load_dotenv
import os

load_dotenv()

EMOTION_MODEL_PATH = os.getenv("EMOTION_MODEL_PATH", "ml-model/emotion_model.onnx")

def envs(*variaveis, default=None):
    if len(variaveis) == 1:
        str_default = str(default) if default is not None else None
        return os.getenv(variaveis[0], str_default)
    else:
        return {var: os.getenv(var) for var in variaveis}

def bool_env(var_name: str, default: str = "false") -> bool:
    value = os.getenv(var_name, default)
    return value.strip().lower() in ("true", "1", "t", "yes", "y")
